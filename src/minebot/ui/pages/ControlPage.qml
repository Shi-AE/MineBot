pragma
ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import "../components"

Item {
    id: root

    required property Theme theme

    ColumnLayout {
        anchors.fill: parent
        spacing: 14

        Panel {
            Layout.fillWidth: true
            Layout.preferredHeight: 78
            theme: root.theme

            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 13

                Rectangle {
                    Layout.preferredWidth: 10
                    Layout.preferredHeight: 10
                    radius: 5
                    color: root.theme.warning

                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: -5
                        radius: 10
                        color: Qt.rgba(root.theme.warning.r, root.theme.warning.g, root.theme.warning.b, 0.09)
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 3

                    Text {
                        text: "界面框架已就绪"
                        color: root.theme.textPrimary
                        font.family: root.theme.fontFamily
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                    }

                    Text {
                        text: "棋盘识别、自动操作与实时数据将在后续版本接入。"
                        color: root.theme.textMuted
                        font.family: root.theme.fontFamily
                        font.pixelSize: 10
                    }
                }

                Rectangle {
                    Layout.preferredWidth: 95
                    Layout.preferredHeight: 24
                    radius: 12
                    color: root.theme.accentSoft
                    border.width: 1
                    border.color: Qt.rgba(root.theme.accent.r, root.theme.accent.g, root.theme.accent.b, 0.28)

                    Text {
                        anchors.centerIn: parent
                        text: "区域未选择"
                        color: root.theme.accent
                        font.family: root.theme.fontFamily
                        font.pixelSize: 9
                        font.weight: Font.DemiBold
                    }
                }

                Rectangle {
                    Layout.preferredWidth: 119
                    Layout.preferredHeight: 24
                    radius: 12
                    color: root.theme.surfaceAlt
                    border.width: 1
                    border.color: root.theme.borderColor

                    Text {
                        anchors.centerIn: parent
                        text: "F8 开始 · F9 结束"
                        color: root.theme.textMuted
                        font.family: root.theme.fontFamily
                        font.pixelSize: 9
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 14

            Panel {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: 620
                theme: root.theme

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 48
                        color: "transparent"

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 16
                            anchors.rightMargin: 16

                            Text {
                                text: "棋盘预览"
                                color: root.theme.textPrimary
                                font.family: root.theme.fontFamily
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                Layout.fillWidth: true
                            }

                            ActionButton {
                                theme: root.theme
                                text: "选择区域"
                                enabled: false
                                outlined: true
                                foreground: root.theme.accent
                                fillColor: root.theme.accentSoft
                                implicitHeight: 30
                                implicitWidth: 86
                                objectName: "selectRegionButton"
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

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: root.theme.surfaceAlt
                        clip: true

                        GridBackdrop {
                            anchors.fill: parent
                            lineColor: root.theme.borderColor
                            cellSize: 24
                        }

                        Rectangle {
                            id: boardShell

                            readonly property var snapshot: root.theme.recognitionSnapshot
                            readonly property int columns: snapshot.board
                                ? Math.max(1, snapshot.board.columns)
                                : 12
                            readonly property int rows: snapshot.board
                                ? Math.max(1, snapshot.board.rows)
                                : 12
                            readonly property real cellSpacing: 1
                            readonly property real horizontalPadding: 20
                            readonly property real verticalChrome: 71
                            readonly property real maximumWidth: Math.max(
                                1,
                                parent.width - 70
                            )
                            readonly property real maximumHeight: Math.max(
                                1,
                                parent.height - 38
                            )
                            readonly property real heightAtMaximumWidth:
                                (maximumWidth
                                    - horizontalPadding
                                    - Math.max(0, columns - 1) * cellSpacing)
                                    * rows / columns
                                + Math.max(0, rows - 1) * cellSpacing
                                + verticalChrome
                            readonly property bool fitsAtMaximumWidth:
                                heightAtMaximumWidth <= maximumHeight

                            width: fitsAtMaximumWidth
                                ? maximumWidth
                                : (maximumHeight
                                    - verticalChrome
                                    - Math.max(0, rows - 1) * cellSpacing)
                                    * columns / rows
                                    + Math.max(0, columns - 1) * cellSpacing
                                    + horizontalPadding
                            height: fitsAtMaximumWidth
                                ? heightAtMaximumWidth
                                : maximumHeight
                            anchors.centerIn: parent
                            radius: 13
                            color: root.theme.surfaceAlt
                            border.width: 1
                            border.color: root.theme.borderStrong

                            Rectangle {
                                anchors.fill: parent
                                anchors.margins: 10
                                radius: 8
                                color: Qt.darker(root.theme.surface, 1.08)
                                border.width: 1
                                border.color: root.theme.borderColor
                                clip: true

                                CellPreview {
                                    anchors.fill: parent
                                    theme: root.theme
                                }
                            }

                            Rectangle {
                                anchors.centerIn: parent
                                width: 150
                                height: 38
                                radius: 9
                                visible: false
                                color: root.theme.surface
                                border.width: 1
                                border.color: root.theme.borderStrong

                                Text {
                                    anchors.centerIn: parent
                                    text: "待选择棋盘区域"
                                    color: root.theme.textMuted
                                    font.family: root.theme.fontFamily
                                    font.pixelSize: 10
                                    font.weight: Font.DemiBold
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 42
                        color: "transparent"

                        Rectangle {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.top: parent.top
                            height: 1
                            color: root.theme.borderColor
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 16
                            anchors.rightMargin: 16

                            Text {
                                text: root.theme.recognitionSnapshot.board
                                    ? "预览尺寸  "
                                        + root.theme.recognitionSnapshot.board.columns
                                        + " × "
                                        + root.theme.recognitionSnapshot.board.rows
                                    : "预览尺寸  --"
                                color: root.theme.textFaint
                                font.family: root.theme.fontFamily
                                font.pixelSize: 9
                            }

                            Item {
                                Layout.fillWidth: true
                            }

                            Text {
                                text: "目标：等待框选"
                                color: root.theme.textFaint
                                font.family: root.theme.fontFamily
                                font.pixelSize: 9
                            }
                        }
                    }
                }
            }

            ColumnLayout {
                Layout.fillHeight: true
                Layout.preferredWidth: 300
                spacing: 14

                Panel {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 191
                    theme: root.theme

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
                                    text: "本次任务"
                                    color: root.theme.textPrimary
                                    font.family: root.theme.fontFamily
                                    font.pixelSize: 11
                                    font.weight: Font.DemiBold
                                    Layout.fillWidth: true
                                }

                                Text {
                                    text: "实时"
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

                        GridLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.margins: 10
                            columns: 2
                            columnSpacing: 8
                            rowSpacing: 8

                            MetricCard {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                theme: root.theme
                                labelText: "用时"
                                valueText: "00:00"
                                unitText: ".0 s"
                            }

                            MetricCard {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                theme: root.theme
                                labelText: "操作"
                                valueText: "0"
                                unitText: "次"
                            }

                            MetricCard {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                theme: root.theme
                                labelText: "识别"
                                valueText: "—"
                                unitText: "格/s"
                            }

                            MetricCard {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                theme: root.theme
                                labelText: "置信度"
                                valueText: "—"
                                unitText: "%"
                            }
                        }
                    }
                }

                SolverHintList {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    theme: root.theme
                }
            }
        }
    }
}
