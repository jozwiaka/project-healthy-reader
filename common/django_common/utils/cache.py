import hashlib


def make_cache_key(prefix: str, identifier: str = "", query_params: str = "") -> str:
    """Generate consistent cache keys"""
    if query_params:
        query_hash = hashlib.md5(query_params.encode()).hexdigest()
        return f"{prefix}:{identifier}:{query_hash}"
    return f"{prefix}:{identifier}" if identifier else prefix
