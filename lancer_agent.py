#!/usr/bin/env python3
"""
Script de lancement pour l'Agent IA Nocturne
"""

import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("🤖 Agent IA Nocturne - Lancement")
    print("=" * 40)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists("agent-nocturne-python.py"):
        print("❌ Erreur: agent-nocturne-python.py non trouvé")
        print("💡 Assurez-vous d'être dans le répertoire AGENT_NOCTURNE")
        return
    
    # Utiliser l'environnement virtuel existant
    venv_path = os.path.join("..", "venv")
    if os.path.exists(venv_path):
        if sys.platform == "win32":
            python_path = os.path.join(venv_path, "Scripts", "python.exe")
        else:
            python_path = os.path.join(venv_path, "bin", "python")
        
        if os.path.exists(python_path):
            print(f"✅ Utilisation de l'environnement virtuel: {python_path}")
        else:
            print("⚠️ Environnement virtuel non trouvé, utilisation de Python système")
            python_path = sys.executable
    else:
        print("⚠️ Environnement virtuel non trouvé, utilisation de Python système")
        python_path = sys.executable
    
    # Vérifier les dépendances
    print("📦 Vérification des dépendances...")
    try:
        subprocess.run([python_path, "-c", "import flask, psutil"], check=True, capture_output=True)
        print("✅ Dépendances OK")
    except subprocess.CalledProcessError:
        print("❌ Dépendances manquantes")
        print("💡 Activez l'environnement virtuel: source ../venv/bin/activate")
        return
    
    # Lancer l'interface web
    print("🌐 Lancement de l'interface web...")
    interface_path = os.path.join("interface", "web_interface.py")
    
    if os.path.exists(interface_path):
        # Ouvrir le navigateur après 3 secondes
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:5002')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Lancer l'interface
        subprocess.run([python_path, interface_path])
    else:
        print("❌ Erreur: interface/web_interface.py non trouvé")
        print("💡 Vérifiez que l'interface est bien installée")

if __name__ == "__main__":
    main() 