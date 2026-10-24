import QtQuick
import QtQuick.Controls

Button {
    id: root

    required property Theme theme

    property color fillColor: theme.accent
    property color foreground: theme.accentText
    property bool outlined: false
    property bool dangerous: false

    implicitWidth: Math.max(78, contentItem.implicitWidth + 28)
    implicitHeight: 38
    hoverEnabled: true
    leftPadding: 14
    rightPadding: 14

    contentItem: Text {
        text: root.text
        color: root.enabled ? root.foreground : root.theme.textFaint
        font.family: root.theme.fontFamily
        font.pixelSize: 12
        font.weight: Font.DemiBold
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        anchors.centerIn: parent
    }

    background: Rectangle {
        radius: 10
        color: {
            if (!root.enabled)
                return root.theme.surfaceAlt;
            if (root.outlined)
                return root.hovered ? root.theme.accentSoft : "transparent";
            return root.hovered ? Qt.lighter(root.fillColor, 1.08) : root.fillColor;
        }
        border.width: root.outlined || !root.enabled ? 1 : 0
        border.color: {
            if (root.dangerous)
                return root.theme.dangerSoft;
            if (!root.enabled)
                return root.theme.borderColor;
            return root.outlined ? root.theme.borderStrong : root.fillColor;
        }
    }
}
