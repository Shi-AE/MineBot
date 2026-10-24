import QtQuick

Rectangle {
    required property Theme theme

    property color fillColor: theme.surface
    property color strokeColor: theme.borderColor

    radius: 14
    color: fillColor
    border.width: 1
    border.color: strokeColor
}
