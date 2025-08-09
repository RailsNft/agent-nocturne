#!/usr/bin/env python3
"""
Interface Web Ultra-Simple pour l'Agent IA Nocturne
"""

from flask import Flask, render_template_string, request, jsonify, make_response
import json
import os
import sys
import subprocess
import psutil
from datetime import datetime
import email.header

app = Flask(__name__)

# Ajouter le répertoire parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def decode_email_subject(subject: str) -> str:
    """Décoder le sujet d'email encodé"""
    try:
        if subject and ('=?' in subject or '=?UTF-8' in subject or '=?Windows-1252' in subject):
            decoded_parts = email.header.decode_header(subject)
            decoded_subject = ''
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_subject += part.decode(encoding)
                    else:
                        decoded_subject += part.decode('utf-8', errors='ignore')
                else:
                    decoded_subject += part
            return decoded_subject
        else:
            return subject
    except Exception as e:
        return subject

def load_opportunities():
    """Charger les opportunités"""
    try:
        opportunities_file = os.path.join(parent_dir, 'opportunities_log.json')
        if os.path.exists(opportunities_file):
            with open(opportunities_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"❌ Erreur chargement opportunités: {e}")
        return []

def calculate_stats(opportunities):
    """Calculer les statistiques"""
    try:
        total = len(opportunities)
        accepted = sum(1 for opp in opportunities if opp.get('decision', '').startswith('✅'))
        rejected = sum(1 for opp in opportunities if opp.get('decision', '').startswith('❌'))
        
        # Calculer la pertinence moyenne
        pertinences = [opp.get('pertinence', 0) for opp in opportunities if opp.get('pertinence')]
        avg_relevance = sum(pertinences) / len(pertinences) if pertinences else 0
        
        # Compter les opportunités d'aujourd'hui
        today = datetime.now().strftime('%Y-%m-%d')
        today_count = sum(1 for opp in opportunities if opp.get('timestamp', '').startswith(today))
        
        return {
            "total": total,
            "accepted": accepted,
            "rejected": rejected,
            "avg_relevance": round(avg_relevance, 1),
            "today_count": today_count,
            "performance": {
                "missions_retenues": accepted,
                "reponses_envoyees": accepted,
                "taux_retention": round((accepted / total * 100) if total > 0 else 0, 1),
                "taux_reponse": round((accepted / total * 100) if total > 0 else 0, 1)
            },
            "pertinence": {
                "moyenne": avg_relevance
            }
        }
    except Exception as e:
        print(f"❌ Erreur calcul stats: {e}")
        return {
            "total": 0,
            "accepted": 0,
            "rejected": 0,
            "avg_relevance": 0,
            "today_count": 0,
            "performance": {
                "missions_retenues": 0,
                "reponses_envoyees": 0,
                "taux_retention": 0,
                "taux_reponse": 0
            },
            "pertinence": {
                "moyenne": 0
            }
        }

