from PySide6.QtCore import Property, QObject, Signal, Slot


class RecognitionViewState(QObject):
    snapshotChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._snapshot: dict[str, object] = {}

    @Property("QVariantMap", notify=snapshotChanged)
    def snapshot(self) -> dict[str, object]:
        return dict(self._snapshot)

    @Slot(object)
    def set_snapshot(self, snapshot: object) -> None:
        if not isinstance(snapshot, dict):
            return
        self._snapshot = dict(snapshot)
        self.snapshotChanged.emit()
