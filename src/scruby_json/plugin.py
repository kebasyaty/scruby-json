# Scruby-Json - In search methods, returns result as json strings.
# Copyright (c) 2026 Gennady Kostyunin
# SPDX-License-Identifier: MIT
"""Scruby-Json Plugin."""

from __future__ import annotations

__all__ = ("ReturnJson",)


import warnings
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Event
from typing import Any, final

import orjson
from anyio import Path
from scruby import Scruby
from scruby_plugin import ScrubyPlugin


class ReturnJson(ScrubyPlugin):
    """Scruby-Json Plugin.

    In search methods, returns result as json strings.
    """

    def __init__(self, scruby_self: Scruby) -> None:  # noqa: D107
        ScrubyPlugin.__init__(self, scruby_self)

    @final
    @staticmethod
    async def _task_find(
        branch_number: int,
        filter_fn: Callable,
        hash_reduce_left: int,
        db_root: str,
        class_model: Any,
        stop_event: Event,
    ) -> list[Any] | None:
        """Task for find documents.

        This method is for internal use.

        Returns:
            List of documents as json strings or None.
        """
        # Suppress warning - RuntimeWarning: coroutine 'Find._task_find' was never awaited
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        # Variable initialization
        branch_number_as_hash: str = f"{branch_number:08x}"[hash_reduce_left:]
        separated_hash: str = "/".join(list(branch_number_as_hash))
        leaf_path = Path(
            *(
                db_root,
                class_model.__name__,
                separated_hash,
                "leaf.json",
            ),
        )
        docs: list[Any] = []
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict[str, str] = orjson.loads(data_json) or {}
            for _, val in data.items():
                if stop_event.is_set():
                    return None
                doc = class_model.model_validate_json(val)
                if filter_fn(doc):
                    docs.append(doc)
        return docs or None

    @final
    async def find_one(
        self,
        filter_fn: Callable,
    ) -> str | None:
        """Asynchronous method for find one document matching the filter.

        Attention:
            - The search is based on the effect of a quantum loop.
            - The search effectiveness depends on the number of processor threads.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.

        Returns:
            One document in json format or None.
        """
        # Get Scruby instance
        scruby_self = self.scruby_self()
        # Variable initialization
        search_task_fn: Callable = self._task_find
        branch_numbers: range = range(scruby_self._max_number_branch)
        hash_reduce_left: int = scruby_self._hash_reduce_left
        db_root: str = scruby_self._db_root
        class_model: Any = scruby_self._class_model
        stop_signal = Event()
        doc: Any | None = None
        # Run quantum loop
        with ThreadPoolExecutor(scruby_self._max_workers) as executor:
            futures: list[Future] = [
                executor.submit(
                    search_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    db_root,
                    class_model,
                    stop_signal,
                )
                for branch_number in branch_numbers
            ]
            for future in as_completed(futures):
                docs = await future.result()
                if docs is not None:
                    # Get first document
                    doc = docs[0]
                    # Cancel all pending tasks in the queue instantly
                    executor.shutdown(wait=False, cancel_futures=True)
                    # Trigger the event to tell running tasks to exit
                    stop_signal.set()
                    # Stop loop
                    break
        # Return document
        return doc.model_dump_json()

    @final
    async def find_many(
        self,
        filter_fn: Callable = lambda _: True,
        limit_docs: int = 100,
        page_number: int = 1,
        sort_fn: Callable | None = lambda doc: doc.created_at,
        sort_reverse: bool = True,
    ) -> str | None:
        """Asynchronous method for find many documents matching the filter.

        Attention:
            - The search is based on the effect of a quantum loop.
            - The search effectiveness depends on the number of processor threads.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.
                                  By default it searches for all documents.
            limit_docs (int): Limiting the number of documents. Default = 100.
            page_number (int): For pagination. By default = 1.
                               Number of documents per page = limit_docs.
            sort_fn (Callable | None): Sort the list of documents.
                                       By default, documents are sorted by creation date.
            sort_reverse: (bool): Sorting direction.
                                  By default, sort descending (newest to oldest).

        Returns:
            List of documents in json format or None
        """
        if __debug__:
            if limit_docs <= 0:
                msg = "`find_many` => The `limit_docs` parameter must not be less than one."
                raise AssertionError(msg)
            if page_number <= 0:
                msg = "`find_many` => The `page_number` parameter must not be less than one."
                raise AssertionError(msg)
        # Get Scruby instance
        scruby_self = self.scruby_self()
        # Variable initialization
        search_task_fn: Callable = self._task_find
        branch_numbers: range = range(scruby_self._max_number_branch)
        hash_reduce_left: int = scruby_self._hash_reduce_left
        db_root: str = scruby_self._db_root
        class_model: Any = scruby_self._class_model
        stop_signal = Event()
        stop_outer_loop: bool = False
        counter: int = 0
        number_docs_skippe: int = limit_docs * (page_number - 1) if page_number > 1 else 0
        result: list[str] = []
        # Run quantum loop
        with ThreadPoolExecutor(scruby_self._max_workers) as executor:
            futures: list[Future] = [
                executor.submit(
                    search_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    db_root,
                    class_model,
                    stop_signal,
                )
                for branch_number in branch_numbers
            ]
            for future in as_completed(futures):
                docs = await future.result()
                if docs is not None:
                    for doc in docs:
                        if number_docs_skippe == 0:
                            if counter >= limit_docs:
                                # Cancel all pending tasks in the queue instantly
                                executor.shutdown(wait=False, cancel_futures=True)
                                # Trigger the event to tell running tasks to exit
                                stop_signal.set()
                                # Stop loops
                                stop_outer_loop = True
                                break
                            result.append(doc)
                            counter += 1
                        else:
                            number_docs_skippe -= 1
                if stop_outer_loop:
                    break
        # Sorting
        if sort_fn is not None:
            result.sort(key=sort_fn, reverse=sort_reverse)
        # Convert to JSON
        result_json: str = f"[{','.join([item.model_dump_json() for item in result])}]"
        # Return a list of documents in json format or None
        return result_json if result else None
