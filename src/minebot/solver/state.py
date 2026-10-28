from PySide6.QtCore import Property, QObject, Signal, Slot

from .types import SolverResult, validate_result


class SolverViewState(QObject):
    """求解结果与 QML 之间的主线程桥接。

    持有最新棋盘标识，异步返回的过期结果在到达 UI 前被丢弃。
    """

    resultChanged = Signal()
    selectedChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._board_key = ""
        self._rows = 0
        self._columns = 0
        self._result: dict[str, object] = {}
        self._selected: dict[str, int] = {}

    @Property("QVariantMap", notify=resultChanged)
    def result(self) -> dict[str, object]:
        return dict(self._result)

    @Property("QVariantMap", notify=selectedChanged)
    def selected_hint(self) -> dict[str, int]:
        return dict(self._selected)

    @Slot(object)
    def set_recognition_snapshot(self, snapshot: object) -> None:
        if not isinstance(snapshot, dict):
            return
        board_key = str(snapshot.get("board_key", ""))
        board = snapshot.get("board")
        # 在主线程跟踪最新棋盘标识；求解结果异步到达时与它比较。
        if isinstance(board, dict):
            self._rows = int(board.get("rows", 0))
            self._columns = int(board.get("columns", 0))
        if board_key == self._board_key:
            return

        self._board_key = board_key
        self._clear_selection()
        if self._result.get("board_key") != board_key:
            self._result = {}
            self.resultChanged.emit()

    @Slot(int, int)
    def select_hint(self, row: int, column: int) -> None:
        if (
            self._selected.get("row") == row
            and self._selected.get("column") == column
        ):
            self._clear_selection()
            return

        self._selected = {"row": row, "column": column}
        self.selectedChanged.emit()

    def _clear_selection(self) -> None:
        if not self._selected:
            return
        self._selected = {}
        self.selectedChanged.emit()

    @Slot(object)
    def set_result(self, result: object) -> None:
        if not isinstance(result, SolverResult):
            return
        try:
            validated = validate_result(result)
        except ValueError:
            return
        if (
            validated.board_key != self._board_key
            or validated.rows != self._rows
            or validated.columns != self._columns
        ):
            return

        result = validated.to_qml()
        # 重复的相同结果不重复发出变更信号。
        if result == self._result:
            return
        self._result = result
        self.resultChanged.emit()
