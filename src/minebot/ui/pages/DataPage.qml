import QtQuick
import QtQuick.Layouts
import "../components"

Item {
    id: root

    required property Theme theme

    ColumnLayout {
        anchors.fill: parent
        spacing: 14

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 3

            Text {
                text: "实时数据"
                color: root.theme.textPrimary
                font.family: root.theme.fontFamily
                font.pixelSize: 17
                font.weight: Font.DemiBold
            }

            Text {
                text: "任务开始后展示识别与操作指标，当前预留稳定布局。"
                color: root.theme.textMuted
                font.family: root.theme.fontFamily
                font.pixelSize: 10
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            StatCard {
                Layout.fillWidth: true
                theme: root.theme
                labelText: "任务用时"
                valueText: "00:00"
                detailText: "本次任务"
            }

            StatCard {
                Layout.fillWidth: true
                theme: root.theme
                labelText: "已处理格子"
                valueText: "—"
                detailText: "当前识别范围"
            }

            StatCard {
                Layout.fillWidth: true
                theme: root.theme
                labelText: "识别延迟"
                valueText: "—"
                detailText: "毫秒"
            }

            StatCard {
                Layout.fillWidth: true
                theme: root.theme
                labelText: "异常操作"
                valueText: "0"
                detailText: "本次任务"
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 12

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

                        Text {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: 16
                            text: "识别延迟趋势"
                            color: root.theme.textPrimary
                            font.family: root.theme.fontFamily
                            font.pixelSize: 11
                            font.weight: Font.DemiBold
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
                        Layout.margins: 16
                        radius: 9
                        color: root.theme.surfaceAlt
                        clip: true

                        GridBackdrop {
                            anchors.fill: parent
                            lineColor: root.theme.borderColor
                            cellSize: 42
                        }

                        Rectangle {
                            anchors.centerIn: parent
                            width: 200
                            height: 48
                            radius: 8
                            color: root.theme.surfaceAlt

                            Text {
                                anchors.centerIn: parent
                                text: "任务开始后生成趋势\n预留延迟与帧率时间轴"
                                color: root.theme.textFaint
                                font.family: root.theme.fontFamily
                                font.pixelSize: 10
                                horizontalAlignment: Text.AlignHCenter
                                lineHeight: 1.5
                            }
                        }
                    }
                }
            }

            Panel {
                Layout.fillHeight: true
                Layout.preferredWidth: 320
                theme: root.theme

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 48
                        color: "transparent"

                        Text {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: 16
                            text: "最近任务"
                            color: root.theme.textPrimary
                            font.family: root.theme.fontFamily
                            font.pixelSize: 11
                            font.weight: Font.DemiBold
                        }

                        Text {
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.rightMargin: 16
                            text: "最多 50 条"
                            color: root.theme.textFaint
                            font.family: root.theme.fontFamily
                            font.pixelSize: 9
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
                        Layout.margins: 16
                        radius: 9
                        color: root.theme.surfaceAlt
                        border.width: 1
                        border.color: root.theme.borderColor

                        Text {
                            anchors.centerIn: parent
                            width: parent.width - 32
                            text: "暂无任务记录\n完成后在这里显示结果摘要"
                            color: root.theme.textFaint
                            font.family: root.theme.fontFamily
                            font.pixelSize: 9
                            horizontalAlignment: Text.AlignHCenter
                            lineHeight: 1.5
                        }
                    }
                }
            }
        }
    }
}
