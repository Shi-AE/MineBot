"""真实求解器的正式实现文件（算法由用户编写）。

链路位置：
    识别线程 snapshotReady
      → SolverAdapter.submit_snapshot（主线程）
      → 求解工作线程调用本文件的 MineBotSolver.__call__
      → 返回 SolverResult → resultReady
      → SolverViewState（校验 board_key，丢弃过期结果）
      → QML 渲染（蒙版提示 + 右侧详情面板）

接入方式：
    在 app.py 的【求解器接入点】把 SolverAdapter(None, app) 改为
    SolverAdapter(MineBotSolver(), app)。除此之外不需要改动任何信号或 UI。

线程约定：
    __call__ 在独立求解工作线程中执行。禁止在其中创建或操作任何
    QWidget/QML 对象；只做纯计算并通过返回值交付结果。

调用频率：
    只有棋盘内容变化（board_key 改变）才会触发一次调用；相同 board_key
    不会重复求解。上一次调用尚未结束时，新快照只会覆盖排队槽位，不会
    中断当前计算，因此算法应尽量保持快速；如需中断，请在算法内部自行
    实现协作式取消。
"""

from __future__ import annotations

from .types import SolverCellHint, SolverOption, SolverResult


class MineBotSolver:
    """求解器实现类；实例本身就是 SolverHandler（可直接传给 SolverAdapter）。

    必须遵守的返回契约（SolverViewState 会强制校验，违规结果被丢弃）：
    - board_key 必须原样返回入参 snapshot["board_key"]；
    - rows/columns 必须与入参棋盘一致；
    - status 取值：solved / partial / conflict / unknown；
    - hints 按格子分组，每格一个 SolverCellHint，格子不重复；
    - 每个候选 SolverOption.kind 只能是 OPEN 或四类 FLAG_*，
      probability ∈ [0, 1]，同一格内按概率从高到低排序；
    - 求解器概率（probability）与识别置信度（confidence）是两回事，
      不要混用。
    """

    def __call__(self, snapshot: dict[str, object]) -> SolverResult | None:
        """每次棋盘变化被调用一次；返回 None 表示本帧不产出任何建议。"""
        board = self._board(snapshot)
        if board is None:
            return None

        rows: int = board["rows"]
        columns: int = board["columns"]
        grid, counters = self._parse(snapshot)

        # ── 算法区 ────────────────────────────────────────────────
        # grid[row][column] 是该格的识别信息 dict：
        #   kind        识别模块按阈值判定后的类别（UNKNOWN 表示不可信）
        #   best_kind   阈值判定前的 top-1 类别
        #   confidence  识别置信度；margin 与 top-2 的概率差
        # counters 是四个余雷区的解析结果 dict：
        #   flag_kind   POSITIVE_REAL / NEGATIVE_REAL /
        #               POSITIVE_IMAGINARY / NEGATIVE_IMAGINARY / UNKNOWN
        #   value       解析出的复数值（失败时为 None）
        #
        # 在这里实现求解算法，产出 self._hint(...) 列表。
        # 概率不确定时仍可给多候选：蒙版显示最高概率项，
        # 详情面板显示全部候选。
        # ─────────────────────────────────────────────────────────
        hints: list[SolverCellHint] = []

        # 骨架阶段没有任何可展示的结论，直接放弃本帧。
        return None

    # ── 以下为输入解析辅助，通常无需修改 ─────────────────────────

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
    ) -> tuple[list[list[dict[str, object] | None]], list[dict[str, object]]]:
        """把 QML 快照展开成 rows×columns 矩阵和余雷区数值列表。"""
        board = self._board(snapshot)
        assert board is not None
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
