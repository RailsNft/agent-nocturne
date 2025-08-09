# 🌙 Agent IA Nocturne

## 📋 Description
Agent IA autonome spécialisé dans la surveillance et la détection d'opportunités 24h/24.

## 🚀 Installation Rapide

### Prérequis
- Python 3.8+
- pip

### Installation
```bash
# Cloner le dépôt
git clone [URL_DU_REPO]
cd agent-nocturne

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'agent
python lancer_agent.py
```

## 🌐 Interface Web
- **URL :** http://localhost:5002
- **Port :** 5002
- **Fonctionnalités :**
  - Dashboard en temps réel
  - Configuration des paramètres
  - Statistiques d'activité
  - Notifications Telegram

## 📁 Structure du Projet
```
agent-nocturne/
├── agent-nocturne-python.py    # Script principal
├── lancer_agent.py             # Lanceur
├── stats_agent.py              # Statistiques
├── telegram_notifications.py   # Notifications
├── interface/                  # Interface web
│   ├── web_interface.py
│   └── templates/
└── agent_config.json           # Configuration
```

## ⚙️ Configuration
Modifiez `agent_config.json` pour personnaliser :
- Intervalles de scan
- Notifications Telegram
- Modèles IA
- Limites d'opportunités

## 📊 Monitoring
- Logs en temps réel
- Statistiques d'activité
- Health checks automatiques
- Alertes en cas d'erreur

## 🔧 Développement
```bash
# Voir les logs
tail -f logs/agent.log

# Tester les composants
python -m pytest tests/

# Lancer en mode debug
DEBUG=1 python lancer_agent.py
```

## 📝 Changelog
- **v1.0** : Version initiale avec interface web complète
- Interface de configuration
- Notifications Telegram
- Dashboard de monitoring

## 🤝 Contribution
1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push vers la branche
5. Créer une Pull Request

## 📄 Licence
Propriétaire - Tous droits réservés

---
**Développé avec ❤️ par l'équipe MicroWorkerLab**
