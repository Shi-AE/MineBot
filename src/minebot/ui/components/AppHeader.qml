import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    required property Theme theme

    property string sectionText: ""
    property string titleText: ""

    signal startRequested()

    signal stopRequested()

    signal settingsRequested()

    implicitHeight: 84
    color: Qt.rgba(root.theme.appBackground.r, root.theme.appBackground.g, root.theme.appBackground.b, 0.9)

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 25
        anchors.rightMargin: 25
        spacing: 12

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2

            Text {
                text: "工作台 / " + root.sectionText
                color: root.theme.textFaint
                font.family: root.theme.fontFamily
                font.pixelSize: 9
                font.letterSpacing: 0.4
            }

            Text {
                text: root.titleText
                color: root.theme.textPrimary
                font.family: root.theme.fontFamily
                font.pixelSize: 20
                font.weight: Font.DemiBold
                font.letterSpacing: -0.4
            }
        }

        RowLayout {
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
            spacing: 8

            Rectangle {
                Layout.preferredWidth: 94
                Layout.preferredHeight: 30
                radius: 15
                color: root.theme.surface
                border.width: 1
                border.color: root.theme.borderColor

                RowLayout {
                    anchors.centerIn: parent
                    spacing: 7

                    Rectangle {
                        width: 7
                        height: 7
                        radius: 4
                        color: root.theme.warning
                    }

                    Text {
                        text: "功能待接入"
                        color: root.theme.textMuted
                        font.family: root.theme.fontFamily
                        font.pixelSize: 9
                    }
                }
            }

            ActionButton {
                theme: root.theme
                text: "开始"
                objectName: "startButton"
                onClicked: root.startRequested()

                ToolTip.visible: hovered
                ToolTip.text: "触发开始事件，自动扫雷功能待接入"
            }

            ActionButton {
                theme: root.theme
                text: "结束"
                outlined: true
                dangerous: true
                foreground: root.theme.danger
                fillColor: root.theme.dangerSoft
                objectName: "stopButton"
                onClicked: root.stopRequested()

                ToolTip.visible: hovered
                ToolTip.text: "关闭区域蒙版"
            }

            SettingsButton {
                theme: root.theme
                onClicked: root.settingsRequested()
                objectName: "settingsShortcutButton"

                ToolTip.visible: hovered
                ToolTip.text: "设置"
            }
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
