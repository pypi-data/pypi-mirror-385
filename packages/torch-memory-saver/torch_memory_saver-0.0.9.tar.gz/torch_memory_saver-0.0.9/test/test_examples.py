import pytest
from contextlib import nullcontext

import multiprocessing
import traceback
import torch_memory_saver
from torch_memory_saver.utils import change_env

from examples import simple, cuda_graph, cpu_backup, rl_example, multi_device, training_engine

_HOOK_MODES = ["preload", "torch"]


@pytest.mark.parametrize("hook_mode", _HOOK_MODES)
def test_simple(hook_mode):
    _test_core(simple.run, hook_mode=hook_mode)


@pytest.mark.parametrize("hook_mode", _HOOK_MODES)
def test_cuda_graph(hook_mode):
    _test_core(cuda_graph.run, hook_mode=hook_mode)


@pytest.mark.parametrize("hook_mode", _HOOK_MODES)
def test_cpu_backup(hook_mode):
    _test_core(cpu_backup.run, hook_mode=hook_mode)


@pytest.mark.parametrize("hook_mode", _HOOK_MODES)
def test_multi_device(hook_mode):
    _test_core(multi_device.run, hook_mode=hook_mode)


@pytest.mark.parametrize("hook_mode", _HOOK_MODES)
def test_rl_example(hook_mode):
    _test_core(rl_example.run, hook_mode=hook_mode)


def test_training_engine():
    with (
        change_env("TMS_INIT_ENABLE", "1"),
        change_env("TMS_INIT_ENABLE_CPU_BACKUP", "1")
    ):
        _test_core(training_engine.run, hook_mode="preload")


def _test_core(fn, hook_mode):
    ctx = torch_memory_saver.configure_subprocess() if hook_mode == "preload" else nullcontext()
    with ctx:
        _run_in_subprocess(fn, fn_kwargs=dict(hook_mode=hook_mode))


def _run_in_subprocess(fn, fn_kwargs):
    ctx = multiprocessing.get_context('spawn')
    output_queue = ctx.Queue()
    proc = ctx.Process(target=_subprocess_fn_wrapper, args=(fn, fn_kwargs, output_queue))
    proc.start()
    proc.join()
    success = output_queue.get()
    assert success


def _subprocess_fn_wrapper(fn, fn_kwargs, output_queue):
    try:
        print(f"Subprocess execution start")
        fn(**fn_kwargs)
        print(f"Subprocess execution end (may see error messages when CUDA exit which is normal)", flush=True)
        output_queue.put(True)
    except Exception as e:
        print(f"Subprocess has error: {e}", flush=True)
        traceback.print_exc()
        output_queue.put(False)
        raise
