#  Copyright 2023 ExxonMobil Technology and Engineering Company
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

import logging
from types import FrameType
from typing import Union, cast

from loguru import logger


class InterceptHandler(logging.Handler):

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        """Log the specified logging record.

        :param record: logging record
        :type record: logging.LogRecord
        """
        level = self._get_level(record)
        self._find_caller(level, record)

    @staticmethod
    def _get_level(record: logging.LogRecord) -> Union[int, str]:
        """Get corresponding Loguru level if it exists.

        :param record: logging record
        :type record: logging.LogRecord
        :return: level
        :rtype: Union[int, str]
        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)
        return level

    @staticmethod
    def _find_caller(level: Union[int, str], record: logging.LogRecord) -> None:
        """Find caller from where originated the logged message.

        :param level: loguru level
        :type level: Union[int, str]
        :param record: logging record
        :type record: logging.LogRecord
        """
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )
