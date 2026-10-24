import QtQuick
import QtQuick.Layouts

Panel {
    id: root

    property string labelText: ""
    property string valueText: "—"
    property string unitText: ""

    implicitHeight: 82

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 6

        Text {
            text: root.labelText
            color: root.theme.textMuted
            font.family: root.theme.fontFamily
            font.pixelSize: 10
            Layout.fillWidth: true
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 3

            Text {
                text: root.valueText
                color: root.theme.textPrimary
                font.family: root.theme.fontFamily
                font.pixelSize: 20
                font.weight: Font.Medium
                font.letterSpacing: -0.4
            }

            Text {
                visible: root.unitText.length > 0
                text: root.unitText
                color: root.theme.textFaint
                font.family: root.theme.fontFamily
                font.pixelSize: 9
                Layout.alignment: Qt.AlignBottom
                Layout.bottomMargin: 3
            }
        }
    }
}