def check_agent_status() -> bool:
    """Vérifier si l'agent est en cours d'exécution"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('agent-nocturne-python.py' in arg for arg in cmdline):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    except Exception as e:
        print(f"❌ Erreur vérification statut : {e}")
        return False

# HTML de la page d'administration
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Agent IA Nocturne - Administration</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #10b981;
            --accent-color: #f59e0b;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
        }
        
        body {
            background-color: var(--bg-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .navbar-brand {
            font-weight: bold;
            color: var(--primary-color) !important;
        }
        
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        
        .card:hover {
            transform: translateY(-2px);
        }
        
        .form-control:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(37, 99, 235, 0.25);
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }
        
        .btn-primary:hover {
            background-color: #1d4ed8;
            border-color: #1d4ed8;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-robot me-2"></i>
                Agent IA Nocturne
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">
                    <i class="fas fa-chart-line me-1"></i>
                    Dashboard
                </a>
                <a class="nav-link active" href="/admin">
                    <i class="fas fa-cog me-1"></i>
                    Administration
                </a>
            </div>
        </div>
    </nav>

    <!-- Contenu Principal -->
    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h4 class="mb-0">
                            <i class="fas fa-cog me-2"></i>
                            Configuration de l'Agent
                        </h4>
                    </div>
                    <div class="card-body">
                        <form id="configForm">
                            <!-- Configuration Email -->
                            <div class="row mb-4">
                                <div class="col-12">
                                    <h5 class="border-bottom pb-2">
                                        <i class="fas fa-envelope me-2"></i>
                                        Configuration Email
                                    </h5>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="email" class="form-label">Adresse Email</label>
                                    <input type="email" class="form-control" id="email" name="email" 
                                           value="{{ config.get('email', '') }}" 
                                           placeholder="votre-email@gmail.com">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="app_password" class="form-label">Mot de passe d'application</label>
                                    <input type="password" class="form-control" id="app_password" name="app_password" 
                                           value="{{ config.get('app_password', '') }}" 
                                           placeholder="Mot de passe d'application Gmail">
                                </div>
                            </div>

                            <!-- Configuration API -->
                            <div class="row mb-4">
                                <div class="col-12">
                                    <h5 class="border-bottom pb-2">
                                        <i class="fas fa-key me-2"></i>
                                        Clés API
                                    </h5>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="openai_api_key" class="form-label">Clé API OpenAI</label>
                                    <input type="password" class="form-control" id="openai_api_key" name="openai_api_key" 
                                           value="{{ config.get('openai_api_key', '') }}" 
                                           placeholder="sk-...">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="mistral_api_key" class="form-label">Clé API Mistral</label>
                                    <input type="password" class="form-control" id="mistral_api_key" name="mistral_api_key" 
                                           value="{{ config.get('mistral_api_key', '') }}" 
                                           placeholder="Clé API Mistral">
                                </div>
                            </div>

                            <!-- Configuration Telegram -->
                            <div class="row mb-4">
                                <div class="col-12">
                                    <h5 class="border-bottom pb-2">
                                        <i class="fas fa-paper-plane me-2"></i>
                                        Notifications Telegram (Optionnel)
                                    </h5>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="telegram_bot_token" class="form-label">Token Bot Telegram</label>
                                    <input type="text" class="form-control" id="telegram_bot_token" name="telegram_bot_token" 
                                           value="{{ config.get('telegram_bot_token', '') }}" 
                                           placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="telegram_chat_id" class="form-label">Chat ID Telegram</label>
                                    <input type="text" class="form-control" id="telegram_chat_id" name="telegram_chat_id" 
                                           value="{{ config.get('telegram_chat_id', '') }}" 
                                           placeholder="123456789">
                                </div>
                            </div>

                            <!-- Configuration Signature -->
                            <div class="row mb-4">
                                <div class="col-12">
                                    <h5 class="border-bottom pb-2">
                                        <i class="fas fa-signature me-2"></i>
                                        Signature Email
                                    </h5>
                                </div>
                                <div class="col-12 mb-3">
                                    <label for="email_signature" class="form-label">Signature des emails</label>
                                    <textarea class="form-control" id="email_signature" name="email_signature" rows="4" 
                                              placeholder="Signature qui sera ajoutée aux emails envoyés">{{ config.get('email_signature', 'Agent IA Nocturne - Développeur Backend Python/IA') }}</textarea>
                                </div>
                            </div>

                            <!-- Boutons d'action -->
                            <div class="row">
                                <div class="col-12">
                                    <div class="d-flex justify-content-between">
                                        <button type="button" class="btn btn-secondary" onclick="testEmail()">
                                            <i class="fas fa-envelope me-1"></i>
                                            Tester Email
                                        </button>
                                        <div>
                                            <button type="button" class="btn btn-outline-primary me-2" onclick="window.location.href='/'">
                                                <i class="fas fa-arrow-left me-1"></i>
                                                Retour Dashboard
                                            </button>
                                            <button type="submit" class="btn btn-primary">
                                                <i class="fas fa-save me-1"></i>
                                                Sauvegarder
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        // Sauvegarder la configuration
        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const config = {};
            
            for (let [key, value] of formData.entries()) {
                config[key] = value;
            }
            
            fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Configuration saved successfully');
                } else {
                    alert('Erreur: ' + data.message);
                }
            })
            .catch(error => {
                alert('Erreur lors de la sauvegarde');
            });
        });

        // Tester la configuration email
        function testEmail() {
            const email = document.getElementById('email').value;
            const appPassword = document.getElementById('app_password').value;
            
            if (!email || !appPassword) {
                alert('Veuillez remplir l\'email et le mot de passe d\'application');
                return;
            }
            
            fetch('/api/email/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    app_password: appPassword
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Email test successful!');
                } else {
                    alert('Erreur test email: ' + data.message);
                }
            })
            .catch(error => {
                alert('Erreur lors du test email');
            });
        }

        // Demarrer l'agent
        function startAgent() {
            fetch('/api/agent/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Agent started successfully');
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                alert('Error starting agent');
            });
        }

        // Arreter l'agent
        function stopAgent() {
            fetch('/api/agent/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Agent stopped successfully');
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                alert('Error stopping agent');
            });
        }
    </script>
</body>
</html>
"""

