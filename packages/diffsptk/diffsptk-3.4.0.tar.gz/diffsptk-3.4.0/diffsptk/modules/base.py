# ------------------------------------------------------------------------ #
# Copyright 2022 SPTK Working Group                                        #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License");          #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
# ------------------------------------------------------------------------ #

from abc import ABC, abstractmethod

import torch
from torch import nn

from ..typing import Precomputed


class BaseNonFunctionalModule(ABC, nn.Module):
    pass


class BaseFunctionalModule(ABC, nn.Module):
    @staticmethod
    @abstractmethod
    def _func(*args, **kwargs) -> torch.Tensor:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _takes_input_size() -> bool:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _check(*args, **kwargs) -> None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _precompute(*args, **kwargs) -> Precomputed:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _forward(*args, **kwargs) -> torch.Tensor:
        raise NotImplementedError


class BaseLearnerModule(ABC, nn.Module):
    @abstractmethod
    def transform(self, *args, **kwargs) -> torch.Tensor:
        raise NotImplementedError
