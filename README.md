# 🤖 Agent IA Nocturne

## 🎯 **Description**

L'Agent IA Nocturne est un assistant intelligent qui analyse automatiquement vos emails pour identifier et répondre aux opportunités de missions freelance.

## 🚀 **Installation et Lancement**

### **Méthode Simple**
```bash
# 1. Aller dans le répertoire
cd AGENT_NOCTURNE

# 2. Lancer l'agent
python3 lancer_agent.py
```

### **Méthode Manuelle**
```bash
# 1. Installer les dépendances
pip install flask psutil requests openai schedule python-dotenv

# 2. Lancer l'interface web
cd interface
python3 web_interface.py
```

## 🌐 **Interface Web**

L'interface est accessible sur : **http://localhost:5002**

### **Fonctionnalités**
- ✅ **Dashboard complet** avec statistiques
- ✅ **Boutons de démarrage/arrêt** de l'agent
- ✅ **Configuration** des clés API et email
- ✅ **Statistiques en temps réel**
- ✅ **Graphiques d'activité**
- ✅ **Historique des opportunités**

## ⚙️ **Configuration**

### **1. Email Gmail**
- Adresse : `prestadevpythonia@gmail.com`
- Mot de passe d'application : `acsc beyt rjar bpnx`

### **2. Clés API**
- **OpenAI API Key** : À configurer dans l'interface
- **Mistral API Key** : À configurer dans l'interface

### **3. Telegram (Optionnel)**
- Bot Token : À configurer
- Chat ID : À configurer

## 📊 **Fonctionnalités**

### **Analyse d'Emails**
- Surveillance automatique de la boîte Gmail
- Analyse IA des opportunités
- Scoring de pertinence (1-10)
- Détection des technologies et budgets

### **Réponses Automatiques**
- Génération de réponses personnalisées
- Signature automatique
- Envoi automatique des réponses

### **Statistiques**
- Nombre total d'opportunités
- Missions retenues/rejetées
- Pertinence moyenne
- Activité quotidienne

## 🔧 **Structure des Fichiers**

```
AGENT_NOCTURNE/
├── agent-nocturne-python.py      # Agent principal
├── agent_config.json             # Configuration
├── stats_agent.py                # Statistiques
├── telegram_notifications.py     # Notifications Telegram
├── opportunities_log.json        # Log des opportunités
├── lancer_agent.py              # Script de lancement
├── interface/                    # Interface web
│   ├── web_interface.py         # Serveur Flask
│   └── templates/               # Templates HTML
└── README.md                    # Ce fichier
```

## 🎯 **Utilisation**

1. **Lancer l'agent** : `python3 lancer_agent.py`
2. **Ouvrir l'interface** : http://localhost:5002
3. **Configurer** vos clés API et email
4. **Démarrer** l'agent avec le bouton "Démarrer"
5. **Surveiller** les opportunités dans le dashboard

## 📈 **Statistiques Exemple**

- **Total Opportunités** : 4
- **Missions Retenues** : 0
- **Missions Rejetées** : 0
- **Pertinence Moyenne** : 8.0/10

## 🔒 **Sécurité**

- Les mots de passe sont stockés localement
- Aucune donnée n'est envoyée à des serveurs tiers
- Connexion sécurisée IMAP/SMTP

## 🆘 **Dépannage**

### **Erreur "Module not found"**
```bash
pip install flask psutil requests openai schedule python-dotenv
```

### **Port déjà utilisé**
```bash
# Tuer les processus existants
pkill -f web_interface
```

### **Agent ne démarre pas**
- Vérifiez la configuration email
- Vérifiez les clés API
- Consultez les logs dans la console

---

**🎉 Agent IA Nocturne - Analyse automatique d'opportunités freelance !** 