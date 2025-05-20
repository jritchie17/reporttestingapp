import sys
import traceback
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        print("Created QApplication")
        
        main_window = MainWindow()
        print("Created MainWindow")
        
        main_window.show()
        print("Showed MainWindow")
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc() 
