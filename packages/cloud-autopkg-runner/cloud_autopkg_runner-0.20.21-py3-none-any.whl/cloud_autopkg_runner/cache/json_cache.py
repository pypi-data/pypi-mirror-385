"""Module for managing a metadata cache stored in a JSON file.

This module provides an asynchronous implementation of a metadata cache that
stores data in a JSON file. It uses a singleton pattern to ensure that only one
instance of the cache is created, and it provides methods for loading, saving,
getting, setting, and deleting cache items. The cache is thread-safe, using an
asyncio lock to prevent race conditions.
"""

import asyncio
import json
from pathlib import Path
from types import TracebackType

from cloud_autopkg_runner import Settings, logging_config
from cloud_autopkg_runner.metadata_cache import MetadataCache, RecipeCache, RecipeName


class AsyncJsonFileCache:
    """Asynchronous implementation of MetadataCachePlugin for JSON file storage.

    This class provides a singleton implementation for managing a metadata cache
    stored in a JSON file. It supports asynchronous loading, saving, getting,
    setting, and deleting cache items, ensuring thread safety through the use of
    an asyncio lock.

    Attributes:
        _file_path: The path to the JSON file used for storing the cache data.
        _cache_data: The in-memory representation of the cache data.
        _is_loaded: A flag indicating whether the cache data has been loaded from
            the JSON file.
        _lock: An asyncio lock used to ensure thread safety when accessing or
            modifying the cache data.
    """

    _instance: "AsyncJsonFileCache | None" = None  # Singleton instance
    _lock: asyncio.Lock = asyncio.Lock()  # Asynchronous lock for thread safety

    def __new__(cls) -> "AsyncJsonFileCache":
        """Singleton implementation.

        This method ensures that only one instance of the `AsyncJsonFileCache`
        class is created. If an instance already exists, it returns the existing
        instance; otherwise, it creates a new instance.

        Returns:
            The singleton instance of `AsyncJsonFileCache`.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the AsyncJsonFileCache instance."""
        if hasattr(self, "_initialized"):
            return  # Prevent re-initialization

        settings = Settings()
        self._logger = logging_config.get_logger(__name__)
        self._file_path: Path = Path(settings.cache_file)
        self._cache_data: MetadataCache = {}
        self._is_loaded: bool = False

        self._initialized: bool = True

    async def open(self) -> None:
        """Placeholder method for opening the cache.

        In this implementation, the `open` method is a placeholder and does not
        perform any actual operations. It is included to satisfy the
        `MetadataCachePlugin` interface.
        """

    async def load(self) -> MetadataCache:
        """Load metadata from the JSON file asynchronously.

        This method loads the metadata cache from the JSON file into memory. It uses
        an asyncio lock to ensure thread safety and prevents multiple coroutines from
        loading the cache simultaneously.

        If the JSON file does not exist or if the JSON file is corrupt, it logs a
        warning and returns an empty cache.

        Returns:
            The metadata cache loaded from the JSON file.
        """
        if self._is_loaded:
            return self._cache_data

        async with self._lock:
            # Could have loaded while waiting
            if self._is_loaded:
                return self._cache_data

            try:
                loop = asyncio.get_event_loop()
                content = await loop.run_in_executor(None, self._file_path.read_text)
                self._cache_data = json.loads(content)
                self._logger.info("Loaded metadata from %s", self._file_path)
            except FileNotFoundError:
                self._cache_data = {}
                self._logger.warning(
                    "Metadata file not found: %s, initializing an empty cache.",
                    self._file_path,
                )
            except json.JSONDecodeError:
                self._cache_data = {}
                self._logger.warning(
                    "Metadata file %s is corrupt, initializing an empty cache.",
                    self._file_path,
                )
            finally:
                self._is_loaded = True

        return self._cache_data

    async def save(self) -> None:
        """Write the metadata cache to disk.

        This method writes the entire metadata cache to the JSON file. It uses an
        asyncio lock to ensure thread safety and prevents multiple coroutines
        from writing to the file simultaneously.
        """
        async with self._lock:
            try:
                loop = asyncio.get_event_loop()
                content = json.dumps(self._cache_data, indent=4)
                await loop.run_in_executor(None, self._file_path.write_text, content)
                self._logger.debug("Saved all metadata to %s", self._file_path)
            except Exception:
                self._logger.exception("Error saving metadata to %s", self._file_path)

    async def close(self) -> None:
        """Placeholder method for closing the cache.

        In this implementation, the `close` method is a placeholder and does not
        perform any actual operations. It is included to satisfy the
        `MetadataCachePlugin` interface.
        """

    async def clear_cache(self) -> None:
        """Clear all data from the cache."""
        async with self._lock:
            self._cache_data = {}
            self._is_loaded = True

        await self.save()

    async def get_item(self, recipe_name: RecipeName) -> RecipeCache | None:
        """Retrieve a specific item from the cache asynchronously.

        Args:
            recipe_name: The name of the recipe to retrieve.

        Returns:
            The metadata associated with the recipe, or None if the recipe is not
            found in the cache.
        """
        await self.load()
        return self._cache_data.get(recipe_name)

    async def set_item(self, recipe_name: RecipeName, value: RecipeCache) -> None:
        """Set a specific item in the cache asynchronously.

        Args:
            recipe_name: The name of the recipe to set.
            value: The metadata to associate with the recipe.
        """
        await self.load()
        async with self._lock:
            self._cache_data[recipe_name] = value
            self._logger.debug(
                "Setting recipe %s to %s in the metadata cache.", recipe_name, value
            )

    async def delete_item(self, recipe_name: RecipeName) -> None:
        """Delete a specific item from the cache asynchronously.

        Args:
            recipe_name: The name of the recipe to delete from the cache.
        """
        await self.load()
        async with self._lock:
            if recipe_name in self._cache_data:
                del self._cache_data[recipe_name]
                self._logger.debug(
                    "Deleted recipe %s from metadata cache.", recipe_name
                )

    async def __aenter__(self) -> "AsyncJsonFileCache":
        """For use in `async with` statements.

        This method is called when entering an `async with` block. It loads the
        cache data from the JSON file and returns the `AsyncJsonFileCache`
        instance.
        """
        await self.load()
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        """For use in `async with` statements.

        This method is called when exiting an `async with` block. It saves the
        cache data to the JSON file and releases any resources held by the cache.

        Args:
            _exc_type: The type of exception that was raised, if any.
            _exc_val: The exception instance that was raised, if any.
            _exc_tb: The traceback associated with the exception, if any.
        """
        await self.close()
