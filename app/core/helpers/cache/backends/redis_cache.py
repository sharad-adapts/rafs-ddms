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

from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio.client import Redis
from redis.exceptions import AuthenticationError, ConnectionError, ResponseError

from app.core.helpers.cache.backends.base_cache import BaseCacheBackend
from app.core.helpers.cache.config import RedisCacheConfig
from app.core.helpers.cache.errors import CacheBackendError

settings = RedisCacheConfig()
redis_client = Redis(
    host=settings.redis_hostname,
    port=settings.redis_port,
    password=settings.redis_password,
    db=settings.redis_database,
    ssl=settings.redis_ssl,
)


class RedisCacheBackend(BaseCacheBackend):
    async def get_backend(self) -> RedisBackend:
        """Init and return instance of RedisBackend from fastapi-cache.

        :return RedisBackend: instance of RedisBackend
        """
        await self._validate_redis_settings(redis_client)
        return RedisBackend(redis_client)

    async def _validate_redis_settings(self, redis_client: Redis) -> None:
        """Validate redis settings.

        :param Redis redis_client: redis instance
        :raises:
          AuthenticationError: for wrong password
          ConnectionError: for wrong host or port
          ResponseError: for wrong db
        """
        try:
            await redis_client.ping()
        except (AuthenticationError, ConnectionError, ResponseError):
            raise CacheBackendError("Redis client can't be init. Redis host, port, password or db are wrong")
