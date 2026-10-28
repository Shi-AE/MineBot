pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts

// 按格子分组显示求解提示的全部候选；点击分组会选中该格子，
// 蒙版提示层随之高亮。
Panel {
    id: root

    readonly property var result: theme.solverResult
    readonly property var hints: result.hints || []
    readonly property var selectedHint: theme.solverState.selected_hint
    readonly property string hintAssetRoot: Qt.resolvedUrl("../assets/hints/")

    function kindLabel(kind) {
        switch (kind) {
        case "OPEN": return "可开格";
        case "FLAG_POSITIVE_REAL": return "正实 +";
        case "FLAG_NEGATIVE_REAL": return "负实 -";
        case "FLAG_POSITIVE_IMAGINARY": return "正虚 +i";
        case "FLAG_NEGATIVE_IMAGINARY": return "负虚 -i";
        default: return kind;
        }
    }

    function statusLabel(status) {
        switch (status) {
        case "solved": return "已完成";
        case "partial": return "部分求解";
        case "conflict": return "结果冲突";
        case "unknown": return "无法确定";
        default: return "等待中";
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 47
            color: "transparent"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 14
                anchors.rightMargin: 14

                Text {
                    text: "求解提示"
                    color: root.theme.textPrimary
                    font.family: root.theme.fontFamily
                    font.pixelSize: 11
                    font.weight: Font.DemiBold
                    Layout.fillWidth: true
                }

                Text {
                    text: root.result.status
                        ? root.statusLabel(root.result.status)
                        : "等待中"
                    color: root.theme.textFaint
                    font.family: root.theme.fontFamily
                    font.pixelSize: 9
                }
            }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: 1
                color: root.theme.borderColor
            }
        }

        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 7
            visible: root.hints.length > 0
            clip: true
            spacing: 3
            model: root.hints

            delegate: Rectangle {
                id: hintRow
                required property var modelData

                readonly property bool selected:
                    root.selectedHint.row === hintRow.modelData.row
                    && root.selectedHint.column === hintRow.modelData.column

                width: ListView.view.width
                height: optionColumn.implicitHeight + 14
                radius: 7
                color: hintRow.selected
                    ? root.theme.accentSoft
                    : root.theme.surfaceAlt
                border.width: hintRow.selected ? 1 : 0
                border.color: root.theme.accent

                ColumnLayout {
                    id: optionColumn

                    anchors.fill: parent
                    anchors.margins: 7
                    spacing: 3

                    RowLayout {
                        spacing: 6

                        Layout.fillWidth: true

                        Text {
                            text: "R" + (hintRow.modelData.row + 1)
                                + " C" + (hintRow.modelData.column + 1)
                            color: root.theme.textFaint
                            font.family: root.theme.monoFontFamily
                            font.pixelSize: 8
                            Layout.fillWidth: true
                        }

                        Text {
                            text: hintRow.modelData.options.length + " 项"
                            color: root.theme.textFaint
                            font.family: root.theme.fontFamily
                            font.pixelSize: 8
                        }
                    }

                    Repeater {
                        model: hintRow.modelData.options

                        RowLayout {
                            id: optionRow
                            required property var modelData

                            Layout.fillWidth: true
                            spacing: 6

                            Item {
                                Layout.preferredWidth: 18
                                Layout.preferredHeight: 18

                                Rectangle {
                                    anchors.centerIn: parent
                                    width: 14
                                    height: 14
                                    radius: 7
                                    visible: optionRow.modelData.kind === "OPEN"
                                    color: "transparent"
                                    border.width: 2
                                    border.color: root.theme.success
                                }

                                Rectangle {
                                    anchors.centerIn: parent
                                    width: 4
                                    height: 4
                                    radius: 2
                                    visible: optionRow.modelData.kind === "OPEN"
                                    color: root.theme.success
                                }

                                Image {
                                    anchors.fill: parent
                                    visible: optionRow.modelData.kind !== "OPEN"
                                    source: root.hintAssetRoot
                                        + optionRow.modelData.kind + ".png"
                                    fillMode: Image.PreserveAspectFit
                                    smooth: false
                                }
                            }

                            Text {
                                Layout.fillWidth: true
                                text: root.kindLabel(optionRow.modelData.kind)
                                color: optionRow.modelData.kind === "OPEN"
                                    ? root.theme.success
                                    : root.theme.textPrimary
                                font.family: root.theme.fontFamily
                                font.pixelSize: 10
                                font.weight: Font.DemiBold
                            }

                            Text {
                                visible: optionRow.modelData.probability < 0.999999
                                text: Math.round(optionRow.modelData.probability * 100) + "%"
                                color: root.theme.warning
                                font.family: root.theme.monoFontFamily
                                font.pixelSize: 10
                                font.weight: Font.Bold
                            }
                        }
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.theme.solverState.select_hint(
                        hintRow.modelData.row,
                        hintRow.modelData.column)
                }
            }
        }

        Text {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: root.hints.length === 0
            text: "等待求解结果"
            color: root.theme.textMuted
            font.family: root.theme.fontFamily
            font.pixelSize: 10
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }
}
