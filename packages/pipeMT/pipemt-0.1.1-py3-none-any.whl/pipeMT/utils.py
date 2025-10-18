import threading
import traceback
import os
import weakref
import torch
import torch.nn as nn

def get_model_size(model: nn.Module):
    param_size = sum(p.numel() * p.element_size() for p in model.parameters())
    buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
    return param_size + buffer_size

def thread_exception_handler(args):
    print(f"Unhandled exception in thread {args.thread.name}:")
    traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback)
    os._exit(1)
threading.excepthook = thread_exception_handler

def pin_tensor(tensor: torch.Tensor) -> None:
    if tensor.device.type != 'cpu' or tensor.is_pinned():
        return
    cudart = torch.cuda.cudart()
    storage = tensor.data.untyped_storage()
    assert int(cudart.cudaHostRegister(storage.data_ptr(), storage.nbytes(), 1)) == 0
    weakref.finalize(storage, lambda ptr: cudart.cudaHostUnregister(ptr), storage.data_ptr())
