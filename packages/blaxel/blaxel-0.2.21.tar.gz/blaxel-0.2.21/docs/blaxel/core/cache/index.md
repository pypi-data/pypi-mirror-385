Module blaxel.core.cache
========================

Sub-modules
-----------
* blaxel.core.cache.cache

Functions
---------

`find_from_cache(resource: str, name: str) ‑> typing.Any | None`
:   Find a resource from the cache by resource type and name.
    
    Args:
        resource: The resource type
        name: The resource name
    
    Returns:
        The cached resource or None if not found