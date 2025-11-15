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

        property string lastCommand: ""

        onNewData: function (sourceName, data) {
            var stdout = data["stdout"] || ""
            try {
                var result = JSON.parse(stdout)
                applyResult(result)

                // Handle run_test response specifically
                if (lastCommand === "run_test") {
                    if (result.status === "success") {
                        logger.info("Speed test started: " + result.message)
                        showNotification("Speed Test", "Test started in background. Results will update automatically.", "dialog-information")
                    } else if (result.status === "error") {
                        logger.info("Speed test error: " + result.message)
                        showNotification("Speed Test Error", result.message, "dialog-error")
                        isRunning = false
                        loadTimer.stop()
                    }
                }
            } catch (e) {
                logger.info("Failed to parse helper output: " + e)
                if (lastCommand === "run_test") {
                    isRunning = false
                    loadTimer.stop()
                }
            }
            // disconnect to avoid repeated triggers
            disconnectSource(sourceName)
            lastCommand = ""
        }

        function run(command) {
            lastCommand = command
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
        if (isRunning) {
            logger.info("Test already running, ignoring request")
            return
        }

        if (!networkConnected) {
            showNotification("Speed Test", "No network connection available", "dialog-warning")
            return
        }

        // Trigger background test via helper; widget will auto-refresh
        logger.info("Starting speed test via helper script")
        isRunning = true
        helperDS.run("run_test")
        loadTimer.start()
    }

    function checkNetwork() {
        helperDS.run("check_network")
    }

    // Helper to run Python script using shell wrapper
    function runHelperCommand(command) {
        helperDS.run(command)
    }

    // Show desktop notification
    function showNotification(title, message, icon) {
        // Use Plasma's notification system if available
        try {
            var notificationCmd = 'notify-send -i "' + icon + '" "' + title + '" "' + message + '"'
            helperDS.connectSource("/bin/sh -c '" + notificationCmd + "'")
        } catch (e) {
            logger.info("Failed to show notification: " + e)
        }
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
        property string lastTimestamp: ""

        onTriggered: {
            var previousTimestamp = lastTimestamp
            loadLastResult()
            checkCount++

            // Check if we got new results (timestamp changed)
            if (isRunning && hasData && lastUpdate !== previousTimestamp && previousTimestamp !== "") {
                // Test completed - new results available!
                logger.info("Test completed! New results detected.")
                showNotification("Speed Test Complete",
                                "Download: " + downloadSpeed + "\nUpload: " + uploadSpeed + "\nPing: " + pingLatency,
                                "dialog-positive")
                stop()
                checkCount = 0
                isRunning = false
                lastTimestamp = ""
            } else {
                lastTimestamp = lastUpdate
            }

            // Stop checking after max attempts
            if (checkCount >= maxChecks) {
                logger.info("Test monitoring timeout reached")
                showNotification("Speed Test", "Test timeout or completed. Check results.", "dialog-warning")
                stop()
                checkCount = 0
                isRunning = false
                lastTimestamp = ""
            }
        }

        function start() {
            checkCount = 0
            lastTimestamp = lastUpdate
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

        // Status message when test is running
        RowLayout {
            Layout.fillWidth: true
            visible: isRunning
            spacing: Kirigami.Units.smallSpacing

            PlasmaComponents.BusyIndicator {
                running: isRunning
                Layout.preferredWidth: Kirigami.Units.iconSizes.small
                Layout.preferredHeight: Kirigami.Units.iconSizes.small
            }

            PlasmaComponents.Label {
                text: "Running speed test..."
                font.pointSize: Kirigami.Theme.smallFont.pointSize
                color: Kirigami.Theme.highlightColor
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }
        }

        // Action buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            // Run Test button
            PlasmaComponents.Button {
                Layout.fillWidth: true
                text: isRunning ? "Test Running..." : "Run Speed Test"
                icon.name: isRunning ? "chronometer" : "run-build"
                enabled: !isRunning && networkConnected
                onClicked: runTest()
                PlasmaComponents.ToolTip {
                    text: isRunning ?
                          "Speed test is currently running. Please wait..." :
                          networkConnected ?
                          "Run a new speed test in the background" :
                          "No network connection available"
                }
            }

            // Refresh button
            PlasmaComponents.Button {
                Layout.fillWidth: true
                text: "Refresh"
                icon.name: "view-refresh"
                enabled: !isRunning
                onClicked: loadLastResult()
                PlasmaComponents.ToolTip {
                    text: "Reload latest results from database"
                }
            }
        }
    }

    // Compact representation (for panel)
    compactRepresentation: PlasmaComponents.ToolButton {
        icon.name: isRunning ? "chronometer" : "network-wired"
        text: isRunning ? "Testing..." : (hasData ? "↓" + root.downloadSpeed + " ↑" + root.uploadSpeed : "Speed Test")

        onClicked: root.expanded = !root.expanded

        // Busy indicator when test is running
        PlasmaComponents.BusyIndicator {
            anchors.centerIn: parent
            running: isRunning
            visible: isRunning
            width: parent.width * 0.6
            height: width
        }

        PlasmaComponents.ToolTip {
            text: isRunning ?
                  "Speed test is running...\nClick to view details" :
                  hasData ?
                  "Download: " + root.downloadSpeed + "\n" +
                  "Upload: " + root.uploadSpeed + "\n" +
                  "Ping: " + root.pingLatency + "\n" +
                  "Last update: " + root.lastUpdate
                  : "No data available\nClick to run a test"
        }
    }
}
