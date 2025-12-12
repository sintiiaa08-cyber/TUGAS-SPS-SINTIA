"""AromaSense - Herbal Analysis System Main Entry Point"""

import sys
import os
import traceback

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main application entry point"""
    try:
        from PySide6.QtWidgets import QApplication
        from main_window import MainWindow
        
        print("🚀 Starting AromaSense Herbal Analysis System...")
        print("📦 Initializing application...")
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("AromaSense")
        app.setApplicationVersion("1.0.0")
        
        print("✅ QApplication created successfully")
        
        # Create and show main window
        print("🖼️ Creating main window...")
        window = MainWindow()
        window.show()
        
        print("✅ Main window displayed successfully")
        print("🌿 AromaSense is ready! Check the GUI window.")
        
        # Run application
        return_code = app.exec()
        print(f"🔚 Application exited with code: {return_code}")
        return return_code
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("📋 Please install required dependencies:")
        print("   pip install PySide6 pyqtgraph pyserial numpy")
        input("Press Enter to exit...")
        return 1
        
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        print("🔍 Stack trace:")
        traceback.print_exc()
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main())