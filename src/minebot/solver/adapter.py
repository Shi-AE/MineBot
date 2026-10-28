import threading
from collections.abc import Callable

from PySide6.QtCore import QObject, Signal, Slot

from .types import SolverResult


SolverHandler = Callable[[dict[str, object]], SolverResult | None]


class SolverAdapter(QObject):
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
                with self._condition:
                    self._last_board_key = ""
                self._error_signal.emit(f"solver submit failed: {error}")
