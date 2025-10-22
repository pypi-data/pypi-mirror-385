from typing import Union
import sqlite3

from ..utils.utils import slugify
from .base import BaseCache


class SQLiteCache(BaseCache):

    connector = None

    def __init__(self, connector, region_tag: str, chunk_size: int=1024**3) -> None:
        super().__init__(region_tag, chunk_size)
        self.connector = connector
        self.connector.row_factory = sqlite3.Row

    def __del__(self) -> None:
        self.connector.close()

    def check(self, category_tag: str, *args, **kwargs) -> bool:
        """ Checks if the cache is avaiable for the given arguments

        Args:
            category_tag (str): the category tag
            *args: list of arguments for the API endpoint
            **kwargs: dict of keyword arguments for the API endpoint

        Returns:
            bool: True if the cache is available and valid for the given arguments else False
        """
        hash_value = self.compute_hash(*args, **kwargs)
        try:
            res = self.connector.execute("""SELECT COUNT(*) FROM cache, categories
                                            WHERE cache.hash = ? AND cache.next_update > unixepoch('now') AND
                                                categories.name = ? AND cache.categoryId = categories.ROWID;""",
                                         (hash_value, slugify(category_tag))).fetchone()
        except TypeError:
            return False
        else:
            return res[0] > 0

    def select(self, category_tag: str, *args, **kwargs) -> Union[None, bytes]:
        """ Retrieves the data from the cache

        Args:
            category_tag (str): category name
            *args: list of arguments for the API endpoint
            **kwargs: dict of keyword arguments for the API endpoint

        Returns:
            bytes: the data from the cache if available and valid
            None: upon failure or no valid data
        """
        hash_value = self.compute_hash(*args, **kwargs)
        try:
            results = self.connector.execute("""SELECT chunks.data FROM cache, categories, chunks
                                                WHERE cache.hash = ? AND chunks.cacheId = cache.ROWID AND
                                                    categories.name = ? AND cache.categoryId = categories.ROWID
                                                ORDER BY sequence;""", (hash_value, slugify(category_tag))).fetchall()
        except TypeError:
            return None
        else:
            if len(results) == 0:
                return None

            return b''.join([row[0] for row in results])

    def insert(self, category_tag: str, data: bytes, *args, **kwargs) -> bool:
        """ Inserts the data into the cache
        Args:
            category_tag (str): the category tag
            data (bytes): the data to insert
            *args: list of arguments for the API endpoint
            **kwargs: dict of keyword arguments for the API endpoint

        Returns:
            bool: True if the insertion was successful else False
        """
        hash_value = self.compute_hash(*args, **kwargs)


        try:
            results = self.connector.execute("""INSERT INTO cache (hash, categoryId, next_update) 
                                             SELECT :hash, categories.ROWID, unixepoch(strftime('%Y-%m-%d 10:00:00', 'now', 'weekday 2')) + categories.duration
                                             FROM categories
                                             WHERE categories.name = :name""",
                                             {"hash": hash_value, "name": slugify(category_tag)})
        except sqlite3.Error:
            return False
        else:
            self.connector.commit()
            last_id = results.lastrowid

        chunks = [{"cacheId": last_id, "sequence": counter, "data": chunk} for counter, chunk in enumerate(self.chunk_data(data), start=1)]

        try:
            results = self.connector.executemany("""INSERT INTO chunks (cacheId, sequence, data)
                                                 VALUES (:cacheId, :sequence, :data);""", chunks)
        except sqlite3.Error:
            return False
        else:
            self.connector.commit()
            return results.rowcount > 0


    def update(self, category_tag: str, data: bytes, *args, **kwargs) -> bool:
        """ Insert or update the data in the cache

        Args:
            category_tag (str): category name
            data (bytes): data to insert
            *args: list of arguments for the API endpoint
            **kwargs: dict of keyword arguments for the API endpoint

        Returns:
            bool: True if the data was inserted or not, False otherwise
        """
        hash_value = self.compute_hash(*args, **kwargs)

        counter = 0
        try:
            cache = self.connector.execute("""SELECT ROWID FROM cache WHERE hash = ?;""", (hash_value,)).fetchone()
        except sqlite3.Error:
            return False

        if not cache:
            return self.insert(category_tag, data, *args, **kwargs)

        chunks = [{'cacheId': cache["ROWID"], "sequence": counter, "data": chunk} for counter, chunk in enumerate(self.chunk_data(data), start=1)]

        try:
            results = self.connector.executemany("""INSERT INTO chunks (cacheId, sequence, data)
                                                    VALUES (:cacheId, :sequence, :data)
                                                    ON CONFLICT (cacheId, sequence) 
                                                        DO UPDATE SET cacheId=excluded.cacheId,
                                                                      sequence=excluded.sequence,
                                                                      data=excluded.data;""", chunks)
        except sqlite3.Error as e:
            print(f"Failed to insert chunk {counter}: {e}")
            return False
        else:
            self.connector.commit()
            return results.lastrowid > 0

    def delete(self, category_tag: str, *args, **kwargs) -> bool:
        """ Deletes the data from the cache

        Args:
            category_tag: category name
            *args: list of arguments for the API endpoint
            **kwargs: dict of keyword arguments for the API endpoint

        Returns:
            bool: True if the cache is deleted or false if it was not deleted or deleted completely
        """
        hashed_value = self.compute_hash(*args, **kwargs)
        cache_id = self.connector.execute("""SELECT FROM cache WHERE hash = ?;""", (hashed_value,)).fetchone()[0]

        try:
            chunk_results = self.connector.execute("""DELETE FROM chunks WHERE cacheId = ?;""", (cache_id,))
            cache_results = self.connector.execute("""DELETE FROM cache WHERE hash = ?;""", (hashed_value,))
        except TypeError:
            return False
        else:
            self.connector.commit()

        return chunk_results.rowcount and cache_results.rowcount
