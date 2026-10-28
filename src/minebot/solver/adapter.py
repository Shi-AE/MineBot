import threading
from collections.abc import Callable

from PySide6.QtCore import QObject, Signal, Slot

from .types import SolverResult


SolverHandler = Callable[[dict[str, object]], SolverResult | None]


# 求解链路：
# 识别线程 snapshotReady → SolverAdapter.submit_snapshot（主线程）
#   → 工作线程 handler(snapshot) → resultReady → SolverViewState → QML
# 真实求解器只需实现 SolverHandler 并在 app.py 接入点传入；
# 返回 None 表示本帧不产出建议，异常会被捕获并通过 errorRaised 上报。
class SolverAdapter(QObject):
    """把识别快照转发给用户求解器，handler 在独立工作线程执行。"""

    resultReady = Signal(object)
    errorRaised = Signal(str)

    def __init__(
        self,
        handler: SolverHandler | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._worker = _SolverWorker(
            handler,
            self.resultReady,
            self.errorRaised,
        )

    @Slot(object)
    def submit_snapshot(self, snapshot: object) -> None:
        if not isinstance(snapshot, dict):
            return
        self._worker.submit(dict(snapshot))

    @Slot()
    def stop(self) -> None:
        self._worker.stop()


class _SolverWorker:
    """单线程执行器，带“最新优先”的待处理槽位。

    相同 board_key 在入队前被拒绝，因此识别全速运行时，
    棋盘不变不会重复求解。
    """

    def __init__(
        self,
        handler: SolverHandler | None,
        result_signal: Signal,
        error_signal: Signal,
    ) -> None:
        self._handler = handler
        self._result_signal = result_signal
        self._error_signal = error_signal
        self._condition = threading.Condition()
        self._pending: dict[str, object] | None = None
        self._last_board_key = ""
        self._stopping = False
        self._thread = threading.Thread(
            target=self._run,
            name="minebot-solver",
            daemon=True,
        )
        self._thread.start()

    def submit(self, snapshot: dict[str, object]) -> None:
        board_key = str(snapshot.get("board_key", ""))
        with self._condition:
            if self._stopping:
                return
            if board_key and board_key == self._last_board_key:
                return
            # 最新优先：排队中的旧棋盘会被覆盖，而不是累积。
            self._last_board_key = board_key
            self._pending = snapshot
            self._condition.notify()

    def stop(self) -> None:
        with self._condition:
            self._stopping = True
            self._pending = None
            self._condition.notify()
        self._thread.join(timeout=2.0)

    def _run(self) -> None:
        while True:
            with self._condition:
                while self._pending is None and not self._stopping:
                    self._condition.wait()
                if self._stopping:
                    return
                snapshot = self._pending
                self._pending = None

            if self._handler is None:
                continue
            try:
                result = self._handler(snapshot)
                if result is not None:
                    self._result_signal.emit(result)
            except Exception as error:
                # handler 失败后允许同一棋盘重试。
                with self._condition:
                    self._last_board_key = ""
                self._error_signal.emit(f"求解器提交失败: {error}")
