from __future__ import annotations

from .types import SolverCellHint, SolverOption, SolverResult


class MineBotSolver:

    def __call__(self, snapshot: dict[str, object]) -> SolverResult | None:
        """每次棋盘变化被调用一次；返回 None 表示本帧不产出任何建议。"""
        board = self._board(snapshot)
        if board is None:
            return None

        rows: int = board["rows"]
        columns: int = board["columns"]
        grid, counters = self._parse(snapshot, board)
        print(grid)
        hints: list[SolverCellHint] = []

        return None

    # ── 以下为输入解析辅助 ─────────────────────────

    def _board(self, snapshot: dict[str, object]) -> dict[str, object] | None:
        """校验快照形状；不完整时返回 None，本帧静默放弃。"""
        board = snapshot.get("board")
        if not isinstance(board, dict):
            return None
        rows = board.get("rows")
        columns = board.get("columns")
        if not isinstance(rows, int) or not isinstance(columns, int):
            return None
        if rows <= 0 or columns <= 0 or not isinstance(board.get("cells"), list):
            return None
        return board

    def _parse(
            self,
            snapshot: dict[str, object],
            board: dict[str, object],
    ) -> tuple[list[list[dict[str, object] | None]], list[dict[str, object]]]:
        """把已校验的棋盘展开成 rows×columns 矩阵和余雷区数值列表。"""
        rows: int = board["rows"]
        columns: int = board["columns"]
        grid: list[list[dict[str, object] | None]] = [
            [None] * columns for _ in range(rows)
        ]
        for cell in board["cells"]:
            grid[cell["row"]][cell["column"]] = cell
        return grid, self._counters(snapshot)

    def _counters(self, snapshot: dict[str, object]) -> list[dict[str, object]]:
        """把四个余雷区解析成 (实部, 虚部) 数值，失败处为 None。"""
        parsed: list[dict[str, object]] = []
        for counter in snapshot.get("counters", []):
            parsed.append(
                {
                    "flag_kind": counter.get("flag_kind"),
                    "value": self._counter_value(counter.get("display_text", "")),
                }
            )
        return parsed

    @staticmethod
    def _counter_value(display_text: str) -> tuple[int, int] | None:
        """把 LED 文本（如 -021 / 018i / -26i）解析成复数分量。

        空串或解析失败返回 None；三位数以内的文本必然匹配该格式。
        """
        text = display_text.strip()
        if not text:
            return None
        try:
            if text.endswith("i"):
                imaginary = int(text[:-1] or "1")
                if imaginary == 0 and text[:-1] not in ("0", "+"):
                    return None
                return (0, imaginary)
            return (int(text), 0)
        except ValueError:
            return None

    # ── 结果构造辅助 ─────────────────────────────────────────────

    @staticmethod
    def _hint(
            row: int,
            column: int,
            options: list[tuple[str, float]],
    ) -> SolverCellHint:
        """把 (类型, 概率) 列表转成 SolverCellHint，并按概率降序。"""
        ordered = sorted(options, key=lambda item: item[1], reverse=True)
        return SolverCellHint(
            row=row,
            column=column,
            options=tuple(SolverOption(kind, probability) for kind, probability in ordered),
        )

    @staticmethod
    def _result(
            snapshot: dict[str, object],
            status: str,
            hints: list[SolverCellHint],
    ) -> SolverResult:
        """统一构造 SolverResult；board_key 必须来自入参快照。"""
        board = snapshot["board"]
        assert isinstance(board, dict)
        return SolverResult(
            board_key=str(snapshot.get("board_key", "")),
            rows=int(board["rows"]),
            columns=int(board["columns"]),
            status=status,
            hints=tuple(hints),
        )
