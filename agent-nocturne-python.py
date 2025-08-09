#!/usr/bin/env python3
"""
Agent IA Nocturne - Version Python
Bot automatique qui filtre et répond aux opportunités freelance
"""

import os
import time
import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import openai
from mistralai.client import MistralClient
import schedule
from typing import Dict, List, Optional

# Import du module Telegram
try:
    from telegram_notifications import TelegramNotifier
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ Module Telegram non disponible")

class AgentIANocturne:
    def __init__(self, config: Dict):
        """Initialiser l'Agent IA Nocturne"""
        self.config = config
        
        # Initialiser les clients IA
        self.openai_client = None
        self.mistral_client = None
        
        # Essayer OpenAI d'abord
        if config.get('openai_api_key') and config['openai_api_key'] != "your_openai_api_key_here":
            try:
                self.openai_client = openai.OpenAI(api_key=config['openai_api_key'])
                print("✅ OpenAI configuré")
            except Exception as e:
                print(f"⚠️  Erreur OpenAI : {e}")
        
        # Fallback sur Mistral
        if config.get('mistral_api_key'):
            try:
                self.mistral_client = MistralClient(api_key=config['mistral_api_key'])
                print("✅ Mistral configuré")
            except Exception as e:
                print(f"⚠️  Erreur Mistral : {e}")
        
        if not self.openai_client and not self.mistral_client:
            raise Exception("❌ Aucun client IA configuré (OpenAI ou Mistral)")
        
        self.processed_emails = set()
        
        # Configuration email
        self.email_config = config['email']
        self.gmail_user = self.email_config['username']
        self.gmail_password = self.email_config['password']
        
        # Configuration IA
        self.criteria = config['criteria']
        
        # Initialiser Telegram
        self.telegram_notifier = None
        if TELEGRAM_AVAILABLE:
            self.telegram_notifier = TelegramNotifier(config)
            if self.telegram_notifier.enabled:
                print("📱 Telegram configuré")
            else:
                print("📱 Telegram désactivé")
        
        print("🤖 Agent IA Nocturne initialisé")
        print(f"📧 Email surveillé : {self.gmail_user}")
        print(f"🎯 Critères : {self.criteria}")
    
    def check_new_emails(self, force_all: bool = False) -> List[Dict]:
        """Vérifier les nouveaux emails"""
        try:
            # Connexion IMAP
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.gmail_user, self.gmail_password)
            mail.select("INBOX")
            
            # Vérifier si c'est la première exécution ou si on force
            first_run = not os.path.exists("processed_emails.txt")
            
            if first_run or force_all:
                print("🚀 Analyse des 50 derniers emails...")
                # Rechercher les 50 derniers emails (lus et non lus)
                _, messages = mail.search(None, "ALL")
                email_list = messages[0].split()[-50:]  # 50 derniers
            else:
                # Rechercher seulement les nouveaux emails non lus
                _, messages = mail.search(None, "UNSEEN")
                email_list = messages[0].split()
            
            new_emails = []
            for email_id in email_list:
                _, msg_data = mail.fetch(email_id, "(RFC822)")
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Extraire les informations
                subject = email_message["subject"] or "Sans objet"
                sender = email_message["from"]
                date = email_message["date"]
                
                # Extraire le contenu
                body = self.extract_email_body(email_message)
                
                email_info = {
                    "id": email_id.decode(),
                    "subject": subject,
                    "from": sender,
                    "date": date,
                    "body": body,
                    "snippet": body[:500] + "..." if len(body) > 500 else body
                }
                
                new_emails.append(email_info)
                print(f"📧 Nouvel email reçu : {subject}")
            
            mail.close()
            mail.logout()
            return new_emails
            
        except Exception as e:
            print(f"❌ Erreur lors de la vérification des emails : {e}")
            return []
    
    def extract_email_body(self, email_message) -> str:
        """Extraire le contenu du corps de l'email"""
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body = part.get_payload(decode=True).decode('latin-1', errors='ignore')
                    break
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = email_message.get_payload(decode=True).decode('latin-1', errors='ignore')
        return body
    
    def analyze_opportunity(self, email_content: str) -> Dict:
        """Analyser l'opportunité avec IA (OpenAI ou Mistral)"""
        prompt = f"""Tu es un assistant IA spécialisé en tri de missions pour un freelance développeur backend Python/API/IA.

Analyse l'opportunité suivante (email ou texte brut) et réponds aux 3 questions suivantes :

1. Est-ce que cette mission correspond à mes critères ?
   - Type : développement backend, API, Python, IA
           - Budget minimum : {self.criteria['budget_min']}€
   - Durée max : {self.criteria['duration_max']} jours
   - Langue : {self.criteria['language']}
   - Mots-clés à éviter : {', '.join(self.criteria['keywords_to_avoid'])}
   - Préférence : {self.criteria['work_mode']}

2. Note cette mission sur 10 en termes de pertinence pour moi.

3. Si elle est pertinente (note ≥ {self.criteria['relevance_threshold']}), dis "✅ Mission retenue"
Sinon, dis "❌ Mission rejetée – hors cible".

Voici le texte de l'opportunité :
---
{email_content}
---

Réponds au format JSON :
{{
  "pertinence": 8,
  "decision": "✅ Mission retenue",
  "raisons": ["Budget suffisant", "Technologies Python/API", "Full remote"],
  "points_attention": ["Vérifier la durée exacte", "Clarifier les spécifications"]
}}"""

        # Essayer OpenAI d'abord
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.3
                )
                
                result = json.loads(response.choices[0].message.content)
                print(f"🧠 Analyse OpenAI terminée : {result['decision']} (pertinence: {result['pertinence']}/10)")
                return result
                
            except Exception as e:
                print(f"⚠️  Erreur OpenAI, essai Mistral : {e}")
        
        # Fallback sur Mistral
        if self.mistral_client:
            try:
                messages = [{"role": "user", "content": prompt}]
                response = self.mistral_client.chat(
                    model="mistral-medium",
                    messages=messages,
                    max_tokens=500,
                    temperature=0.3
                )
                
                result = json.loads(response.choices[0].message.content)
                print(f"🧠 Analyse Mistral terminée : {result['decision']} (pertinence: {result['pertinence']}/10)")
                return result
                
            except Exception as e:
                print(f"❌ Erreur Mistral : {e}")
        
        # Erreur si aucun client ne fonctionne
        print("❌ Aucun client IA disponible")
        return {
            "pertinence": 0,
            "decision": "❌ Erreur d'analyse",
            "raisons": ["Erreur technique"],
            "points_attention": []
        }
    
    def generate_response(self, email_content: str) -> Dict:
        """Générer une réponse automatique avec IA (OpenAI ou Mistral)"""
        prompt = f"""Tu es un assistant personnel freelance spécialisé en développement backend Python/API/IA.

Génère une réponse professionnelle, aimable et personnalisée à cette mission, en tenant compte des éléments suivants :

- Tu es freelance spécialisé en développement backend Python, API et IA
- Tu es disponible pour échanger rapidement
- Tu veux clarifier les attentes du client
- Sois concis, humain, et engageant
- Signature incluse automatiquement

Texte de la mission :
---
{email_content}
---

Réponse attendue au format JSON :
{{
  "objet": "Proposition suite à votre demande de développement",
  "message": "Bonjour,\\n\\nMerci pour votre message. Votre projet de développement backend/API semble correspondre parfaitement à mon expertise en Python et IA.\\n\\nJe serais ravi d'échanger avec vous pour clarifier vos besoins et vous proposer une solution adaptée.\\n\\nDisponible pour un appel rapide cette semaine.\\n\\nCordialement,",
  "signature": "{self.config['signature']}"
}}

Le message doit être en français, ton professionnel mais accessible, et inclure un appel à l'action pour un échange rapide."""

        # Essayer OpenAI d'abord
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,
                    temperature=0.7
                )
                
                result = json.loads(response.choices[0].message.content)
                print(f"✍️ Réponse OpenAI générée : {result['objet']}")
                return result
                
            except Exception as e:
                print(f"⚠️  Erreur OpenAI, essai Mistral : {e}")
        
        # Fallback sur Mistral
        if self.mistral_client:
            try:
                messages = [{"role": "user", "content": prompt}]
                response = self.mistral_client.chat(
                    model="mistral-medium",
                    messages=messages,
                    max_tokens=800,
                    temperature=0.7
                )
                
                result = json.loads(response.choices[0].message.content)
                print(f"✍️ Réponse Mistral générée : {result['objet']}")
                return result
                
            except Exception as e:
                print(f"❌ Erreur Mistral : {e}")
        
        # Réponse par défaut si aucun client ne fonctionne
        print("❌ Aucun client IA disponible, réponse par défaut")
        return {
            "objet": "Réponse automatique",
            "message": "Bonjour,\n\nMerci pour votre message. Je vous répondrai rapidement.\n\nCordialement,",
            "signature": self.config['signature']
        }
    
    def send_email(self, to_email: str, subject: str, body: str, reply_to_id: str = None):
        """Envoyer un email de réponse"""
        try:
            msg = MIMEMultipart()
            # Utiliser l'email Hotmail comme expéditeur si configuré
            from_email = self.config.get('email', {}).get('reply_to', self.gmail_user)
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if reply_to_id:
                msg['In-Reply-To'] = reply_to_id
                msg['References'] = reply_to_id
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Connexion SMTP
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.gmail_user, self.gmail_password)
            
            # Envoi
            text = msg.as_string()
            server.sendmail(self.gmail_user, to_email, text)
            server.quit()
            
            print(f"📧 Email envoyé à : {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi : {e}")
            return False
    
    def log_opportunity(self, email_info: Dict, analysis: Dict, action: str):
        """Logger l'opportunité"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "email_id": email_info["id"],
            "subject": email_info["subject"],
            "sender": email_info["from"],
            "pertinence": analysis.get("pertinence", 0),
            "decision": analysis.get("decision", "❌ Erreur"),
            "action": action,
            "raisons": analysis.get("raisons", [])
        }
        
        # Sauvegarder dans un fichier JSON
        log_file = "opportunities_log.json"
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
                
            print(f"📊 Opportunité loggée : {action}")
            
        except Exception as e:
            print(f"❌ Erreur lors du logging : {e}")
    
    def process_email(self, email_info: Dict):
        """Traiter un email"""
        email_id = email_info["id"]
        
        # Éviter les doublons
        if email_id in self.processed_emails:
            return
        
        print(f"\n🔍 Traitement de l'email : {email_info['subject']}")
        
        # Analyser l'opportunité
        analysis = self.analyze_opportunity(email_info["body"])
        
        # Prendre une décision
        if analysis["decision"] == "✅ Mission retenue":
            print("✅ Mission retenue - Génération de réponse...")
            
            # Générer la réponse
            response = self.generate_response(email_info["body"])
            
            # Envoyer l'email
            full_body = f"{response['message']}\n\n{response['signature']}"
            success = self.send_email(
                to_email=email_info["from"],
                subject=response["objet"],
                body=full_body,
                reply_to_id=email_id
            )
            
            if success:
                self.log_opportunity(email_info, analysis, "Réponse envoyée")
            else:
                self.log_opportunity(email_info, analysis, "Erreur envoi")
        else:
            print("❌ Mission rejetée - Logging...")
            self.log_opportunity(email_info, analysis, "Rejetée")
        
        # Marquer comme traité
        self.processed_emails.add(email_id)
        
        # Notification Telegram pour les opportunités importantes
        if self.telegram_notifier and self.telegram_notifier.enabled:
            self.telegram_notifier.send_opportunity_alert(email_info, analysis)
    
    def run_once(self, force_all: bool = False):
        """Exécuter une fois"""
        print(f"\n🔄 Vérification des emails - {datetime.now().strftime('%H:%M:%S')}")
        new_emails = self.check_new_emails(force_all)
        
        if new_emails:
            print(f"📧 {len(new_emails)} email(s) trouvé(s)")
            for email_info in new_emails:
                self.process_email(email_info)
        else:
            print("📭 Aucun email trouvé")
    
    def start_monitoring(self, interval_minutes: int = 5):
        """Démarrer la surveillance continue"""
        print(f"🚀 Démarrage de la surveillance - Vérification toutes les {interval_minutes} minutes")
        print("🌙 Agent IA Nocturne actif - Tu dors, il bosse !")
        print("💡 Appuie sur Ctrl+C pour arrêter")
        
        # Planifier les vérifications
        schedule.every(interval_minutes).minutes.do(self.run_once)
        
        # Planifier le rapport quotidien Telegram
        if self.telegram_notifier and self.telegram_notifier.enabled:
            daily_config = self.telegram_notifier.daily_report
            if daily_config.get("enabled", False):
                report_time = daily_config.get("time", "07:00")
                print(f"📱 Rapport quotidien programmé à {report_time}")
                schedule.every().day.at(report_time).do(self.telegram_notifier.send_daily_report)
        
        # Première vérification immédiate
        self.run_once()
        
        # Boucle principale
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Vérifier toutes les 30 secondes
        except KeyboardInterrupt:
            print("\n🛑 Arrêt de l'Agent IA Nocturne")
            print("📊 Statistiques sauvegardées dans opportunities_log.json")

def load_config() -> Dict:
    """Charger la configuration"""
    config_file = "agent_config.json"
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Configuration par défaut
        config = {
            "openai_api_key": "your_openai_api_key_here",
            "email": {
                "username": "your_email@gmail.com",
                "password": "your_app_password"
            },
            "criteria": {
                "budget_min": 500,
                "duration_max": 30,
                "language": "français",
                "work_mode": "full remote",
                "keywords_to_avoid": ["gratuit", "exposition", "urgent sans budget", "bénévolat"],
                "relevance_threshold": 7
            },
            "signature": "David - Développeur Backend Python/IA\nwww.davidfreelance.fr\n+33 6 XX XX XX XX"
        }
        
        # Sauvegarder la configuration par défaut
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Configuration par défaut créée dans {config_file}")
        print("⚠️  Modifiez la configuration avant de lancer l'agent")
        return config

def main():
    """Fonction principale"""
    print("🤖 Agent IA Nocturne - Version Python")
    print("=" * 50)
    
    # Charger la configuration
    config = load_config()
    
    # Vérifier la configuration
    if config["openai_api_key"] == "your_openai_api_key_here":
        print("❌ Veuillez configurer votre clé API OpenAI dans agent_config.json")
        return
    
    if config["email"]["username"] == "your_email@gmail.com":
        print("❌ Veuillez configurer vos identifiants email dans agent_config.json")
        return
    
    # Créer et démarrer l'agent
    agent = AgentIANocturne(config)
    
    # Mode de fonctionnement
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--once":
            print("🔄 Mode exécution unique")
            agent.run_once()
        elif sys.argv[1] == "--force":
            print("🔄 Mode exécution unique - analyse forcée de tous les emails récents")
            agent.run_once(force_all=True)
        else:
            print("🔄 Mode surveillance continue")
            agent.start_monitoring()
    else:
        print("🔄 Mode surveillance continue")
        agent.start_monitoring()

if __name__ == "__main__":
    main() 