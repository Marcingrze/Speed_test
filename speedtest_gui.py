#!/usr/bin/env python3
"""
Speed Test GUI Application using Kivy

Modern Material Design GUI for internet speed testing application.
Provides an intuitive interface for running speed tests with real-time progress updates.
"""

import os
import sys
from pathlib import Path
import threading

# Set environment variables for Kivy before importing
os.environ['KIVY_GL_BACKEND'] = 'gl'
os.environ['KIVY_NO_CONSOLELOG'] = '1'  # Disable console logging to avoid Python 3.13 file descriptor issues

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.floatlayout import MDFloatLayout

from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, BooleanProperty

from speedtest_core import SpeedTestEngine, SpeedTestConfig, AsyncSpeedTestRunner
from test_results_storage import TestResultStorage


KV = '''
#:import Clock kivy.clock.Clock
#:import Widget kivy.uix.widget.Widget

<SpeedTestMainScreen>:
    md_bg_color: 0.95, 0.95, 0.95, 1

    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(20)
        
        MDTopAppBar:
            title: "Speed Test Tool"
            md_bg_color: app.theme_cls.primary_color
            elevation: 1
            right_action_items: [["cog", lambda x: root.show_settings_dialog()]]
        
        # Main content area
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(20)
            adaptive_height: True
            
            # Status card
            MDCard:
                size_hint_y: None
                height: dp(100)
                elevation: 2
                md_bg_color: 1, 1, 1, 1
                padding: dp(20)

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(10)

                    MDLabel:
                        text: "Network Status"
                        theme_text_color: "Primary"
                        font_style: "H6"
                        size_hint_y: None
                        height: dp(30)
                        bold: True

                    MDLabel:
                        id: status_label
                        text: root.status_text
                        theme_text_color: "Secondary"
                        font_style: "Subtitle1"
                        size_hint_y: None
                        height: dp(30)
            
            # Progress section
            MDCard:
                id: progress_card
                size_hint_y: None
                height: dp(120)
                elevation: 2
                md_bg_color: 1, 1, 1, 1
                padding: dp(20)
                opacity: 0

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(15)

                    MDLabel:
                        id: progress_label
                        text: root.progress_text
                        theme_text_color: "Primary"
                        font_style: "Subtitle1"
                        size_hint_y: None
                        height: dp(30)

                    MDProgressBar:
                        id: progress_bar
                        value: root.progress_value
                        color: app.theme_cls.primary_color
                        size_hint_y: None
                        height: dp(8)
            
            # Results section
            MDCard:
                id: results_card
                size_hint_y: None
                height: dp(320)
                elevation: 2
                md_bg_color: 1, 1, 1, 1
                padding: dp(20)
                opacity: 0

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(15)

                    # Title
                    MDLabel:
                        text: "Test Results"
                        theme_text_color: "Primary"
                        font_style: "H6"
                        size_hint_y: None
                        height: dp(30)

                    # Download
                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(50)

                        MDLabel:
                            text: "Download:"
                            theme_text_color: "Secondary"
                            font_style: "Subtitle1"
                            size_hint_x: 0.4
                            halign: "left"

                        MDLabel:
                            text: root.download_text
                            theme_text_color: "Primary"
                            font_style: "H5"
                            size_hint_x: 0.6
                            halign: "right"

                    # Upload
                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(50)

                        MDLabel:
                            text: "Upload:"
                            theme_text_color: "Secondary"
                            font_style: "Subtitle1"
                            size_hint_x: 0.4
                            halign: "left"

                        MDLabel:
                            text: root.upload_text
                            theme_text_color: "Primary"
                            font_style: "H5"
                            size_hint_x: 0.6
                            halign: "right"

                    # Ping
                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(50)

                        MDLabel:
                            text: "Ping:"
                            theme_text_color: "Secondary"
                            font_style: "Subtitle1"
                            size_hint_x: 0.4
                            halign: "left"

                        MDLabel:
                            text: root.ping_text
                            theme_text_color: "Primary"
                            font_style: "H5"
                            size_hint_x: 0.6
                            halign: "right"

                    # Separator
                    Widget:
                        size_hint_y: None
                        height: dp(1)
                        canvas:
                            Color:
                                rgba: 0.8, 0.8, 0.8, 0.5
                            Rectangle:
                                pos: self.pos
                                size: self.size

                    # Server
                    MDBoxLayout:
                        orientation: 'vertical'
                        spacing: dp(5)
                        size_hint_y: None
                        height: dp(50)

                        MDLabel:
                            text: "Server"
                            theme_text_color: "Secondary"
                            font_style: "Caption"
                            size_hint_y: None
                            height: dp(20)

                        MDLabel:
                            text: root.server_info
                            theme_text_color: "Primary"
                            font_style: "Body2"
                            size_hint_y: None
                            height: dp(25)
            
            # Spacer
            Widget:
        
        # Control buttons
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(15)
            size_hint_y: None
            height: dp(56)
            padding: [0, dp(10), 0, dp(10)]

            MDRaisedButton:
                id: test_button
                text: root.button_text
                disabled: root.is_testing
                md_bg_color: app.theme_cls.primary_color
                on_release: root.start_speed_test()
                size_hint_x: 0.75
                font_size: "16sp"

            MDRaisedButton:
                text: "Stop"
                disabled: not root.is_testing
                on_release: root.cancel_speed_test()
                md_bg_color: (0.95, 0.26, 0.21, 1) if not self.disabled else (0.7, 0.7, 0.7, 1)
                size_hint_x: 0.25
'''


