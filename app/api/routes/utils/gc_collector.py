#  Copyright 2024 ExxonMobil Technology and Engineering Company
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import asyncio
import functools
import gc

from loguru import logger

from app.core.config import get_app_settings


def with_gc_collect(func):
    """Decorator to trigger garbage collection before and after an async
    function execution."""

    async def gc_wrapper(*args, **kwargs):
        logger.debug("Calling GC Collector...")
        gc.collect()  # Run GC before execution
        await asyncio.sleep(0)  # Yield control back to event loop
        func_result = await func(*args, **kwargs)
        await asyncio.sleep(0)  # Yield control again before collecting GC
        gc.collect()  # Run GC after execution
        return func_result

    async def no_op_wrapper(*args, **kwargs):
        logger.debug("Not calling GC Collector...")
        return await func(*args, **kwargs)

    # Select wrapper based on enable_gc_collect setting
    wrapper = gc_wrapper if get_app_settings().enable_gc_collect else no_op_wrapper

    return functools.wraps(func)(wrapper)
