import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "pages"

ApplicationWindow {
    id: root

    required property var appSettings

    property int currentPage: 0

    signal startRequested()

    readonly property var pageSections: ["任务控制", "实时数据", "设置"]
    readonly property var pageTitles: ["任务控制", "实时数据", "偏好设置"]

    width: 1120
    height: 760
    minimumWidth: 980
    minimumHeight: 700
    visible: true
    color: appTheme.pageBackground
    title: "MineBot"
    font.family: appTheme.fontFamily

    Theme {
        id: appTheme
        settings: root.appSettings
    }

    Rectangle {
        anchors.fill: parent
        color: appTheme.pageBackground

        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.lighter(appTheme.pageBackground, 1.12) }
            GradientStop { position: 0.42; color: appTheme.pageBackground }
            GradientStop { position: 1.0; color: Qt.darker(appTheme.pageBackground, 1.12) }
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        NavSidebar {
            Layout.fillHeight: true
            Layout.preferredWidth: 204
            theme: appTheme
            currentPage: root.currentPage
            onPageRequested: (page) => root.currentPage = page
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: appTheme.appBackground

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                AppHeader {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 84
                    theme: appTheme
                    sectionText: root.pageSections[root.currentPage]
                    titleText: root.pageTitles[root.currentPage]
                    onStartRequested: root.startRequested()
                    onSettingsRequested: root.currentPage = 2
                }

                StackLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.margins: 25
                    currentIndex: root.currentPage

                    ControlPage {
                        theme: appTheme
                        objectName: "controlPage"
                    }

                    DataPage {
                        theme: appTheme
                        objectName: "dataPage"
                    }

                    SettingsPage {
                        theme: appTheme
                        objectName: "settingsPage"
                    }
                }
            }
        }
    }
}
