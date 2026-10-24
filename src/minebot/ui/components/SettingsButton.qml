import QtQuick
import QtQuick.Controls

Button {
    id: root

    required property Theme theme

    implicitWidth: 38
    implicitHeight: 38
    hoverEnabled: true
    Accessible.name: "设置"

    contentItem: SettingsIcon {
        anchors.centerIn: parent
        width: 16
        height: 16
        iconColor: root.hovered ? root.theme.textPrimary : root.theme.textMuted
    }

    background: Rectangle {
        radius: 10
        color: root.theme.surface
        border.width: 1
        border.color: root.hovered ? root.theme.borderStrong : root.theme.borderColor
    }
}
