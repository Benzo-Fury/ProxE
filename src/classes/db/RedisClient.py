import redis
import json
from typing import Any, cast

class RedisClient:
    """
    A wrapper around the Redis client for simplified data storage and retrieval.
    Supports storing strings, dictionaries, and lists with optional expiration.

    NOTE: Some methods cast the return type. This is because redis will decode the responses itself.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """
        Initializes the Redis connection.

        Args:
            host (str): Redis server hostname or IP. Defaults to "localhost".
            port (int): Redis server port. Defaults to 6379.
            db (int): Redis database number. Defaults to 0.
        """
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def set(self, key: str, value: Any, expire: int | None = None) -> bool:
        """
        Stores a value in Redis under the given key.

        Args:
            key (str): Redis key to set.
            value (Any): Value to store. Dicts/lists are automatically converted to JSON.
            expire (int, optional): Expiration time in seconds. Defaults to None (no expiration).

        Returns:
            bool: True if the operation was successful.
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return cast(bool, self.client.set(key, value, ex=expire))

    def get(self, key: str) -> Any:
        """
        Retrieves a value from Redis by key.

        Returns:
            Any: Parsed JSON if the value is JSON-formatted, raw value otherwise.
        """
        value = self.client.get(key)

        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        else:
            return value

    def delete(self, key: str) -> int:
        """
        Deletes a key from Redis. 

        Returns:
            int: The number of keys deleted (0 or 1).
        """
        return cast(int, self.client.delete(key))

    def exists(self, key: str) -> bool:
        """
        Checks if a given key exists in Redis.

        Args:
            key (str): The Redis key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return self.client.exists(key) == 1

    def keys(self, pattern: str = "*") -> list[str]:
        """
        Returns a list of keys matching a pattern.

        Args:
            pattern (str): Redis key pattern to match (default is '*').

        Returns:
            list[str]: A list of matching keys.
        """
        return cast(list[str], self.client.keys(pattern))

    def flush(self) -> None:
        """
        Deletes all keys from the current Redis database.

        WARNING: This is destructive and cannot be undone.
        """
        self.client.flushdb()
