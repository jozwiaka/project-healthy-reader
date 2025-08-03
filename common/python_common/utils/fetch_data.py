import httpx
import pandas as pd

def fetch_all(url, timeout=30):
    """Fetch all pages from a paginated DRF endpoint."""
    results = []
    next_url = url

    while next_url:
        response = httpx.get(next_url, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        # DRF pagination format: { "count": ..., "next": ..., "previous": ..., "results": [...] }
        results.extend(data.get("results", []))
        next_url = data.get("next")  # if None → loop ends

    return pd.DataFrame(results)

def fetch(url, timeout=30):
    response = httpx.get(url, timeout=timeout)
    response.raise_for_status()
    return pd.DataFrame(response.json())