# HTML du dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Agent IA Nocturne - Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #10b981;
            --accent-color: #f59e0b;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
        }
        
        body {
            background-color: var(--bg-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .navbar-brand {
            font-weight: bold;
            color: var(--primary-color) !important;
        }
        
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        
        .card:hover {
            transform: translateY(-2px);
        }
        
        .stat-card {
            background: linear-gradient(135deg, var(--primary-color), #1d4ed8);
            color: white;
        }
        
        .stat-card.success {
            background: linear-gradient(135deg, var(--secondary-color), #059669);
        }
        
        .stat-card.warning {
            background: linear-gradient(135deg, var(--accent-color), #d97706);
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        
        .status-running {
            background-color: var(--secondary-color);
            animation: pulse 2s infinite;
        }
        
        .status-stopped {
            background-color: #ef4444;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .opportunity-item {
            border-left: 4px solid var(--primary-color);
            padding: 12px;
            margin-bottom: 8px;
            background-color: var(--card-bg);
            border-radius: 0 8px 8px 0;
        }
        
        .opportunity-item.success {
            border-left-color: var(--secondary-color);
        }
        
        .opportunity-item.warning {
            border-left-color: var(--accent-color);
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-robot me-2"></i>
                Agent IA Nocturne
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link active" href="/">
                    <i class="fas fa-chart-line me-1"></i>
                    Dashboard
                </a>
                <a class="nav-link" href="/admin">
                    <i class="fas fa-cog me-1"></i>
                    Administration
                </a>
            </div>
        </div>
    </nav>

    <!-- Contenu Principal -->
    <div class="container mt-4">
        <!-- En-tête avec statut de l'agent -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h4 class="mb-1">
                                    <span class="status-indicator {% if agent_running %}status-running{% else %}status-stopped{% endif %}"></span>
                                    Statut de l'Agent
                                </h4>
                                <p class="text-muted mb-0">
                                    {% if agent_running %}
                                        Agent actif - Surveillance en cours
                                    {% else %}
                                        Agent arrêté - Aucune surveillance
                                    {% endif %}
                                </p>
                            </div>
                            <div>
                                {% if agent_running %}
                                    <button class="btn btn-danger" onclick="stopAgent()">
                                        <i class="fas fa-stop me-1"></i>
                                        Arrêter
                                    </button>
                                {% else %}
                                    <button class="btn btn-success" onclick="startAgent()">
                                        <i class="fas fa-play me-1"></i>
                                        Démarrer
                                    </button>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Statistiques principales -->
        <div class="row mb-4">
            <div class="col-md-3 mb-3">
                <div class="card stat-card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h6 class="card-title text-white-50">Total Opportunités</h6>
                                <h3 class="mb-0 text-white">{{ stats.total }}</h3>
                            </div>
                            <div class="align-self-center">
                                <i class="fas fa-envelope fa-2x text-white-50"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3 mb-3">
                <div class="card stat-card success">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h6 class="card-title text-white-50">Missions Retenues</h6>
                                <h3 class="mb-0 text-white">{{ stats.performance.missions_retenues }}</h3>
                            </div>
                            <div class="align-self-center">
                                <i class="fas fa-check-circle fa-2x text-white-50"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3 mb-3">
                <div class="card stat-card warning">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h6 class="card-title text-white-50">Missions Rejetées</h6>
                                <h3 class="mb-0 text-white">{{ stats.rejected }}</h3>
                            </div>
                            <div class="align-self-center">
                                <i class="fas fa-times-circle fa-2x text-white-50"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3 mb-3">
                <div class="card stat-card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h6 class="card-title text-white-50">Pertinence Moyenne</h6>
                                <h3 class="mb-0 text-white">{{ "%.1f"|format(stats.pertinence.moyenne) }}/10</h3>
                            </div>
                            <div class="align-self-center">
                                <i class="fas fa-chart-line fa-2x text-white-50"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Opportunités récentes -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-clock me-2"></i>
                            Opportunités Récentes
                        </h5>
                    </div>
                    <div class="card-body">
                        {% if opportunities %}
                            {% for opp in opportunities[-5:] %}
                                <div class="opportunity-item {% if '✅' in opp.decision %}success{% else %}warning{% endif %}">
                                    <div class="d-flex justify-content-between align-items-start">
                                        <div class="flex-grow-1">
                                            <div class="fw-bold">{{ decode_subject(opp.subject) }}</div>
                                            <small class="text-muted">{{ opp.timestamp }}</small>
                                        </div>
                                        <span class="badge {% if '✅' in opp.decision %}bg-success{% else %}bg-warning{% endif %}">
                                            {{ opp.pertinence }}/10
                                        </span>
                                    </div>
                                </div>
                            {% endfor %}
                        {% else %}
                            <div class="text-center text-muted">
                                <i class="fas fa-inbox fa-3x mb-3"></i>
                                <p>Aucune opportunité pour le moment</p>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        // Démarrer l'agent
        function startAgent() {
            fetch('/api/agent/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Agent started successfully');
                    location.reload();
                } else {
                    alert('Erreur: ' + data.message);
                }
            })
            .catch(error => {
                                    alert('Error starting agent');
            });
        }

        // Arrêter l'agent
        function stopAgent() {
            fetch('/api/agent/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Agent stopped successfully');
                    location.reload();
                } else {
                    alert('Erreur: ' + data.message);
                }
            })
            .catch(error => {
                                    alert('Error stopping agent');
            });
        }

        // Actualiser les statistiques
        function refreshStats() {
            fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                console.log('Stats actualisées:', data);
            })
            .catch(error => {
                console.error('Erreur actualisation stats:', error);
            });
        }

        // Actualiser automatiquement toutes les 30 secondes
        setInterval(refreshStats, 30000);
    </script>
