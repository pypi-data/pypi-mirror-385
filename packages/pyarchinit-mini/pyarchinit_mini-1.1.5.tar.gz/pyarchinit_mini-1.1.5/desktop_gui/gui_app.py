#!/usr/bin/env python3
"""
PyArchInit-Mini Desktop GUI Application Launcher
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from desktop_gui.main_window import PyArchInitGUI
    from desktop_gui.dialogs import *
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all dependencies are installed and the module path is correct")
    sys.exit(1)

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'tkinter',
        'sqlalchemy', 
        'PIL',
        'reportlab',
        'networkx',
        'matplotlib'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'PIL':
                import PIL
            else:
                __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"""
Moduli mancanti: {', '.join(missing_modules)}

Per installare le dipendenze mancanti, esegui:
pip install {' '.join(missing_modules)}

oppure:
python scripts/modules_installer.py
"""
        print(error_msg)
        
        # Try to show GUI error if tkinter is available
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Dipendenze Mancanti", error_msg)
        except:
            pass
        
        return False
    
    return True

def main():
    """Main application entry point"""
    print("PyArchInit-Mini Desktop GUI")
    print("Archaeological Data Management System")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("Errore: Dipendenze mancanti. Installare i moduli richiesti.")
        sys.exit(1)
    
    try:
        # Create and run GUI application
        print("Avvio interfaccia grafica...")
        app = PyArchInitGUI()
        
        print("Interfaccia avviata con successo!")
        print("Utilizzare l'interfaccia grafica per gestire i dati archeologici.")
        print("Chiudere la finestra per terminare l'applicazione.")
        
        app.run()
        
        print("Applicazione terminata.")
        
    except KeyboardInterrupt:
        print("\nApplicazione interrotta dall'utente.")
    except Exception as e:
        error_msg = f"Errore imprevisto: {str(e)}"
        print(error_msg)
        
        # Try to show GUI error
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Errore", error_msg)
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()