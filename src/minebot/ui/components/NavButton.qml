import QtQuick
import QtQuick.Controls

Button {
    id: root

    required property Theme theme

    property string glyph: ""
    property bool selected: false

    implicitHeight: 43
    hoverEnabled: true
    leftPadding: 12
    rightPadding: 12

    contentItem: Row {
        spacing: 10
        anchors.verticalCenter: parent.verticalCenter

        Text {
            text: root.glyph
            color: root.selected ? root.theme.textPrimary : root.theme.textMuted
            font.family: root.theme.monoFontFamily
            font.pixelSize: 10
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: root.text
            color: root.selected ? root.theme.textPrimary : root.theme.textMuted
            font.family: root.theme.fontFamily
            font.pixelSize: 12
            font.weight: root.selected ? Font.DemiBold : Font.Normal
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    background: Rectangle {
        radius: 11
        color: root.selected
            ? Qt.rgba(root.theme.accent.r, root.theme.accent.g, root.theme.accent.b, 0.16)
            : (root.hovered ? root.theme.surface : "transparent")

        Rectangle {
            visible: root.selected
            width: 2
            height: 19
            radius: 1
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            color: root.theme.accent
        }
    }
}
