pragma ComponentBehavior: Bound

import QtQuick

Item {
    id: root

    property color lineColor: "transparent"
    property int cellSize: 24

    Repeater {
        model: Math.ceil(root.width / Math.max(root.cellSize, 1)) + 1

        Rectangle {
            required property int index

            x: index * root.cellSize
            width: 1
            height: root.height
            color: root.lineColor
        }
    }

    Repeater {
        model: Math.ceil(root.height / Math.max(root.cellSize, 1)) + 1

        Rectangle {
            required property int index

            y: index * root.cellSize
            width: root.width
            height: 1
            color: root.lineColor
        }
    }
}
