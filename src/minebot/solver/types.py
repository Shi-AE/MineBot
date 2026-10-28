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
    row: int
    column: int
    options: tuple[SolverOption, ...]


@dataclass(frozen=True)
class SolverResult:
    board_key: str
    rows: int
    columns: int
    status: str
    hints: tuple[SolverCellHint, ...]
    source: str = "solver"

    def to_qml(self) -> dict[str, object]:
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
    if not result.board_key:
        raise ValueError("solver result is missing board_key")
    if result.status not in RESULT_STATUSES:
        raise ValueError(f"invalid solver status: {result.status}")
    if result.rows <= 0 or result.columns <= 0:
        raise ValueError("solver board dimensions must be positive")

    seen: set[tuple[int, int]] = set()
    for hint in result.hints:
        if not 0 <= hint.row < result.rows:
            raise ValueError(f"solver row out of range: {hint.row}")
        if not 0 <= hint.column < result.columns:
            raise ValueError(f"solver column out of range: {hint.column}")
        if (hint.row, hint.column) in seen:
            raise ValueError(
                f"duplicate solver hint: row={hint.row}, column={hint.column}"
            )
        seen.add((hint.row, hint.column))
        if not hint.options:
            raise ValueError(
                f"solver hint has no options: row={hint.row}, column={hint.column}"
            )
        for option in hint.options:
            if option.kind not in HINT_KINDS:
                raise ValueError(f"invalid solver option kind: {option.kind}")
            if not 0.0 <= option.probability <= 1.0:
                raise ValueError(
                    f"invalid solver probability: {option.probability}"
                )
    return result
