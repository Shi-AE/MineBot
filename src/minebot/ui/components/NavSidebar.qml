import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root

    required property Theme theme
    property int currentPage: 0

    signal pageRequested(int page)

    implicitWidth: 204

    gradient: Gradient {
        GradientStop { position: 0.0; color: root.theme.sidebarTop }
        GradientStop { position: 0.34; color: Qt.darker(root.theme.sidebarTop, 1.12) }
        GradientStop { position: 1.0; color: root.theme.sidebarBottom }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 2

        RowLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 8
            Layout.rightMargin: 8
            Layout.topMargin: 8
            Layout.bottomMargin: 24
            spacing: 11

            Rectangle {
                Layout.preferredWidth: 38
                Layout.preferredHeight: 38
                radius: 13
                color: root.theme.accentSoft
                border.width: 1
                border.color: Qt.rgba(root.theme.accent.r, root.theme.accent.g, root.theme.accent.b, 0.32)

                Text {
                    anchors.centerIn: parent
                    text: "M"
                    color: root.theme.accent
                    font.family: root.theme.fontFamily
                    font.pixelSize: 19
                    font.weight: Font.Bold
                }

                Rectangle {
                    width: 6
                    height: 6
                    radius: 3
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.rightMargin: 6
                    anchors.bottomMargin: 6
                    color: root.theme.success
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 1

                Text {
                    text: "MineBot"
                    color: root.theme.textPrimary
                    font.family: root.theme.fontFamily
                    font.pixelSize: 17
                    font.weight: Font.DemiBold
                    font.letterSpacing: -0.2
                }

                Text {
                    text: "扫雷自动化控制台"
                    color: root.theme.textMuted
                    font.family: root.theme.fontFamily
                    font.pixelSize: 9
                    font.letterSpacing: 0.5
                }
            }
        }

        Text {
            Layout.leftMargin: 11
            Layout.bottomMargin: 8
            text: "工作区"
            color: root.theme.textFaint
            font.family: root.theme.fontFamily
            font.pixelSize: 9
            font.weight: Font.DemiBold
            font.letterSpacing: 1.2
        }

        NavButton {
            Layout.fillWidth: true
            theme: root.theme
            text: "任务控制"
            glyph: "01"
            selected: root.currentPage === 0
            onClicked: root.pageRequested(0)
            objectName: "controlNavButton"
        }

        NavButton {
            Layout.fillWidth: true
            theme: root.theme
            text: "实时数据"
            glyph: "02"
            selected: root.currentPage === 1
            onClicked: root.pageRequested(1)
            objectName: "dataNavButton"
        }

        NavButton {
            Layout.fillWidth: true
            theme: root.theme
            text: "设置"
            glyph: "03"
            selected: root.currentPage === 2
            onClicked: root.pageRequested(2)
            objectName: "settingsNavButton"
        }

        Item { Layout.fillHeight: true }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 64
            radius: 12
            color: root.theme.surfaceAlt
            border.width: 1
            border.color: root.theme.borderColor

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 4

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 7

                    Rectangle {
                        width: 7
                        height: 7
                        radius: 4
                        color: root.theme.warning
                    }

                    Text {
                        text: "自动扫雷模块待接入"
                        color: root.theme.textPrimary
                        font.family: root.theme.fontFamily
                        font.pixelSize: 10
                        font.weight: Font.DemiBold
                    }
                }

                Text {
                    text: "当前仅展示界面框架"
                    color: root.theme.textMuted
                    font.family: root.theme.fontFamily
                    font.pixelSize: 9
                }
            }
        }

        Text {
            Layout.fillWidth: true
            Layout.topMargin: 3
            text: "MineBot 0.1.0"
            color: root.theme.textFaint
            font.family: root.theme.fontFamily
            font.pixelSize: 9
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
