#!/usr/bin/env python3
"""
Speed Test GUI with Fallback Support

This version includes fallback mechanisms for different Python versions
and missing dependencies.
"""

import sys
import os
from pathlib import Path

def check_python_compatibility():
    """Check Python version and warn about compatibility issues."""
    if sys.version_info >= (3, 13):
        print("⚠️  Warning: Python 3.13 may have compatibility issues with some GUI components.")
        print("   Recommended: Python 3.11-3.12 for optimal experience.")
        print("   Continuing with fallback support...\n")
    return True

def try_import_gui_dependencies():
    """Try importing GUI dependencies with fallback."""
    try:
        # Test Kivy import first
        os.environ['KIVY_GL_BACKEND'] = 'gl'
        import kivy
        from kivymd.app import MDApp
        return True, "kivymd"
    except ImportError as e:
        print(f"KivyMD not available: {e}")
        try:
            import tkinter as tk
            from tkinter import ttk, messagebox
            print("Falling back to Tkinter interface...")
            return True, "tkinter"
        except ImportError:
            print("No GUI framework available!")
            return False, None

def create_tkinter_gui():
    """Create simple Tkinter GUI as fallback."""
    import tkinter as tk
    from tkinter import ttk, messagebox
    import threading
    
    from speedtest_core import SpeedTestEngine, SpeedTestConfig, AsyncSpeedTestRunner
    
    class TkinterSpeedTestApp:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("Speed Test Tool")
            self.root.geometry("500x400")
            self.root.resizable(True, True)
            
            # Initialize core components
            self.config = SpeedTestConfig()
            self.engine = SpeedTestEngine(self.config)
            self.async_runner = AsyncSpeedTestRunner(self.engine)
            
            # GUI state
            self.is_testing = False
            self.create_widgets()
            self.update_status("Ready to test")
            
        def create_widgets(self):
            """Create GUI widgets."""
            # Main frame
            main_frame = ttk.Frame(self.root, padding="20")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Title
            title_label = ttk.Label(main_frame, text="Speed Test Tool", font=("Arial", 16, "bold"))
            title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
            
            # Status
            ttk.Label(main_frame, text="Status:").grid(row=1, column=0, sticky=tk.W, pady=5)
            self.status_var = tk.StringVar(value="Ready")\n            self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
            self.status_label.grid(row=1, column=1, sticky=tk.W, pady=5)
            
            # Progress
            ttk.Label(main_frame, text="Progress:").grid(row=2, column=0, sticky=tk.W, pady=5)
            self.progress_var = tk.StringVar(value="")
            self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
            self.progress_label.grid(row=2, column=1, sticky=tk.W, pady=5)
            
            self.progress_bar = ttk.Progressbar(main_frame, length=300, mode='determinate')
            self.progress_bar.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
            
            # Results frame
            results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
            results_frame.grid(row=4, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))
            
            # Results labels
            ttk.Label(results_frame, text="Download:").grid(row=0, column=0, sticky=tk.W)
            self.download_var = tk.StringVar(value="0.0 Mbps")
            ttk.Label(results_frame, textvariable=self.download_var).grid(row=0, column=1, sticky=tk.W, padx=10)
            
            ttk.Label(results_frame, text="Upload:").grid(row=1, column=0, sticky=tk.W)
            self.upload_var = tk.StringVar(value="0.0 Mbps")
            ttk.Label(results_frame, textvariable=self.upload_var).grid(row=1, column=1, sticky=tk.W, padx=10)
            
            ttk.Label(results_frame, text="Ping:").grid(row=2, column=0, sticky=tk.W)
            self.ping_var = tk.StringVar(value="0 ms")
            ttk.Label(results_frame, textvariable=self.ping_var).grid(row=2, column=1, sticky=tk.W, padx=10)
            
            ttk.Label(results_frame, text="Server:").grid(row=3, column=0, sticky=tk.W)
            self.server_var = tk.StringVar(value="No server selected")
            server_label = ttk.Label(results_frame, textvariable=self.server_var, wraplength=300)
            server_label.grid(row=3, column=1, sticky=tk.W, padx=10)
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
            
            self.start_button = ttk.Button(buttons_frame, text="Start Speed Test", command=self.start_test)
            self.start_button.grid(row=0, column=0, padx=5)
            
            self.cancel_button = ttk.Button(buttons_frame, text="Cancel", command=self.cancel_test, state="disabled")
            self.cancel_button.grid(row=0, column=1, padx=5)
            
            # Configure grid weights
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            main_frame.columnconfigure(1, weight=1)
            
        def update_status(self, message):
            """Update status message."""
            self.status_var.set(message)
            self.root.update_idletasks()
            
        def start_test(self):
            """Start speed test."""
            if not self.engine.check_network_connectivity():
                messagebox.showerror("Error", "No internet connection detected!")
                return
                
            self.is_testing = True
            self.start_button.config(state="disabled")
            self.cancel_button.config(state="normal")
            self.update_status("Testing in progress...")
            
            # Start async test
            self.async_runner.start_test()
            
            # Schedule progress updates
            self.check_progress()
            
        def cancel_test(self):
            """Cancel running test."""
            self.async_runner.cancel_test()
            self.reset_ui()
            self.update_status("Test cancelled")
            
        def check_progress(self):
            """Check for progress updates and results."""
            # Check progress
            progress_update = self.async_runner.get_progress()
            if progress_update:
                message, progress = progress_update
                self.progress_var.set(message)
                if progress >= 0:
                    self.progress_bar['value'] = int(progress * 100)
                    
            # Check for results
            result = self.async_runner.get_result()
            if result:
                self.handle_result(result)
                return
                
            # Continue checking if test is still running
            if self.is_testing:
                self.root.after(100, self.check_progress)
                
        def handle_result(self, result):
            """Handle test result."""
            self.reset_ui()
            
            if result.is_valid:
                self.download_var.set(f"{result.download_mbps:.1f} Mbps")
                self.upload_var.set(f"{result.upload_mbps:.1f} Mbps")
                self.ping_var.set(f"{result.ping_ms:.0f} ms")
                self.server_var.set(result.server_info)
                self.update_status("Test completed successfully")
                
                if result.warnings:
                    warning_msg = "\\n".join(result.warnings)
                    messagebox.showwarning("Warning", f"Test completed with warnings:\\n{warning_msg}")
            else:
                error_msg = "\\n".join(result.warnings) if result.warnings else "Test failed"
                self.update_status(f"Test failed")
                messagebox.showerror("Test Failed", error_msg)
                
        def reset_ui(self):
            """Reset UI to initial state."""
            self.is_testing = False
            self.start_button.config(state="normal")
            self.cancel_button.config(state="disabled")
            self.progress_var.set("")
            self.progress_bar['value'] = 0
            
        def run(self):
            """Run the application."""
            self.root.mainloop()
    
    return TkinterSpeedTestApp()

def main():
    """Main function with fallback support."""
    print("🚀 Speed Test Tool - GUI Edition")
    print("=" * 40)
    
    # Check Python compatibility
    check_python_compatibility()
    
    # Try importing GUI dependencies
    gui_available, gui_type = try_import_gui_dependencies()
    
    if not gui_available:
        print("❌ No GUI framework available!")
        print("   Please install tkinter or kivymd, or use CLI version:")
        print("   python sp.py")
        return 1
        
    try:
        if gui_type == "kivymd":
            print("✅ Starting KivyMD interface...")
            from speedtest_gui import SpeedTestApp
            SpeedTestApp().run()
        else:  # tkinter
            print("✅ Starting Tkinter fallback interface...")
            app = create_tkinter_gui()
            app.run()
            
    except KeyboardInterrupt:
        print("\\n⏹️  Application interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Application error: {e}")
        print("   Try using the CLI version: python sp.py")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())