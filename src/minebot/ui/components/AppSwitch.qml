import QtQuick
import QtQuick.Controls

Switch {
    id: root

    required property Theme theme

    implicitWidth: 38
    implicitHeight: 22
    padding: 0

    indicator: Rectangle {
        implicitWidth: 36
        implicitHeight: 21
        x: 1
        y: 0.5
        radius: 11
        color: root.checked ? root.theme.accent : root.theme.borderStrong

        Rectangle {
            width: 15
            height: 15
            radius: 8
            x: root.checked ? 18 : 3
            y: 3
            color: "#ffffff"

            Behavior on x {
                NumberAnimation { duration: 140 }
            }
        }
    }

    contentItem: Item {}
    background: Item {}
}
