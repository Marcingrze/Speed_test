import QtQuick 2.15
import QtQuick.Layouts 1.15
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.plasmoid 2.0
import org.kde.plasma.components 3.0 as PlasmaComponents3
import org.kde.kirigami 2.20 as Kirigami

PlasmoidItem {
    id: root

    // Size hints
    Plasmoid.backgroundHints: PlasmaCore.Types.DefaultBackground | PlasmaCore.Types.ConfigurableBackground
    preferredRepresentation: fullRepresentation

    width: Kirigami.Units.gridUnit * 18
    height: Kirigami.Units.gridUnit * 12

    // Data properties
    property string downloadSpeed: "N/A"
    property string uploadSpeed: "N/A"
    property string pingLatency: "N/A"
    property string serverInfo: "No data"
    property string lastUpdate: "Never"
    property bool hasData: false
    property bool isRunning: false
    property bool networkConnected: true

    // Helper script path
    property string helperScript: Qt.resolvedUrl("../code/speedtest_helper.py").replace("file://", "")

    // Timer for auto-refresh
    Timer {
        id: refreshTimer
        interval: 30000  // 30 seconds
        running: true
        repeat: true
        onTriggered: loadLastResult()
    }

    // Load data on startup
    Component.onCompleted: {
        loadLastResult()
        checkNetwork()
    }

    // Functions
    function loadLastResult() {
        var process = PlasmaCore.DataSource
        executeCommand("python3", [helperScript, "get_last"], function(output) {
            try {
                var result = JSON.parse(output)
                if (result.status === "success") {
                    downloadSpeed = result.download + " Mbps"
                    uploadSpeed = result.upload + " Mbps"
                    pingLatency = result.ping + " ms"
                    serverInfo = result.server
                    lastUpdate = result.timestamp
                    hasData = true
                } else if (result.status === "no_data") {
                    serverInfo = result.message
                    hasData = false
                } else {
                    serverInfo = "Error: " + result.message
                    hasData = false
                }
            } catch (e) {
                serverInfo = "Parse error: " + e
                hasData = false
            }
        })
    }

    function runTest() {
        isRunning = true
        executeCommand("python3", [helperScript, "run_test"], function(output) {
            try {
                var result = JSON.parse(output)
                if (result.status === "success") {
                    // Wait a moment then reload results
                    Qt.callLater(function() {
                        isRunning = false
                        // Test takes time, so schedule refresh after delay
                        loadTimer.start()
                    })
                } else {
                    isRunning = false
                    serverInfo = "Error: " + result.message
                }
            } catch (e) {
                isRunning = false
                serverInfo = "Error: " + e
            }
        })
    }

    function checkNetwork() {
        executeCommand("python3", [helperScript, "check_network"], function(output) {
            try {
                var result = JSON.parse(output)
                networkConnected = result.connected || false
            } catch (e) {
                networkConnected = false
            }
        })
    }

    // Helper to execute command
    function executeCommand(program, args, callback) {
        var process = Qt.createQmlObject('
            import QtQuick 2.0
            import org.kde.plasma.core 2.0 as PlasmaCore
            PlasmaCore.DataSource {
                id: executable
                engine: "executable"
                connectedSources: []
                onNewData: {
                    var stdout = data["stdout"]
                    disconnectSource(sourceName)
                    callback(stdout)
                }
                function exec(cmd) {
                    connectSource(cmd)
                }
            }
        ', root);
        var cmd = program + " " + args.join(" ")
        process.exec(cmd)
    }

    // Timer to reload after test completes
    Timer {
        id: loadTimer
        interval: 60000  // Wait 60 seconds for test to complete
        running: false
        repeat: false
        onTriggered: {
            loadLastResult()
        }
    }

    // Main layout
    fullRepresentation: ColumnLayout {
        spacing: Kirigami.Units.smallSpacing

        // Header with title and refresh button
        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            Kirigami.Heading {
                level: 3
                text: "Speed Test"
                Layout.fillWidth: true
            }

            PlasmaComponents3.ToolButton {
                icon.name: "view-refresh"
                onClicked: loadLastResult()
                PlasmaComponents3.ToolTip {
                    text: "Refresh results"
                }
            }
        }

        // Network status indicator
        RowLayout {
            Layout.fillWidth: true
            visible: !networkConnected
            spacing: Kirigami.Units.smallSpacing

            Kirigami.Icon {
                source: "dialog-warning"
                width: Kirigami.Units.iconSizes.small
                height: width
            }

            PlasmaComponents3.Label {
                text: "No network connection"
                color: Kirigami.Theme.negativeTextColor
                font.pointSize: Kirigami.Theme.smallFont.pointSize
            }
        }

        // Separator
        Kirigami.Separator {
            Layout.fillWidth: true
        }

        // Results grid
        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            columns: 2
            columnSpacing: Kirigami.Units.largeSpacing
            rowSpacing: Kirigami.Units.smallSpacing

            // Download
            ColumnLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing

                PlasmaComponents3.Label {
                    text: "Download"
                    font.pointSize: Kirigami.Theme.smallFont.pointSize
                    color: Kirigami.Theme.disabledTextColor
                }

                PlasmaComponents3.Label {
                    text: root.downloadSpeed
                    font.pointSize: Kirigami.Theme.defaultFont.pointSize * 1.5
                    font.bold: true
                    color: hasData ? Kirigami.Theme.textColor : Kirigami.Theme.disabledTextColor
                }

                Kirigami.Icon {
                    source: "download"
                    width: Kirigami.Units.iconSizes.medium
                    height: width
                    color: Kirigami.Theme.highlightColor
                    Layout.alignment: Qt.AlignHCenter
                }
            }

            // Upload
            ColumnLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing

                PlasmaComponents3.Label {
                    text: "Upload"
                    font.pointSize: Kirigami.Theme.smallFont.pointSize
                    color: Kirigami.Theme.disabledTextColor
                }

                PlasmaComponents3.Label {
                    text: root.uploadSpeed
                    font.pointSize: Kirigami.Theme.defaultFont.pointSize * 1.5
                    font.bold: true
                    color: hasData ? Kirigami.Theme.textColor : Kirigami.Theme.disabledTextColor
                }

                Kirigami.Icon {
                    source: "upload"
                    width: Kirigami.Units.iconSizes.medium
                    height: width
                    color: Kirigami.Theme.highlightColor
                    Layout.alignment: Qt.AlignHCenter
                }
            }

            // Ping (spans 2 columns)
            ColumnLayout {
                Layout.columnSpan: 2
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing

                PlasmaComponents3.Label {
                    text: "Ping"
                    font.pointSize: Kirigami.Theme.smallFont.pointSize
                    color: Kirigami.Theme.disabledTextColor
                    Layout.alignment: Qt.AlignHCenter
                }

                PlasmaComponents3.Label {
                    text: root.pingLatency
                    font.pointSize: Kirigami.Theme.defaultFont.pointSize * 1.3
                    font.bold: true
                    color: hasData ? Kirigami.Theme.textColor : Kirigami.Theme.disabledTextColor
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }

        // Separator
        Kirigami.Separator {
            Layout.fillWidth: true
        }

        // Server info and last update
        ColumnLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            PlasmaComponents3.Label {
                text: root.serverInfo
                font.pointSize: Kirigami.Theme.smallFont.pointSize
                elide: Text.ElideRight
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }

            PlasmaComponents3.Label {
                text: "Last update: " + root.lastUpdate
                font.pointSize: Kirigami.Theme.smallFont.pointSize
                color: Kirigami.Theme.disabledTextColor
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }
        }

        // Run test button
        PlasmaComponents3.Button {
            Layout.fillWidth: true
            text: isRunning ? "Test Running..." : "Run Speed Test"
            icon.name: isRunning ? "chronometer" : "media-playback-start"
            enabled: !isRunning && networkConnected
            onClicked: runTest()
        }
    }

    // Compact representation (for panel)
    compactRepresentation: PlasmaComponents3.ToolButton {
        icon.name: "network-wired"
        text: hasData ? "↓" + root.downloadSpeed + " ↑" + root.uploadSpeed : "Speed Test"

        onClicked: root.expanded = !root.expanded

        PlasmaComponents3.ToolTip {
            text: hasData ?
                  "Download: " + root.downloadSpeed + "\n" +
                  "Upload: " + root.uploadSpeed + "\n" +
                  "Ping: " + root.pingLatency
                  : "No data available"
        }
    }
}