class SpeedTestMainScreen(MDScreen):
    """Main screen for speed test application."""
    
    # Properties for data binding
    status_text = StringProperty("Ready to test")
    progress_text = StringProperty("")
    progress_value = NumericProperty(0)
    is_testing = BooleanProperty(False)
    button_text = StringProperty("Start Speed Test")
    
    # Results properties
    download_speed = NumericProperty(0)
    upload_speed = NumericProperty(0)
    ping_latency = NumericProperty(0)
    server_info = StringProperty("No server selected")

    # Formatted display properties
    download_text = StringProperty("0.0 Mbps")
    upload_text = StringProperty("0.0 Mbps")
    ping_text = StringProperty("0 ms")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize core components
        self.config = SpeedTestConfig()
        self.engine = SpeedTestEngine(self.config)
        self.async_runner = AsyncSpeedTestRunner(self.engine)
        self.storage = TestResultStorage()

        # UI state
        self.update_event = None
        self.settings_dialog = None

        # Check initial network status
        Clock.schedule_once(self.check_initial_network, 0.5)
    
    def check_initial_network(self, dt):
        """Check network connectivity on app start (non-blocking)."""
        def _bg_check():
            ok = self.engine.check_network_connectivity()
            Clock.schedule_once(lambda _dt: self._set_network_status(ok), 0)
        threading.Thread(target=_bg_check, daemon=True).start()
    
    def _set_network_status(self, ok: bool):
        self.status_text = "Network connection active" if ok else "No network connection detected"
        if not ok:
            Snackbar(
                text="No internet connection detected",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=.5
            ).open()
    
    def start_speed_test(self):
        """Start the speed test process."""
        # Prevent multiple concurrent tests
        if self.is_testing:
            return
            
        # Check network connectivity first (non-blocking UX)
        # Optimistic start + background recheck to avoid blocking UI
        prev_status = self.status_text
        def _bg_recheck():
            ok = self.engine.check_network_connectivity()
            if not ok:
                Clock.schedule_once(lambda _dt: self._handle_no_network_during_start(prev_status), 0)
        threading.Thread(target=_bg_recheck, daemon=True).start()
        
        # CRITICAL: Properly cleanup any existing Clock events
        if self.update_event:
            Clock.unschedule(self.update_event)
            self.update_event = None
        
        # Update UI state
        self.is_testing = True
        self.button_text = "Testing..."
        self.status_text = "Speed test in progress"
        
        # Show progress card with animation
        self.show_progress_card()
        
        # Start asynchronous test
        self.async_runner.start_test()
        
        # Schedule progress updates
        self.update_event = Clock.schedule_interval(self.update_progress, 0.1)
    
    def cancel_speed_test(self):
        """Cancel running speed test."""
        if self.async_runner.is_running():
            self.async_runner.cancel_test()
            self.reset_ui_state()
            self.status_text = "Test cancelled"
            Snackbar(
                text="Speed test cancelled",
                snackbar_x="10dp",
                snackbar_y="10dp",
            ).open()
    
    def _handle_no_network_during_start(self, previous_status: str):
        if self.is_testing:
            self.cancel_speed_test()
        self.status_text = "No internet connection detected"
        Snackbar(
            text="No internet connection detected",
            snackbar_x="10dp",
            snackbar_y="10dp",
        ).open()
    
    def update_progress(self, dt):
        """Update progress and check for results with atomic queue operations."""
        # Use new atomic method to get all progress updates
        progress_updates = self.async_runner.get_all_progress()
        
        # Use the latest progress update if any
        if progress_updates:
            message, progress = progress_updates[-1]  # Use most recent update
            self.progress_text = message
            if progress is not None and progress >= 0:
                self.progress_value = int(progress * 100)
        
        # Check for test completion
        result = self.async_runner.get_result()
        if result:
            # Handle cancellation separately
            if result.is_cancelled:
                self.reset_ui_state()
                self.status_text = "Test cancelled"
                return False  # Stop the clock event

            self.handle_test_result(result)
            return False  # Stop the clock event

        return True  # Continue the clock event

    def handle_test_result(self, result):
        """Handle completed test result."""
        self.reset_ui_state()

        if result.is_valid:
            # Update result values
            self.download_speed = result.download_mbps
            self.upload_speed = result.upload_mbps
            self.ping_latency = result.ping_ms
            self.server_info = result.server_info

            # Update formatted display text
            self.download_text = f"{result.download_mbps:.1f} Mbps"
            self.upload_text = f"{result.upload_mbps:.1f} Mbps"
            self.ping_text = f"{result.ping_ms:.0f} ms"

            # Show results with animation
            self.show_results_card()

            self.status_text = "Test completed successfully"

            # Save results to database if enabled
            if self.config['save_results_to_database']:
                try:
                    record_id = self.storage.save_result(result)
                    print(f"Result saved to database (ID: {record_id}).")
                except Exception as e:
                    error_msg = f"Failed to save result to database: {e}"
                    print(f"Warning: {error_msg}")
                    # Show user-facing error notification
                    Snackbar(
                        text=f"Warning: {error_msg}",
                        snackbar_x="10dp",
                        snackbar_y="10dp",
                        bg_color=(0.8, 0.4, 0, 1)  # Orange warning color
                    ).open()

            # Update Plasma widget cache
            try:
                from pathlib import Path
                import json as json_module
                from datetime import datetime as dt

                cache_dir = Path.home() / '.cache' / 'plasma-speedtest'
                cache_file = cache_dir / 'widget_cache.json'
                cache_dir.mkdir(parents=True, exist_ok=True)

                cache_data = {
                    "status": "success",
                    "download": round(result.download_mbps, 1),
                    "upload": round(result.upload_mbps, 1),
                    "ping": round(result.ping_ms, 0),
                    "server": result.server_info,
                    "timestamp": dt.fromtimestamp(result.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                    "is_valid": result.is_valid,
                    "warnings": result.warnings
                }

                with open(cache_file, 'w', encoding='utf-8') as f:
                    json_module.dump(cache_data, f, ensure_ascii=False, indent=2)

                print(f"Widget cache updated: {cache_file}")
            except Exception as e:
                print(f"Note: Failed to update widget cache: {e}")

            # Show warnings if any
            if result.warnings:
                warning_text = "; ".join(result.warnings)
                Snackbar(
                    text=f"Warning: {warning_text}",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                ).open()
        else:
            # Show error
            error_msg = "; ".join(result.warnings) if result.warnings else "Test failed"
            self.status_text = f"Test failed: {error_msg}"

            Snackbar(
                text=f"Test failed: {error_msg}",
                snackbar_x="10dp",
                snackbar_y="10dp",
            ).open()
    
    def reset_ui_state(self):
        """Reset UI to initial state with proper resource cleanup."""
        self.is_testing = False
        self.button_text = "Start Speed Test"
        self.progress_value = 0
        self.progress_text = ""
        
        # Stop progress updates with proper Clock cleanup
        if self.update_event:
            Clock.unschedule(self.update_event)
            self.update_event = None
        
        # Ensure async runner is properly cleaned up with improved timeout
        if hasattr(self.async_runner, '_thread') and self.async_runner._thread:
            if self.async_runner._thread.is_alive():
                # First try gentle cancellation
                self.async_runner.cancel_test()
                try:
                    # Calculate worst-case timeout for thread cleanup
                    # Components:
                    # 1. Test execution time per retry: base_timeout * max_retries
                    # 2. Exponential backoff delays between retries (capped at 30s each)
                    # 3. Safety buffer for cleanup

                    base_timeout = self.config.get('speedtest_timeout', 60)
                    max_retries = self.config.get('max_retries', 3)
                    retry_delay_base = self.config.get('retry_delay', 2)

                    # Sum of all possible backoff delays (capped at 30s per delay)
                    total_backoff = sum(
                        min(retry_delay_base * (2 ** i), 30)
                        for i in range(max_retries - 1)  # -1 because no delay after last retry
                    )

                    # Total timeout = all retries + all backoffs + buffer
                    timeout = (base_timeout * max_retries) + total_backoff + 10

                    self.async_runner._thread.join(timeout=timeout)
                    if self.async_runner._thread.is_alive():
                        # Log warning but don't force - daemon thread will clean up
                        print(f"Warning: Background test thread did not terminate within {timeout}s")
                except Exception:
                    pass  # Thread cleanup failed, but continue
        
        # Hide progress card
        self.hide_progress_card()
    
    def show_progress_card(self):
        """Show progress card with animation."""
        progress_card = self.ids.progress_card
        anim = Animation(opacity=1, duration=0.3)
        anim.start(progress_card)
    
    def hide_progress_card(self):
        """Hide progress card with animation."""
        progress_card = self.ids.progress_card
        anim = Animation(opacity=0, duration=0.3)
        anim.start(progress_card)
    
    def show_results_card(self):
        """Show results card with animation."""
        results_card = self.ids.results_card
        anim = Animation(opacity=1, duration=0.5)
        anim.start(results_card)
    
    def show_settings_dialog(self):
        """Show settings configuration dialog with proper lifecycle management."""
        # Prevent multiple simultaneous dialogs
        if self.settings_dialog:
            if hasattr(self.settings_dialog, '_is_dismissing'):
                return  # Already dismissing, ignore request
            self.settings_dialog._is_dismissing = True
            self.settings_dialog.dismiss()
            self.settings_dialog = None
            # Allow one frame for Kivy to complete cleanup
            Clock.schedule_once(lambda dt: self._create_settings_dialog(), 0.1)
        else:
            self._create_settings_dialog()

    def _create_settings_dialog(self):
        """Create and show settings dialog."""
        self.settings_dialog = MDDialog(
            title="Settings",
            text="Configuration options will be available in future updates.",
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=self.close_settings_dialog
                )
            ]
        )
        self.settings_dialog.open()

    def close_settings_dialog(self, *args):
        """Close settings dialog with proper cleanup."""
        if self.settings_dialog:
            self.settings_dialog.dismiss()
            self.settings_dialog = None  # Allow garbage collection


class SpeedTestApp(MDApp):
    """Main application class."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Speed Test Tool"
    
    def build(self):
        """Build and return the main application screen."""
        # Set app theme
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"

        # Set window size
        from kivy.core.window import Window
        Window.size = (500, 700)
        Window.minimum_width = 400
        Window.minimum_height = 600

        # Load KV string
        Builder.load_string(KV)

        # Return main screen
        screen = SpeedTestMainScreen()
        self.main_screen = screen
        return screen


    def on_stop(self):
        """Ensure DB connection is closed on app shutdown."""
        try:
            if hasattr(self, 'main_screen') and hasattr(self.main_screen, 'storage'):
                self.main_screen.storage.close()
        except Exception:
            pass


def main():
    """Main function to start GUI application."""
    try:
        SpeedTestApp().run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())