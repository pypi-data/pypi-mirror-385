from __future__ import annotations

import importlib.util
import socket
from typing import Any, Callable, Literal

from bodo.mpi4py import MPI

PROCESS_GROUP_INIT_RETRIES = 5


def torch_import_guard():
    try:
        importlib.util.find_spec("torch")
    except ImportError:
        raise ImportError(
            "PyTorch is not installed. Please install it to use TorchTrainer."
        )


def _get_open_port():
    """
    Finds and returns an available open TCP port.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("", 0))  # Bind to an ephemeral port (port 0)
        port = s.getsockname()[1]  # Get the assigned port number
        return port
    finally:
        s.close()


def _init_process_group():
    import torch
    import torch.distributed as dist

    from bodo import get_gpu_ranks, get_num_nodes

    if dist.is_initialized():
        dist.destroy_process_group()
    if hasattr(torch, "accelerator"):
        device = torch.accelerator.current_accelerator(check_available=True)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pytorch_rank = MPI.COMM_WORLD.Get_rank()

    gpu_ranks = get_gpu_ranks()
    if device is None or device == torch.device("cpu"):
        device = torch.device("cpu")
    else:
        # Assign each rank to an accelerator
        mpi_rank = MPI.COMM_WORLD.Get_rank()
        num_local_gpus = len(gpu_ranks) // get_num_nodes()
        if mpi_rank in gpu_ranks:
            pytorch_rank = gpu_ranks.index(mpi_rank)
            if hasattr(torch, "accelerator"):
                torch.accelerator.set_device_index(pytorch_rank % num_local_gpus)
                device = torch.accelerator.current_accelerator()
            else:
                torch.cuda.set_device(pytorch_rank % num_local_gpus)
                device = torch.device(f"cuda:{pytorch_rank % num_local_gpus}")
        else:
            pytorch_rank = None
    npes = (
        len(gpu_ranks) if device != torch.device("cpu") else MPI.COMM_WORLD.Get_size()
    )

    backend = torch.distributed.get_default_backend_for_device(device)
    # Incase something binds to the port between getting the port and initializing
    # the process group, we retry a few times.
    for i in range(PROCESS_GROUP_INIT_RETRIES):
        try:
            tcp_conn_str = None
            if pytorch_rank == 0:
                port = _get_open_port()
                tcp_conn_str = f"tcp://{socket.gethostname()}:{port}"
            tcp_conn_str = MPI.COMM_WORLD.bcast(tcp_conn_str, root=0)

            if pytorch_rank is not None:
                dist.init_process_group(
                    backend=backend,
                    init_method=tcp_conn_str,
                    rank=pytorch_rank,
                    world_size=npes,
                )
            return pytorch_rank, npes, device
        except Exception as e:
            if i == PROCESS_GROUP_INIT_RETRIES - 1:
                raise e


def torch_train(
    train_loop_per_worker: Callable[[], None] | Callable[[dict], None],
    *args,
    **kwargs,
):
    # We need the compiler on the spawner since the workers will import it
    # for get_gpu_ranks, if the workers have it and not the spawner it can
    # cause a hang in gather/scatter operations since they will have
    # different implementations.
    import bodo.decorators  # noqa: F401
    from bodo.pandas.lazy_wrapper import BodoLazyWrapper
    from bodo.spawn.spawner import submit_func_to_workers

    def worker_func(args, kwargs):
        torch_import_guard()
        import torch.distributed as dist

        train_loop_per_worker(*args, **kwargs)
        if dist.is_initialized():
            dist.destroy_process_group()

    for arg in args:
        if isinstance(arg, BodoLazyWrapper):
            arg.execute_plan()
    for _, kwarg in kwargs.items():
        if isinstance(kwarg, BodoLazyWrapper):
            kwarg.execute_plan()
    submit_func_to_workers(worker_func, [], args, kwargs)


def prepare_model(
    model,
    parallel_strategy: Literal["ddp", "fsdp"] | None = "ddp",
    parallel_strategy_kwargs: dict[str, Any] | None = None,
):
    torch_import_guard()
    import torch

    assert isinstance(model, torch.nn.Module), (
        "Model should be an instance of torch.nn.Module"
    )
    pytorch_rank, pytorch_world_size, device = _init_process_group()
    if pytorch_rank is None:
        return None

    model.to(device)
    # If we only have one rank, no need to wrap the model
    if pytorch_world_size == 1:
        return model
    if parallel_strategy is not None:
        assert parallel_strategy in ["ddp", "fsdp"], (
            "parallel_strategy should be either 'ddp' or 'fsdp'"
        )
        if parallel_strategy_kwargs is None:
            parallel_strategy_kwargs = {}
        if parallel_strategy == "ddp":
            from torch.nn.parallel import DistributedDataParallel as DDP

            model = DDP(model, **parallel_strategy_kwargs)
        elif parallel_strategy == "fsdp":
            from torch.distributed.fsdp import FullyShardedDataParallel as FSDP

            model = FSDP(model, **parallel_strategy_kwargs)
    return model
