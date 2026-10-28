pragma ComponentBehavior: Bound

import QtQuick

// 使用识别快照的归一化网格边界，把求解提示叠加到蒙版窗口。
// 每格只显示一个提示：待执行时四角括线呼吸；详情面板选中显示
// 静态边框加一次扩散脉冲，两种动画保持可区分。
Item {
    id: root

    required property Theme theme
    required property var geometry
    required property var hints
    required property var selectedHint

    readonly property var columnEdges: geometry.column_edges || []
    readonly property var rowEdges: geometry.row_edges || []
    readonly property string hintAssetRoot: Qt.resolvedUrl("../assets/hints/")
    readonly property var cellKinds: {
        const kinds = ({});
        const cells = root.geometry.cells || [];
        for (let index = 0; index < cells.length; index += 1) {
            const cell = cells[index];
            kinds[cell.row + ":" + cell.column] = cell.kind;
        }
        return kinds;
    }
    readonly property int selectedRow: root.selectedHint.row !== undefined
        ? root.selectedHint.row
        : -1
    readonly property int selectedColumn: root.selectedHint.column !== undefined
        ? root.selectedHint.column
        : -1

    function bestOption(hint) {
        let best = hint.options[0];
        for (let index = 1; index < hint.options.length; index += 1) {
            if (hint.options[index].probability > best.probability)
                best = hint.options[index];
        }
        return best;
    }

    function isFlagKind(kind) {
        return typeof kind === "string" && kind.indexOf("FLAG_") === 0;
    }

    function currentKind(hint) {
        return root.cellKinds[hint.row + ":" + hint.column] || "";
    }

    Repeater {
        model: root.hints

        Item {
            id: hintCell
            required property var modelData
            readonly property var best: root.bestOption(modelData)
            readonly property bool selected:
                root.selectedRow === modelData.row
                && root.selectedColumn === modelData.column
            readonly property string observedKind: root.currentKind(modelData)
            readonly property bool alreadyApplied:
                hintCell.best.kind !== "OPEN"
                && hintCell.observedKind === hintCell.best.kind
            readonly property bool replaceFlag:
                root.isFlagKind(hintCell.best.kind)
                && root.isFlagKind(hintCell.observedKind)
                && hintCell.observedKind !== hintCell.best.kind
            readonly property bool showHint: !hintCell.alreadyApplied
            readonly property color bracketColor:
                hintCell.replaceFlag ? root.theme.warning : root.theme.success
            readonly property real bracketLength: Math.max(
                3,
                Math.min(7, Math.min(hintCell.width, hintCell.height) * 0.32)
            )
            readonly property real bracketThickness: Math.max(
                1,
                Math.min(2.5, Math.min(hintCell.width, hintCell.height) * 0.08)
            )

            readonly property int column: modelData.column
            readonly property int row: modelData.row
            readonly property real cellX: root.columnEdges[column] * root.width
            readonly property real cellY: root.rowEdges[row] * root.height
            readonly property real cellWidth:
                (root.columnEdges[column + 1] - root.columnEdges[column])
                * root.width
            readonly property real cellHeight:
                (root.rowEdges[row + 1] - root.rowEdges[row])
                * root.height

            visible: column >= 0
                && column < root.columnEdges.length - 1
                && row >= 0
                && row < root.rowEdges.length - 1
            x: cellX
            y: cellY
            width: cellWidth
            height: cellHeight

            Item {
                id: hintBrackets

                anchors.fill: parent
                visible: hintCell.showHint
                opacity: 1

                SequentialAnimation on opacity {
                    running: hintCell.showHint
                    loops: Animation.Infinite
                    NumberAnimation {
                        from: 1.0
                        to: 0.5
                        duration: 850
                        easing.type: Easing.InOutQuad
                    }
                    NumberAnimation {
                        from: 0.5
                        to: 1.0
                        duration: 850
                        easing.type: Easing.InOutQuad
                    }
                }

                Rectangle {
                    width: hintCell.bracketLength
                    height: hintCell.bracketThickness
                    color: hintCell.bracketColor
                }
                Rectangle {
                    width: hintCell.bracketThickness
                    height: hintCell.bracketLength
                    color: hintCell.bracketColor
                }
                Rectangle {
                    x: parent.width - width
                    width: hintCell.bracketLength
                    height: hintCell.bracketThickness
                    color: hintCell.bracketColor
                }
                Rectangle {
                    x: parent.width - width
                    width: hintCell.bracketThickness
                    height: hintCell.bracketLength
                    color: hintCell.bracketColor
                }
                Rectangle {
                    y: parent.height - height
                    width: hintCell.bracketLength
                    height: hintCell.bracketThickness
                    color: hintCell.bracketColor
                }
                Rectangle {
                    y: parent.height - height
                    width: hintCell.bracketThickness
                    height: hintCell.bracketLength
                    color: hintCell.bracketColor
                }
                Rectangle {
                    x: parent.width - width
                    y: parent.height - height
                    width: hintCell.bracketLength
                    height: hintCell.bracketThickness
                    color: hintCell.bracketColor
                }
                Rectangle {
                    x: parent.width - width
                    y: parent.height - height
                    width: hintCell.bracketThickness
                    height: hintCell.bracketLength
                    color: hintCell.bracketColor
                }
            }

            Rectangle {
                anchors.centerIn: parent
                width: Math.max(3, Math.min(8, hintCell.width * 0.22))
                height: width
                radius: width / 2
                visible: hintCell.showHint && hintCell.best.kind === "OPEN"
                color: root.theme.success
            }

            Image {
                anchors.centerIn: parent
                width: Math.min(hintCell.width, hintCell.height) * 0.72
                height: width
                visible: hintCell.showHint && hintCell.best.kind !== "OPEN"
                source: root.hintAssetRoot + hintCell.best.kind + ".png"
                fillMode: Image.PreserveAspectFit
                smooth: false
                mipmap: false
            }

            Rectangle {
                id: selectionFrame

                anchors.fill: parent
                anchors.margins: -1
                visible: hintCell.selected
                color: "transparent"
                border.width: 2
                border.color: root.theme.accent
                opacity: 0.9
            }

            Rectangle {
                id: selectionPulse

                anchors.fill: parent
                anchors.margins: -2
                visible: hintCell.selected
                color: "transparent"
                border.width: 2
                border.color: root.theme.accent
                opacity: 0

                SequentialAnimation {
                    running: hintCell.selected
                    loops: 1
                    ParallelAnimation {
                        NumberAnimation {
                            target: selectionPulse
                            property: "scale"
                            from: 0.9
                            to: 1.45
                            duration: 650
                            easing.type: Easing.OutCubic
                        }
                        NumberAnimation {
                            target: selectionPulse
                            property: "opacity"
                            from: 1.0
                            to: 0.0
                            duration: 650
                            easing.type: Easing.OutCubic
                        }
                    }
                }
            }

            Text {
                anchors.bottom: parent.bottom
                anchors.right: parent.right
                anchors.bottomMargin: 1
                anchors.rightMargin: 1
                visible: hintCell.showHint
                    && hintCell.best.probability < 0.999999
                text: Math.round(hintCell.best.probability * 100) + "%"
                color: root.theme.warning
                style: Text.Outline
                styleColor: "#F0081118"
                font.family: root.theme.monoFontFamily
                font.pixelSize: Math.max(
                    6,
                    Math.min(9, hintCell.height * 0.4)
                )
                font.weight: Font.Bold
            }
        }
    }
}
