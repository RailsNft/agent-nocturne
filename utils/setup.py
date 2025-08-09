#!/usr/bin/env python3
"""
Script de configuration automatique pour l'Agent Nocturne
Copie la configuration locale vers la configuration active
"""

import os
import shutil
import json

def main():
    print("🔧 Configuration de l'Agent Nocturne")
    print("=" * 40)
    
    # Vérifier si la config locale existe
    if not os.path.exists("agent_config_local.json"):
        print("❌ agent_config_local.json non trouvé")
        print("💡 Créez ce fichier avec vos vraies informations")
        return
    
    # Copier la config locale vers la config active
    try:
        shutil.copy("agent_config_local.json", "agent_config.json")
        print("✅ Configuration copiée avec succès")
        print("🔐 Vos vraies clés API et email sont maintenant actives")
        
        # Vérifier que la copie a fonctionné
        with open("agent_config.json", "r") as f:
            config = json.load(f)
            print(f"📧 Email configuré : {config['email']['username']}")
            print(f"🤖 OpenAI API : {'✅' if config['openai_api_key'] != 'VOTRE_CLE_API_OPENAI_ICI' else '❌'}")
            print(f"🌙 Mistral API : {'✅' if config['mistral_api_key'] != 'VOTRE_CLE_API_MISTRAL_ICI' else '❌'}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la copie : {e}")
        return
    
    print("\n🎯 Configuration terminée !")
    print("💡 Vous pouvez maintenant lancer l'agent : python3 lancer_agent.py")

if __name__ == "__main__":
    main()
