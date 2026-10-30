import hashlib
import json
from dataclasses import dataclass

from ..constants import (
    SLOT_BLANK,
    SLOT_IMAGINARY,
    SLOT_MINUS,
    UNKNOWN,
)

@dataclass(frozen=True)
class Classification:
    """应用 UNKNOWN 拒绝规则后的 top-1 分类结果。"""

    kind: str
    best_kind: str
    confidence: float
    margin: float


@dataclass(frozen=True)
class CellRecognition:
    row: int
    column: int
    classification: Classification


@dataclass(frozen=True)
class CounterRecognition:
    position: int
    box: dict[str, float]
    flag: Classification | None
    slots: tuple[Classification, ...]

    @property
    def display_text(self) -> str:
        return "".join(_slot_text(slot.kind) for slot in self.slots)


@dataclass(frozen=True)
class RecognitionSnapshot:
    """单帧一次识别的不可变结果。"""

    frame_number: int
    board_key: str
    captured_at: float
    capture_rect: dict[str, int]
    provider: str
    rows: int
    columns: int
    column_edges: tuple[float, ...]
    row_edges: tuple[float, ...]
    cells: tuple[CellRecognition, ...]
    counters: tuple[CounterRecognition, ...]
    timings_ms: dict[str, float]


def snapshot_to_qml(snapshot: RecognitionSnapshot) -> dict[str, object]:
    """把快照展开为 QML 可用的 QVariant 字典。"""
    return {
        "frame_number": snapshot.frame_number,
        "board_key": snapshot.board_key,
        "captured_at": snapshot.captured_at,
        "capture_rect": dict(snapshot.capture_rect),
        "provider": snapshot.provider,
        "board": {
            "rows": snapshot.rows,
            "columns": snapshot.columns,
            "column_edges": list(snapshot.column_edges),
            "row_edges": list(snapshot.row_edges),
            "cells": [
                {
                    "row": cell.row,
                    "column": cell.column,
                    "kind": cell.classification.kind,
                }
                for cell in snapshot.cells
            ],
        },
        "counters": [
            {
                "position": counter.position,
                "box": dict(counter.box),
                "flag_kind": (
                    counter.flag.kind if counter.flag is not None else UNKNOWN
                ),
                "display_text": counter.display_text,
                "slots": [
                    {
                        "index": index,
                        "kind": slot.kind,
                    }
                    for index, slot in enumerate(counter.slots, start=1)
                ],
            }
            for counter in snapshot.counters
        ],
        "timings_ms": dict(snapshot.timings_ms),
    }


def make_board_key(
    rows: int,
    columns: int,
    cells: tuple[CellRecognition, ...],
    counters: tuple[CounterRecognition, ...],
) -> str:
    """只对玩法事实做哈希；几何变化不改变键值，
    移动框选区域不会触发重新求解。"""
    payload = {
        "rows": rows,
        "columns": columns,
        "cells": [
            [cell.row, cell.column, cell.classification.kind]
            for cell in cells
        ],
        "counters": [
            [
                counter.position,
                counter.flag.kind if counter.flag is not None else UNKNOWN,
                [slot.kind for slot in counter.slots],
            ]
            for counter in counters
        ],
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:24]


def _slot_text(kind: str) -> str:
    if kind == SLOT_BLANK:
        return ""
    if kind == SLOT_MINUS:
        return "-"
    if kind == SLOT_IMAGINARY:
        return "i"
    if len(kind) == 1 and kind.isdigit():
        return kind
    return "?"
