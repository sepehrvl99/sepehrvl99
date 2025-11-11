"""Simple JSON-backed storage with an in-memory cache."""

from __future__ import annotations

import json
import os
from typing import Dict, List


DATA_FILE = "data.json"


def _default_data() -> Dict[str, List[int] | List[str]]:
    return {
        "users": [],
        "groups": [],
        "keywords": [],
    }

_data_cache: Dict[str, List[int] | List[str]] | None = None


def _ensure_data_shape(data: Dict[str, List[int] | List[str]]) -> Dict[str, List[int] | List[str]]:
    """Backwards compatible normalisation for persisted data."""

    # Old versions stored a single ``user_id`` instead of a list.
    if "user_id" in data and "users" not in data:
        user_id = data.get("user_id")
        users: List[int] = []
        if isinstance(user_id, int):
            users.append(user_id)
        data.pop("user_id", None)
        data["users"] = users

    for key, default_value in _default_data().items():
        data.setdefault(key, default_value)

    return data


def load_data() -> Dict[str, List[int] | List[str]]:
    global _data_cache

    if _data_cache is None:
        if not os.path.exists(DATA_FILE):
            save_data(_default_data())
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        _data_cache = _ensure_data_shape(loaded)

    return _data_cache


def save_data(data: Dict[str, List[int] | List[str]]) -> None:
    global _data_cache
    _data_cache = _ensure_data_shape(data)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(_data_cache, f, ensure_ascii=False, indent=4)


def add_user(user_id: int) -> bool:
    data = load_data()
    users = data["users"]
    if user_id not in users:
        users.append(user_id)
        save_data(data)
        return True
    return False


def add_group(group_id: int) -> bool:
    data = load_data()
    groups = data["groups"]
    if group_id not in groups:
        groups.append(group_id)
        save_data(data)
        return True
    return False


def add_keyword(keyword: str) -> bool:
    data = load_data()
    keywords = data["keywords"]
    if keyword not in keywords:
        keywords.append(keyword)
        save_data(data)
        return True
    return False


def get_users() -> List[int]:
    return list(load_data()["users"])


def get_groups() -> List[int]:
    return list(load_data()["groups"])


def get_keywords() -> List[str]:
    return list(load_data()["keywords"])
