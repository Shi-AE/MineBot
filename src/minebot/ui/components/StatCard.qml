import QtQuick
import QtQuick.Layouts

Panel {
    id: root

    property string labelText: ""
    property string valueText: "—"
    property string detailText: ""

    implicitHeight: 112

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 15
        spacing: 6

        Text {
            text: root.labelText
            color: root.theme.textMuted
            font.family: root.theme.fontFamily
            font.pixelSize: 10
        }

        Text {
            text: root.valueText
            color: root.theme.textPrimary
            font.family: root.theme.fontFamily
            font.pixelSize: 28
            font.weight: Font.Medium
            font.letterSpacing: -0.7
        }

        Text {
            text: root.detailText
            color: root.theme.textFaint
            font.family: root.theme.fontFamily
            font.pixelSize: 9
        }
    }
}
