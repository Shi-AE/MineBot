from PySide6.QtCore import Property, QObject, Signal, Slot


class RecognitionViewState(QObject):
    """主线程持有的最新识别快照，供 QML 读取。"""

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
        # 浅拷贝即可：QML 只读普通字典，不会修改内容。
        self._snapshot = dict(snapshot)
        self.snapshotChanged.emit()
