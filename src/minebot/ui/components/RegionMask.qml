import QtQuick
import QtQuick.Window

Window {
    id: frameWindow
    objectName: "frameWindow"

    required property var controller
    required property var settings
    readonly property color accentColor: frameWindow.settings.colors["Accent"]

    property int edgeSize: 12
    readonly property int cornerRadius: 8

    width: 800
    height: 560
    minimumWidth: 320
    minimumHeight: 240
    visible: false
    color: "transparent"
    flags: Qt.Tool
        | Qt.FramelessWindowHint
        | Qt.WindowStaysOnTopHint

    function open() {
        maskWindow.visible = true;
        visible = true;
        raise();
        updateFrameShape();
    }

    function closeMask() {
        maskWindow.visible = false;
        visible = false;
    }

    function updateFrameShape() {
        Qt.callLater(function () {
            if (visible && width > 0 && height > 0)
                controller.apply_frame_region(frameWindow, edgeSize);
        });
    }

    function edgesAt(x, y) {
        const dragZoneHalfWidth = 48;
        if (y < edgeSize
            && x > width / 2 - dragZoneHalfWidth
            && x < width / 2 + dragZoneHalfWidth) {
            return 0;
        }

        let edges = 0;
        if (x < edgeSize)
            edges |= Qt.LeftEdge;
        if (x > width - edgeSize)
            edges |= Qt.RightEdge;
        if (y < edgeSize)
            edges |= Qt.TopEdge;
        if (y > height - edgeSize)
            edges |= Qt.BottomEdge;
        return edges;
    }

    function cursorForEdges(edges) {
        const horizontal = (edges & Qt.LeftEdge) || (edges & Qt.RightEdge);
        const vertical = (edges & Qt.TopEdge) || (edges & Qt.BottomEdge);
        if (horizontal && vertical)
            return ((edges & Qt.LeftEdge) && (edges & Qt.TopEdge))
                || ((edges & Qt.RightEdge) && (edges & Qt.BottomEdge))
                ? Qt.SizeFDiagCursor
                : Qt.SizeBDiagCursor;
        if (horizontal)
            return Qt.SizeHorCursor;
        if (vertical)
            return Qt.SizeVerCursor;
        return Qt.SizeAllCursor;
    }

    Component.onCompleted: {
        if (screen) {
            x = Math.round((screen.width - width) / 2);
            y = Math.round((screen.height - height) / 2);
        }
    }

    onWidthChanged: updateFrameShape()
    onHeightChanged: updateFrameShape()

    Rectangle {
        anchors.fill: parent
        color: "transparent"
        border.width: 2
        border.color: frameWindow.accentColor
        radius: frameWindow.cornerRadius
    }

    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 5
        width: 48
        height: 3
        radius: 1.5
        color: frameWindow.accentColor
    }

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton
        hoverEnabled: true

        onPressed: function (mouse) {
            const edges = frameWindow.edgesAt(mouse.x, mouse.y);
            if (edges === 0)
                frameWindow.startSystemMove();
            else
                frameWindow.startSystemResize(edges);
        }

        onPositionChanged: function (mouse) {
            cursorShape = frameWindow.cursorForEdges(
                frameWindow.edgesAt(mouse.x, mouse.y)
            );
        }
    }

    Window {
        id: maskWindow
        objectName: "maskWindow"

        x: frameWindow.x
        y: frameWindow.y
        width: frameWindow.width
        height: frameWindow.height
        visible: false
        color: "transparent"
        flags: Qt.Tool
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.WindowTransparentForInput
            | Qt.WindowDoesNotAcceptFocus

        Item {
            anchors.fill: parent
            visible: frameWindow.settings.general["RegionMaskVisible"]
            opacity: frameWindow.settings.region_mask_opacity

            Rectangle {
                anchors.fill: parent
                radius: frameWindow.cornerRadius
                color: frameWindow.accentColor
            }
        }
    }
}
