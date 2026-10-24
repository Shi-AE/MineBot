import QtQuick

QtObject {
    id: root

    required property var settings

    readonly property var colors: root.settings.colors
    readonly property var generalValues: root.settings.general
    readonly property string fontFamily: "Microsoft YaHei UI"
    readonly property string monoFontFamily: "Consolas"
    readonly property string configPath: root.settings.config_path
    readonly property bool windowAlwaysOnTop: root.generalValues["WindowAlwaysOnTop"]
    readonly property bool preserveDashboard: root.generalValues["PreserveDashboard"]
    readonly property bool regionMaskVisible: root.generalValues["RegionMaskVisible"]
    readonly property real regionMaskOpacity: root.settings.region_mask_opacity

    readonly property color accent: root.colors["Accent"]
    readonly property color accentText: root.colors["AccentText"]
    readonly property color pageBackground: root.colors["PageBackground"]
    readonly property color appBackground: root.colors["AppBackground"]
    readonly property color surface: root.colors["Surface"]
    readonly property color surfaceAlt: root.colors["SurfaceAlt"]
    readonly property color sidebarTop: root.colors["SidebarTop"]
    readonly property color sidebarBottom: root.colors["SidebarBottom"]
    readonly property color borderColor: root.colors["Border"]
    readonly property color borderStrong: root.colors["BorderStrong"]
    readonly property color textPrimary: root.colors["TextPrimary"]
    readonly property color textMuted: root.colors["TextMuted"]
    readonly property color textFaint: root.colors["TextFaint"]
    readonly property color danger: root.colors["Danger"]
    readonly property color dangerSoft: root.colors["DangerSoft"]
    readonly property color success: root.colors["Success"]
    readonly property color warning: root.colors["Warning"]
    readonly property color accentSoft: Qt.rgba(root.accent.r, root.accent.g, root.accent.b, 0.13)

    readonly property var themePresets: [
        {name: "青蓝", value: "#4bd4de"},
        {name: "湖绿", value: "#63d9b0"},
        {name: "琥珀", value: "#f1b95e"},
        {name: "珊瑚", value: "#ff8b93"},
        {name: "紫罗兰", value: "#b8a1ff"}
    ]

    function setAccent(value) {
        root.settings.set_color("Accent", value);
    }

    function setGeneral(key, value) {
        root.settings.set_general(key, value);
    }

    function setRegionMaskOpacity(value) {
        root.settings.set_region_mask_opacity(value);
    }

    function themeName(colorValue) {
        for (let index = 0; index < root.themePresets.length; index += 1) {
            if (root.themePresets[index].value === colorValue.toString())
                return root.themePresets[index].name;
        }
        return "自定义";
    }
}
