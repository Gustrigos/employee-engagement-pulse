from __future__ import annotations

import json
import os
from typing import Dict, List, Set


_STATE_PATH = os.environ.get("EPULSE_STATE_FILE", os.path.join(os.path.dirname(__file__), "_state.json"))


def _load_all() -> Dict[str, dict]:
    try:
        if not os.path.exists(_STATE_PATH):
            return {}
        with open(_STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_all(data: Dict[str, dict]) -> None:
    try:
        with open(_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        # best-effort
        pass


def load_selected_channels(team_id: str) -> Set[str]:
    data = _load_all()
    team = data.get(team_id) or {}
    arr = team.get("selected_channel_ids") or []
    if not isinstance(arr, list):
        return set()
    return set(str(x) for x in arr)


def save_selected_channels(team_id: str, channel_ids: List[str]) -> None:
    data = _load_all()
    team = data.get(team_id) or {}
    team["selected_channel_ids"] = list(dict.fromkeys(channel_ids))
    data[team_id] = team
    _save_all(data)


