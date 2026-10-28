from .types import SolverCellHint, SolverOption, SolverResult


class Demo30By16Solver:
    def __call__(self, snapshot: dict[str, object]) -> SolverResult | None:
        board = snapshot.get("board")
        board_key = snapshot.get("board_key")
        if not isinstance(board, dict) or not isinstance(board_key, str):
            return None
        if board.get("rows") != 16 or board.get("columns") != 30:
            return None

        hints = (
            SolverCellHint(0, 0, (SolverOption("OPEN", 1.0),)),
            SolverCellHint(0, 1, (SolverOption("FLAG_POSITIVE_REAL", 1.0),)),
            SolverCellHint(0, 2, (SolverOption("FLAG_NEGATIVE_REAL", 1.0),)),
            SolverCellHint(0, 3, (SolverOption("FLAG_POSITIVE_IMAGINARY", 1.0),)),
            SolverCellHint(0, 4, (SolverOption("FLAG_NEGATIVE_IMAGINARY", 1.0),)),
            SolverCellHint(1, 0, (SolverOption("FLAG_POSITIVE_REAL", 0.72),)),
            SolverCellHint(1, 1, (SolverOption("FLAG_NEGATIVE_REAL", 0.64),)),
            SolverCellHint(1, 2, (SolverOption("FLAG_POSITIVE_IMAGINARY", 0.58),)),
            SolverCellHint(1, 3, (SolverOption("FLAG_NEGATIVE_IMAGINARY", 0.53),)),
            SolverCellHint(1, 4, (SolverOption("OPEN", 0.61),)),
            SolverCellHint(
                2,
                0,
                (
                    SolverOption("FLAG_POSITIVE_IMAGINARY", 0.63),
                    SolverOption("FLAG_NEGATIVE_REAL", 0.20),
                    SolverOption("OPEN", 0.17),
                ),
            ),
            SolverCellHint(
                2,
                1,
                (
                    SolverOption("OPEN", 0.55),
                    SolverOption("FLAG_POSITIVE_REAL", 0.45),
                ),
            ),
        )
        return SolverResult(
            board_key=board_key,
            rows=16,
            columns=30,
            status="partial",
            hints=hints,
            source="demo",
        )
