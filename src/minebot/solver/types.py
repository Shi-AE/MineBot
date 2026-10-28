from dataclasses import dataclass


FLAG_KINDS = frozenset(
    {
        "FLAG_POSITIVE_REAL",
        "FLAG_NEGATIVE_REAL",
        "FLAG_POSITIVE_IMAGINARY",
        "FLAG_NEGATIVE_IMAGINARY",
    }
)
HINT_KINDS = FLAG_KINDS | {"OPEN"}
RESULT_STATUSES = frozenset({"solved", "partial", "conflict", "unknown"})


@dataclass(frozen=True)
class SolverOption:
    kind: str
    probability: float


@dataclass(frozen=True)
class SolverCellHint:
    """单个格子的全部候选解释，按概率从高到低。"""

    row: int
    column: int
    options: tuple[SolverOption, ...]


@dataclass(frozen=True)
class SolverResult:
    """与计算时的棋盘标识绑定的求解答案。"""

    board_key: str
    rows: int
    columns: int
    status: str
    hints: tuple[SolverCellHint, ...]
    source: str = "solver"

    def to_qml(self) -> dict[str, object]:
        """展开为 SolverViewState 可用的 QVariant 字典。"""
        return {
            "board_key": self.board_key,
            "rows": self.rows,
            "columns": self.columns,
            "status": self.status,
            "source": self.source,
            "hints": [
                {
                    "row": hint.row,
                    "column": hint.column,
                    "options": [
                        {
                            "kind": option.kind,
                            "probability": option.probability,
                        }
                        for option in hint.options
                    ],
                }
                for hint in self.hints
            ],
        }


def validate_result(result: SolverResult) -> SolverResult:
    """在进入 UI 前拒绝格式非法的求解结果。"""
    if not result.board_key:
        raise ValueError("求解结果缺少 board_key")
    if result.status not in RESULT_STATUSES:
        raise ValueError(f"非法求解状态: {result.status}")
    if result.rows <= 0 or result.columns <= 0:
        raise ValueError("求解棋盘尺寸必须为正")

    seen: set[tuple[int, int]] = set()
    for hint in result.hints:
        if not 0 <= hint.row < result.rows:
            raise ValueError(f"求解行号越界: {hint.row}")
        if not 0 <= hint.column < result.columns:
            raise ValueError(f"求解列号越界: {hint.column}")
        if (hint.row, hint.column) in seen:
            raise ValueError(
                f"重复的求解提示: 行={hint.row}, 列={hint.column}"
            )
        seen.add((hint.row, hint.column))
        if not hint.options:
            raise ValueError(
                f"求解提示缺少候选: 行={hint.row}, 列={hint.column}"
            )
        for option in hint.options:
            if option.kind not in HINT_KINDS:
                raise ValueError(f"非法候选类型: {option.kind}")
            if not 0.0 <= option.probability <= 1.0:
                raise ValueError(
                    f"非法概率值: {option.probability}"
                )
    return result
