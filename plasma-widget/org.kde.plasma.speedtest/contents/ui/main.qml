import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami
import Qt.labs.platform as Platform
import org.kde.plasma.plasma5support as Plasma5Support

PlasmoidItem {
    id: root

    // Size hints
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
    property string helperScript: Qt.resolvedUrl("../code/speedtest_helper.py").toString().replace("file://", "")
    property string helperWrapper: Qt.resolvedUrl("../code/run_helper.sh").toString().replace("file://", "")
    property string pythonCmd: "python3"

    // Helper DataSource to execute helper script (Plasma 5/6)
    Plasma5Support.DataSource {
        id: helperDS
        engine: "executable"
        connectedSources: []
        interval: 0

        onNewData: function (sourceName, data) {
            var stdout = data["stdout"] || ""
            try {
                var result = JSON.parse(stdout)
                applyResult(result)
            } catch (e) {
                logger.info("Failed to parse helper output: " + e)
            }
            // disconnect to avoid repeated triggers
            disconnectSource(sourceName)
        }

        function run(command) {
            var cmd = helperWrapper + " " + command
            // Use /bin/sh -c to ensure script runs with shell
            connectSource("/bin/sh -c '" + cmd + "'")
        }
    }

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
    function applyResult(result) {
        if (!result)
            return
        if (result.status === "success") {
            downloadSpeed = result.download + " Mbps"
            uploadSpeed = result.upload + " Mbps"
            pingLatency = result.ping + " ms"
            serverInfo = result.server || "Speed test server"
            lastUpdate = result.timestamp || "Unknown"
            hasData = true
            networkConnected = true
        } else if (result.status === "no_data") {
            serverInfo = result.message || "No data available"
            hasData = false
        } else if (result.status === "error") {
            serverInfo = "Error: " + (result.message || "Unknown error")
            hasData = false
        } else if (typeof result.connected !== "undefined") {
            networkConnected = result.connected
        }
    }

    function loadLastResult() {
        // Load result from database via helper script
        runHelperCommand("get_last")
    }

    function runTest() {
        // Trigger background test via helper; widget will auto-refresh
        helperDS.run("run_test")
        isRunning = true
        loadTimer.start()
    }

    function checkNetwork() {
        helperDS.run("check_network")
    }

    // Helper to run Python script using shell wrapper
    function runHelperCommand(command) {
        helperDS.run(command)
    }

    // Logger function for debugging
    function logger_info(msg) {
        console.log("[SpeedTest Widget] " + msg)
    }
    property var logger: ({ info: logger_info })

    // Timer to reload after test completes
    Timer {
        id: loadTimer
        interval: 5000  // Check every 5 seconds
        running: false
        repeat: true
        triggeredOnStart: false

        property int checkCount: 0
        property int maxChecks: 24  // 2 minutes max (24 * 5 seconds)

        onTriggered: {
            loadLastResult()
            checkCount++

            // Stop checking after max attempts or when test completes
            if (checkCount >= maxChecks || (!isRunning && hasData)) {
                stop()
                checkCount = 0
                isRunning = false
            }
        }

        function start() {
            checkCount = 0
            running = true
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

            PlasmaComponents.ToolButton {
                icon.name: "view-refresh"
                onClicked: loadLastResult()
                PlasmaComponents.ToolTip {
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

            PlasmaComponents.Label {
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

                PlasmaComponents.Label {
                    text: "Download"
                    font.pointSize: Kirigami.Theme.smallFont.pointSize
                    color: Kirigami.Theme.disabledTextColor
                }

                PlasmaComponents.Label {
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

                PlasmaComponents.Label {
                    text: "Upload"
                    font.pointSize: Kirigami.Theme.smallFont.pointSize
                    color: Kirigami.Theme.disabledTextColor
                }

                PlasmaComponents.Label {
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

                PlasmaComponents.Label {
                    text: "Ping"
                    font.pointSize: Kirigami.Theme.smallFont.pointSize
                    color: Kirigami.Theme.disabledTextColor
                    Layout.alignment: Qt.AlignHCenter
                }

                PlasmaComponents.Label {
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

            PlasmaComponents.Label {
                text: root.serverInfo
                font.pointSize: Kirigami.Theme.smallFont.pointSize
                elide: Text.ElideRight
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }

            PlasmaComponents.Label {
                text: "Last update: " + root.lastUpdate
                font.pointSize: Kirigami.Theme.smallFont.pointSize
                color: Kirigami.Theme.disabledTextColor
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }
        }

        // Info text about running tests
        PlasmaComponents.Label {
            Layout.fillWidth: true
            text: "To run a new test, use CLI: make run-cli"
            font.pointSize: Kirigami.Theme.smallFont.pointSize
            color: Kirigami.Theme.disabledTextColor
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }

        // Refresh button (widget shows cached results)
        PlasmaComponents.Button {
            Layout.fillWidth: true
            text: "Refresh Results"
            icon.name: "view-refresh"
            onClicked: loadLastResult()
            PlasmaComponents.ToolTip {
                text: "Reload results from cache.\nRun tests using: cd ~/Projekty/Speed_test && make run-cli"
            }
        }
    }

    // Compact representation (for panel)
    compactRepresentation: PlasmaComponents.ToolButton {
        icon.name: "network-wired"
        text: hasData ? "↓" + root.downloadSpeed + " ↑" + root.uploadSpeed : "Speed Test"

        onClicked: root.expanded = !root.expanded

        PlasmaComponents.ToolTip {
            text: hasData ?
                  "Download: " + root.downloadSpeed + "\n" +
                  "Upload: " + root.uploadSpeed + "\n" +
                  "Ping: " + root.pingLatency
                  : "No data available"
        }
    }
}
