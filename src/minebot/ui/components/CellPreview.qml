pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts

// 渲染最新识别快照的棋盘；行列数来自快照，
// 正确支持非正方形棋盘布局。
Item {
    id: root

    required property var theme

    readonly property string cellAssetRoot: Qt.resolvedUrl("../assets/cells/")
    readonly property var snapshot: root.theme.recognitionSnapshot
    readonly property var boardCells: root.snapshot.board
        ? root.snapshot.board.cells
        : []
    readonly property int boardRows: root.snapshot.board
        ? root.snapshot.board.rows
        : 0
    readonly property int boardColumns: root.snapshot.board
        ? root.snapshot.board.columns
        : 0
    readonly property var counters: root.snapshot.counters || []

    function flagLabel(kind) {
        switch (kind) {
        case "POSITIVE_REAL": return "正实 +";
        case "NEGATIVE_REAL": return "负实 -";
        case "POSITIVE_IMAGINARY": return "正虚 +i";
        case "NEGATIVE_IMAGINARY": return "负虚 -i";
        default: return "N/A";
        }
    }

    function slotGlyph(slot) {
        if (!slot || slot.kind === "UNKNOWN")
            return "?";
        if (slot.kind === "BLANK")
            return "";
        if (slot.kind === "MINUS")
            return "-";
        if (slot.kind === "IMAGINARY")
            return "i";
        return slot.kind;
    }

    readonly property var counterPreview: {
        const values = [];
        for (let index = 0; index < 4; index += 1) {
            const counter = root.counters[index];
            const glyphs = [];
            if (counter) {
                for (let slotIndex = 0; slotIndex < 4; slotIndex += 1) {
                    glyphs.push(root.slotGlyph(counter.slots[slotIndex]));
                }
            } else {
                glyphs.push("-", "-", "-", "-");
            }
            values.push({
                label: counter ? root.flagLabel(counter.flag_kind) : "N/A",
                glyphs: glyphs
            });
        }
        return values;
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 5

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 46
            radius: 4
            color: root.theme.surfaceAlt
            border.width: 1
            border.color: root.theme.borderColor

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 6
                anchors.rightMargin: 6
                spacing: 8

                Repeater {
                    model: root.counterPreview

                    ColumnLayout {
                        id: counterItem
                        required property var modelData
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 1

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: counterItem.modelData.label
                            color: root.theme.textMuted
                            font.family: root.theme.fontFamily
                            font.pixelSize: 9
                            font.weight: Font.DemiBold
                        }

                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            Row {
                                anchors.centerIn: parent
                                spacing: 1

                                Repeater {
                                    model: counterItem.modelData.glyphs

                                    Text {
                                        required property string modelData

                                        visible: text.length > 0
                                        text: modelData
                                        width: text === "1"
                                            ? Math.round(implicitWidth * 0.82)
                                            : implicitWidth
                                        horizontalAlignment: Text.AlignHCenter
                                        color: root.theme.textPrimary
                                        font.family: root.theme.fontFamily
                                        font.pixelSize: 11
                                        font.weight: Font.Bold
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            Grid {
                id: previewGrid
                anchors.centerIn: parent
                columns: Math.max(1, root.boardColumns)
                spacing: 1
                visible: root.boardCells.length > 0

                readonly property real cellSize: Math.max(
                    1,
                    Math.min(
                        (parent.width - spacing * Math.max(0, columns - 1))
                            / Math.max(1, columns),
                        (parent.height - spacing * Math.max(0, root.boardRows - 1))
                            / Math.max(1, root.boardRows)
                    )
                )

                Repeater {
                    model: root.boardCells

                    Image {
                        id: boardCell
                        required property var modelData

                        width: previewGrid.cellSize
                        height: previewGrid.cellSize
                        source: root.cellAssetRoot + (modelData.kind || "UNKNOWN") + ".png"
                        fillMode: Image.Stretch
                        smooth: false
                        mipmap: false
                        cache: true
                    }
                }
            }

            Text {
                anchors.centerIn: parent
                visible: root.boardCells.length === 0
                text: "等待识别结果"
                color: root.theme.textMuted
                font.family: root.theme.fontFamily
                font.pixelSize: 10
            }
        }
    }
}
