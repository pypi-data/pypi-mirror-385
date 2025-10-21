def drop_none_entries(data: dict) -> dict:
    return {k: v for k, v in data.items() if v is not None}
