# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from typing import Any

from llama_stack.apis.files import Files
from llama_stack.apis.inference import Inference
from llama_stack.apis.models import Models
from llama_stack.core.datatypes import AccessRule, Api
from llama_stack.providers.utils.kvstore import kvstore_impl

from .batches import ReferenceBatchesImpl
from .config import ReferenceBatchesImplConfig

__all__ = ["ReferenceBatchesImpl", "ReferenceBatchesImplConfig"]


async def get_provider_impl(config: ReferenceBatchesImplConfig, deps: dict[Api, Any], policy: list[AccessRule]):
    kvstore = await kvstore_impl(config.kvstore)
    inference_api: Inference | None = deps.get(Api.inference)
    files_api: Files | None = deps.get(Api.files)
    models_api: Models | None = deps.get(Api.models)

    if inference_api is None:
        raise ValueError("Inference API is required but not provided in dependencies")
    if files_api is None:
        raise ValueError("Files API is required but not provided in dependencies")
    if models_api is None:
        raise ValueError("Models API is required but not provided in dependencies")

    impl = ReferenceBatchesImpl(config, inference_api, files_api, models_api, kvstore)
    await impl.initialize()
    return impl
