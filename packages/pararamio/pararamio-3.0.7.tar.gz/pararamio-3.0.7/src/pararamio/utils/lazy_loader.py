"""Lazy loading utilities for sync operations."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence

__all__ = ['lazy_loader']

ItemT = TypeVar('ItemT')
ClsT = TypeVar('ClsT')

log = logging.getLogger('pararamio.lazy_loader')


def lazy_loader(
    cls: ClsT,
    items: Sequence[int],
    load_fn: Callable[[ClsT, Sequence[int]], list[ItemT]],
    per_load: int = 50,
) -> Iterable[ItemT]:
    """Load items lazily in batches from a sequence of IDs.

    Optimized implementation that:
    - Loads batches only once per batch
    - Handles empty results gracefully
    - Logs batch operations for debugging

    Args:
        cls: The class or instance context used by the load function.
        items: The collection of item IDs to be loaded.
        load_fn: Function responsible for loading a batch of items.
            Must accept the class/instance and a subset of IDs,
            and return a list of loaded items.
        per_load: Number of items to load in each batch. Default: 50.

    Yields:
        Loaded items one at a time.

    Example:
        >>> users = lazy_loader(client, [1, 2, 3, 4, 5], User.load_users, per_load=2)
        >>> for user in users:
        ...     print(user.name)
        # Loads in 3 batches: [1,2], [3,4], [5]
    """
    if not items:
        log.debug('lazy_loader: No items to load')
        return

    total_items = len(items)
    log.debug('lazy_loader: Loading %d items in batches of %d', total_items, per_load)

    # Process items in batches
    for batch_idx in range(0, total_items, per_load):
        batch_end = min(batch_idx + per_load, total_items)
        batch_ids = items[batch_idx:batch_end]

        log.debug(
            'lazy_loader: Loading batch %d/%d (%d items)',
            (batch_idx // per_load) + 1,
            (total_items + per_load - 1) // per_load,
            len(batch_ids),
        )

        # Load the batch
        loaded_items = load_fn(cls, batch_ids)

        if not loaded_items:
            log.warning('lazy_loader: Batch returned no items for IDs: %s', batch_ids)
            continue

        # Yield items from this batch
        yield from loaded_items
