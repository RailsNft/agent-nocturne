#!/usr/bin/env python3
"""
Script de démarrage de l'Agent IA Nocturne
Version 2.0 - Architecture optimisée
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    try:
        # Importer et lancer l'application
        from interface.web.app import app
        
        print("🚀 Agent IA Nocturne - Démarrage...")
        print("🌐 Interface web : http://localhost:5002")
        print("📊 Dashboard : http://localhost:5002/")
        print("⚙️ Configuration : http://localhost:5002/config")
        print("🔧 Admin : http://localhost:5002/admin")
        
        app.run(
            host='localhost',
            port=5002,
            debug=False
        )
        
    except ImportError as e:
        print(f"❌ Erreur d'import : {e}")
        print("💡 Vérifiez que la migration a été effectuée correctement")
        return 1
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
