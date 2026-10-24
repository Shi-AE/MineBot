pragma
ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
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
                text: "设置"
                color: root.theme.textPrimary
                font.family: root.theme.fontFamily
                font.pixelSize: 17
                font.weight: Font.DemiBold
            }

            Text {
                text: "设置修改后会立即保存到用户配置目录，无需手动点击保存。"
                color: root.theme.textMuted
                font.family: root.theme.fontFamily
                font.pixelSize: 10
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 12

            Panel {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: 650
                theme: root.theme

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.margins: 18
                        spacing: 5

                        Text {
                            text: "外观"
                            color: root.theme.textPrimary
                            font.family: root.theme.fontFamily
                            font.pixelSize: 12
                            font.weight: Font.DemiBold
                        }

                        Text {
                            text: "选择控制台强调色，当前仅在本次运行中预览。"
                            color: root.theme.textMuted
                            font.family: root.theme.fontFamily
                            font.pixelSize: 9
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: root.theme.borderColor
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.margins: 18
                        spacing: 13

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            Text {
                                text: "主题配色"
                                color: root.theme.textPrimary
                                font.family: root.theme.fontFamily
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                            }

                            Text {
                                text: "当前选择：" + root.theme.themeName(root.theme.accent)
                                color: root.theme.textFaint
                                font.family: root.theme.fontFamily
                                font.pixelSize: 9
                                Layout.fillWidth: true
                            }
                        }

                        Row {
                            spacing: 8

                            Repeater {
                                model: root.theme.themePresets

                                Button {
                                    id: themeButton

                                    required property var modelData

                                    width: 80
                                    height: 42
                                    hoverEnabled: true
                                    text: modelData["name"]

                                    contentItem: Row {
                                        anchors.centerIn: parent
                                        spacing: 7

                                        Rectangle {
                                            width: 14
                                            height: 14
                                            radius: 7
                                            color: themeButton.modelData["value"]
                                            anchors.verticalCenter: parent.verticalCenter
                                        }

                                        Text {
                                            text: themeButton.text
                                            color: root.theme.accent === themeButton.modelData["value"]
                                                ? root.theme.textPrimary
                                                : root.theme.textMuted
                                            font.family: root.theme.fontFamily
                                            font.pixelSize: 10
                                            font.weight: root.theme.accent === themeButton.modelData["value"]
                                                ? Font.DemiBold
                                                : Font.Normal
                                            anchors.verticalCenter: parent.verticalCenter
                                        }
                                    }

                                    background: Rectangle {
                                        radius: 9
                                        color: themeButton.hovered ? root.theme.surface : root.theme.surfaceAlt
                                        border.width: 1
                                        border.color: root.theme.accent === themeButton.modelData["value"]
                                            ? themeButton.modelData["value"]
                                            : root.theme.borderColor
                                    }

                                    onClicked: root.theme.setAccent(modelData["value"])
                                }
                            }
                        }

                        Text {
                            text: "选择预设会立即写入 Accent 色值；完整色板可在配置文件中手动调整。"
                            color: root.theme.textFaint
                            font.family: root.theme.fontFamily
                            font.pixelSize: 9
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: root.theme.borderColor
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.margins: 18
                        spacing: 0

                        Text {
                            Layout.bottomMargin: 10
                            text: "通用"
                            color: root.theme.textPrimary
                            font.family: root.theme.fontFamily
                            font.pixelSize: 12
                            font.weight: Font.DemiBold
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 50
                            spacing: 16

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2

                                Text {
                                    text: "运行时窗口置顶"
                                    color: root.theme.textPrimary
                                    font.family: root.theme.fontFamily
                                    font.pixelSize: 11
                                }

                                Text {
                                    text: "方便观察目标窗口与任务状态。"
                                    color: root.theme.textMuted
                                    font.family: root.theme.fontFamily
                                    font.pixelSize: 9
                                }
                            }

                            AppSwitch {
                                theme: root.theme
                                checked: root.theme.windowAlwaysOnTop
                                onToggled: root.theme.setGeneral("WindowAlwaysOnTop", checked)
                                Accessible.name: "运行时窗口置顶"
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: root.theme.borderColor
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 50
                            spacing: 16

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2

                                Text {
                                    text: "结束后保留数据看板"
                                    color: root.theme.textPrimary
                                    font.family: root.theme.fontFamily
                                    font.pixelSize: 11
                                }

                                Text {
                                    text: "切换页面时不清空本次任务数据。"
                                    color: root.theme.textMuted
                                    font.family: root.theme.fontFamily
                                    font.pixelSize: 9
                                }
                            }

                            AppSwitch {
                                theme: root.theme
                                checked: root.theme.preserveDashboard
                                onToggled: root.theme.setGeneral("PreserveDashboard", checked)
                                Accessible.name: "结束后保留数据看板"
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: root.theme.borderColor
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 50
                            spacing: 16

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2

                                Text {
                                    text: "显示区域蒙版"
                                    color: root.theme.textPrimary
                                    font.family: root.theme.fontFamily
                                    font.pixelSize: 11
                                }

                                Text {
                                    text: "关闭后仍保留可调整的外框。"
                                    color: root.theme.textMuted
                                    font.family: root.theme.fontFamily
                                    font.pixelSize: 9
                                }
                            }

                            AppSwitch {
                                theme: root.theme
                                checked: root.theme.regionMaskVisible
                                onToggled: root.theme.setGeneral("RegionMaskVisible", checked)
                                Accessible.name: "显示区域蒙版"
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: root.theme.borderColor
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 68
                            spacing: 2

                            RowLayout {
                                Layout.fillWidth: true

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2

                                    Text {
                                        text: "捕获频率"
                                        color: root.theme.textPrimary
                                        font.family: root.theme.fontFamily
                                        font.pixelSize: 11
                                    }

                                    Text {
                                        text: "拖动调整，步长 0.1 次/秒。"
                                        color: root.theme.textMuted
                                        font.family: root.theme.fontFamily
                                        font.pixelSize: 9
                                    }
                                }

                                Text {
                                    text: captureFrequencySlider.value.toFixed(1) + " FPS"
                                    color: root.theme.accent
                                    font.family: root.theme.monoFontFamily
                                    font.pixelSize: 10
                                    font.weight: Font.DemiBold
                                }
                            }

                            Slider {
                                id: captureFrequencySlider

                                Layout.fillWidth: true
                                implicitHeight: 20
                                from: 0.1
                                to: 10.0
                                stepSize: 0.1
                                value: root.theme.captureFrequency
                                Accessible.name: "捕获频率"

                                onPressedChanged: {
                                    if (!pressed)
                                        root.theme.setCaptureFrequency(value);
                                }

                                onMoved: {
                                    if (!pressed)
                                        root.theme.setCaptureFrequency(value);
                                }

                                background: Rectangle {
                                    x: 0
                                    y: (captureFrequencySlider.height - height) / 2
                                    width: captureFrequencySlider.width
                                    height: 4
                                    radius: 2
                                    color: root.theme.borderColor

                                    Rectangle {
                                        width: parent.width * captureFrequencySlider.visualPosition
                                        height: parent.height
                                        radius: parent.radius
                                        color: root.theme.accent
                                    }
                                }

                                handle: Rectangle {
                                    x: captureFrequencySlider.visualPosition
                                        * (captureFrequencySlider.width - width)
                                    y: (captureFrequencySlider.height - height) / 2
                                    width: 16
                                    height: 16
                                    radius: 8
                                    color: root.theme.accent
                                    border.width: 2
                                    border.color: root.theme.surface
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: root.theme.borderColor
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 68
                            spacing: 2

                            RowLayout {
                                Layout.fillWidth: true

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2

                                    Text {
                                        text: "蒙版不透明度"
                                        color: root.theme.textPrimary
                                        font.family: root.theme.fontFamily
                                        font.pixelSize: 11
                                    }

                                    Text {
                                        text: "数值越低越透明，外框不受影响。"
                                        color: root.theme.textMuted
                                        font.family: root.theme.fontFamily
                                        font.pixelSize: 9
                                    }
                                }

                                Text {
                                    text: Math.round(root.theme.regionMaskOpacity * 100) + "%"
                                    color: root.theme.accent
                                    font.family: root.theme.monoFontFamily
                                    font.pixelSize: 10
                                    font.weight: Font.DemiBold
                                }
                            }

                            Slider {
                                id: maskOpacitySlider

                                Layout.fillWidth: true
                                implicitHeight: 20
                                from: 0
                                to: 1
                                stepSize: 0.01
                                value: root.theme.regionMaskOpacity
                                onMoved: root.theme.setRegionMaskOpacity(value)
                                Accessible.name: "蒙版不透明度"

                                background: Rectangle {
                                    x: 0
                                    y: (maskOpacitySlider.height - height) / 2
                                    width: maskOpacitySlider.width
                                    height: 4
                                    radius: 2
                                    color: root.theme.borderColor

                                    Rectangle {
                                        width: parent.width * maskOpacitySlider.visualPosition
                                        height: parent.height
                                        radius: parent.radius
                                        color: root.theme.accent
                                    }
                                }

                                handle: Rectangle {
                                    x: maskOpacitySlider.visualPosition
                                        * (maskOpacitySlider.width - width)
                                    y: (maskOpacitySlider.height - height) / 2
                                    width: 16
                                    height: 16
                                    radius: 8
                                    color: root.theme.accent
                                    border.width: 2
                                    border.color: root.theme.surface
                                }
                            }
                        }
                    }
                }
            }

            Panel {
                Layout.fillHeight: true
                Layout.preferredWidth: 300
                theme: root.theme

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    Text {
                        text: "设置范围"
                        color: root.theme.textPrimary
                        font.family: root.theme.fontFamily
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                    }

                    Text {
                        text: "颜色使用具体十六进制值保存，配置文件内置各字段说明。"
                        color: root.theme.textMuted
                        font.family: root.theme.fontFamily
                        font.pixelSize: 10
                        wrapMode: Text.WordWrap
                        lineHeight: 1.5
                        Layout.fillWidth: true
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: root.theme.borderColor
                    }

                    Repeater {
                        model: [
                            "窗口与显示",
                            "识别与操作",
                            "快捷键",
                            "数据与日志"
                        ]

                        Text {
                            required property string modelData

                            text: modelData
                            color: root.theme.textMuted
                            font.family: root.theme.fontFamily
                            font.pixelSize: 10
                            Layout.fillWidth: true
                        }
                    }

                    Text {
                        text: "配置文件"
                        color: root.theme.textFaint
                        font.family: root.theme.fontFamily
                        font.pixelSize: 9
                    }

                    Text {
                        text: root.theme.configPath
                        color: root.theme.textMuted
                        font.family: root.theme.monoFontFamily
                        font.pixelSize: 9
                        wrapMode: Text.WrapAnywhere
                        lineHeight: 1.35
                        Layout.fillWidth: true
                    }

                    Text {
                        text: "截图缓存"
                        color: root.theme.textFaint
                        font.family: root.theme.fontFamily
                        font.pixelSize: 9
                    }

                    Text {
                        text: root.theme.captureCachePath
                        color: root.theme.textMuted
                        font.family: root.theme.monoFontFamily
                        font.pixelSize: 9
                        wrapMode: Text.WrapAnywhere
                        lineHeight: 1.35
                        Layout.fillWidth: true
                    }

                    Item {
                        Layout.fillHeight: true
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        radius: 9
                        color: root.theme.accentSoft
                        border.width: 1
                        border.color: Qt.rgba(root.theme.accent.r, root.theme.accent.g, root.theme.accent.b, 0.28)

                        RowLayout {
                            anchors.centerIn: parent
                            spacing: 7

                            Rectangle {
                                width: 7
                                height: 7
                                radius: 4
                                color: root.theme.success
                            }

                            Text {
                                text: "修改后自动保存"
                                color: root.theme.accent
                                font.family: root.theme.fontFamily
                                font.pixelSize: 10
                                font.weight: Font.DemiBold
                            }
                        }
                    }
                }
            }
        }
    }
}
