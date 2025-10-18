from typing import *
import traceback

import torch.nn as nn
from torch.distributed.pipelining import pipeline

from pipeMT.async_handle import pipeMTAsyncHandle
from pipeMT.batch import Batch
from pipeMT.device import *
from pipeMT.scheduler import model_enqueue
from pipeMT.timer import ModelTimer
from pipeMT.utils import get_model_size, pin_tensor

if TYPE_CHECKING:
    import torch.fx as fx
    from torch.distributed.pipelining import SplitPoint

class pipeMT(nn.Module):
    def __init__(self,
                 model: Union[nn.Module, Iterable[nn.Module]],
                 num_microbatch: int = torch.cuda.device_count() + 1,
                 preserve_rng_state: bool = True):
        super().__init__()
        filename, lineno, _, _ = traceback.extract_stack()[-2]
        self.name = f'{filename.split("/")[-1]}:{lineno}'
        self.num_microbatch = num_microbatch
        self.preserve_rng_state = preserve_rng_state
        
        self.model_timer = ModelTimer()
        self.layer_workload: List[float] = []
        self.layer_has_param: List[bool] = []
        self.max_layer_workload: int = 0
        if isinstance(model, nn.Sequential):
            self.model: nn.Module = model
            self.layers = list(model)
            self.init_layer_info()
            self.model_workload = sum(self.layer_workload)
            self.require_spliting = False
        elif isinstance(model, nn.Module):
            self.model: nn.Module = model
            self.layers = [model]
            self.init_layer_info()
            self.model_workload = sum(self.layer_workload)
            self.require_spliting = False
        else:
            raise TypeError('input model should be torch.nn.Module or torch.nn.Sequential')
        self.preprocess_param()

    def __getattr__(self, name: str):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return getattr(self.model, name)

    def preprocess_param(self):
        for parm in self.model.parameters():
            pin_tensor(parm.data)
            parm.data_cpu = parm.data
        for buffer in self.model.buffers():
            pin_tensor(buffer.data)
            buffer.data_cpu = buffer.data

    def init_layer_info(self):
        self.num_layers = len(self.layers)
        self.model_timer.init(self.num_layers)
        for layer in self.layers:
            self.layer_has_param.append(any(True for _ in layer.parameters()))
            self.layer_workload.append(get_model_size(layer))
        self.max_layer_workload = max(self.layer_workload)
    
    def split_model(self,
                    mb_args: Tuple[Any, ...] = tuple(),
                    mb_kwargs: Optional[Dict[str, Any]] = None,
                    split_spec: Optional[Dict[str, 'SplitPoint']] = None,
                    split_policy: Optional[Callable[['fx.GraphModule'], 'fx.GraphModule']] = None):
        # This function is thread un-safe, be aware of pytorch export racing
        self.require_spliting = False
        split_spec = self.split_spec if split_spec is None else split_spec
        split_policy = self.split_policy if split_policy is None else split_policy
        pipe = pipeline(self.model, mb_args, mb_kwargs, split_spec, split_policy)
        self.layers = []
        for i in range(pipe.num_stages):
            self.layers.append(pipe.get_stage_module(i))
        self.init_layer_info()

    def update_workload(self):
        if self.model_timer.update_workload(self.layer_workload):
            self.model_workload = sum(self.layer_workload)
            self.max_layer_workload = max(self.layer_workload)

    def forward(self, *args,
                is_async: bool = False, require_grad: bool = torch.is_grad_enabled(),
                output_device: torch.device = torch.device('cpu'),
                **kwargs):
        self.update_workload()
        if 'num_microbatch' not in kwargs:
            kwargs['num_microbatch'] = self.num_microbatch
        input = Batch(*args, **kwargs)
        result_handle = pipeMTAsyncHandle(self, input, require_grad, output_device)
        model_enqueue(result_handle)
        return result_handle if is_async else result_handle.get_result()

    def forward_backward(self, *args, **kwargs):
        assert torch.is_grad_enabled(), "You can't perform backward without gradient!"
        self.update_workload()
        if 'num_microbatch' not in kwargs:
            kwargs['num_microbatch'] = self.num_microbatch
        input = Batch(*args, **kwargs)
        handle = pipeMTAsyncHandle(self, input, True, torch.device('cpu'), True)
        model_enqueue(handle)
        return handle.backward()