</body>
</html>
"""

@app.route('/admin')
def admin_page():
    """Page d'administration"""
    config = load_agent_config()
    response = make_response(render_template_string(ADMIN_HTML, config=config))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def dashboard():
    """Page d'accueil avec dashboard"""
    opportunities = load_opportunities()
    stats = calculate_stats(opportunities)
    agent_running = check_agent_status()
    
    response = make_response(render_template_string(DASHBOARD_HTML, 
                                 stats=stats,
                                 opportunities=opportunities,
                                 agent_running=agent_running,
                                 decode_subject=decode_email_subject))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """API : Obtenir les statistiques"""
    try:
        opportunities = load_opportunities()
        stats = calculate_stats(opportunities)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/opportunities', methods=['GET'])
def api_get_opportunities():
    """API : Obtenir les opportunités récentes"""
    try:
        opportunities = load_opportunities()
        limit = request.args.get('limit', type=int)
        
        if limit:
            opportunities = opportunities[-limit:]
        
        # Décoder les sujets d'email
        for opp in opportunities:
            if 'subject' in opp:
                opp['subject'] = decode_email_subject(opp['subject'])
        
        return jsonify(opportunities)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/agent/start', methods=['POST'])
def api_start_agent():
    """API : Démarrer l'agent"""
    try:
        agent_path = os.path.join(parent_dir, 'agent-nocturne-python.py')
        subprocess.Popen([sys.executable, agent_path], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        return jsonify({"success": True, "message": "Agent started successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/agent/status', methods=['GET'])
def api_agent_status():
    """API : Vérifier le statut de l'agent"""
    try:
        is_running = check_agent_status()
        return jsonify({"running": is_running})
    except Exception as e:
        return jsonify({"running": False, "error": str(e)})

@app.route('/api/agent/stop', methods=['POST'])
def api_stop_agent():
    """API : Arrêter l'agent"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('agent-nocturne-python.py' in arg for arg in cmdline):
                    proc.terminate()
                    proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue
        return jsonify({"success": True, "message": "Agent stopped successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/email/test', methods=['POST'])
def api_test_email():
    """API : Tester la configuration email"""
    try:
        data = request.json
        email = data.get('email')
        app_password = data.get('app_password')
        
        if not email or not app_password:
            return jsonify({"success": False, "message": "Email et mot de passe requis"})
        
        # Test simple de connexion IMAP
        import imaplib
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email, app_password)
        mail.select("INBOX")
        mail.close()
        mail.logout()
        
        return jsonify({"success": True, "message": "Email test successful"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/config', methods=['GET'])
def api_get_config():
    """API : Obtenir la configuration"""
    try:
        config = load_agent_config()
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/config', methods=['POST'])
def api_save_config():
    """API : Sauvegarder la configuration"""
    try:
        config = request.json
        if save_agent_config(config):
            return jsonify({"success": True, "message": "Configuration saved"})
        else:
            return jsonify({"success": False, "message": "Erreur sauvegarde"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

def load_agent_config():
    """Charger la configuration de l'agent"""
    try:
        config_path = os.path.join(parent_dir, 'agent_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"❌ Erreur chargement config : {e}")
        return {}

def save_agent_config(config):
    """Sauvegarder la configuration de l'agent"""
    try:
        config_path = os.path.join(parent_dir, 'agent_config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde config : {e}")
        return False

if __name__ == '__main__':
    print("🤖 Agent IA Nocturne - Interface Web Ultra-Simple")
    print("=" * 50)
    print("🌐 Interface accessible sur : http://localhost:5002")
    print("💡 Le navigateur s'ouvrira automatiquement")
    
    # Ouvrir le navigateur automatiquement
    import webbrowser
    webbrowser.open('http://localhost:5002')
    
    app.run(host='0.0.0.0', port=5002, debug=False) 