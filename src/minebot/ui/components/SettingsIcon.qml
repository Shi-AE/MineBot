pragma ComponentBehavior: Bound

import QtQuick

Item {
    id: root

    property color iconColor: "transparent"

    implicitWidth: 16
    implicitHeight: 16

    Repeater {
        model: 8

        Rectangle {
            required property int index

            width: 2
            height: 4
            radius: 1
            rotation: index * 45
            x: root.width / 2 - width / 2 + Math.sin(index * Math.PI / 4) * 5
            y: root.height / 2 - height / 2 - Math.cos(index * Math.PI / 4) * 5
            color: root.iconColor
        }
    }

    Rectangle {
        width: 11
        height: 11
        radius: 5.5
        anchors.centerIn: parent
        color: "transparent"
        border.width: 1.4
        border.color: root.iconColor
    }
}
