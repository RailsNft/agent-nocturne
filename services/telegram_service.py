#!/usr/bin/env python3
"""
Module de notifications Telegram pour l'Agent IA Nocturne
Gère l'envoi de rapports quotidiens et notifications
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pytz
from stats_agent import load_opportunities, calculate_stats

class TelegramNotifier:
    def __init__(self, config: Dict[str, Any]):
        """Initialiser le notificateur Telegram"""
        self.config = config.get("telegram", {})
        self.enabled = self.config.get("enabled", False)
        self.bot_token = self.config.get("bot_token", "")
        self.chat_id = self.config.get("chat_id", "")
        self.daily_report = self.config.get("daily_report", {})
        
        if self.enabled and (not self.bot_token or not self.chat_id):
            print("⚠️ Telegram activé mais bot_token ou chat_id manquant")
            self.enabled = False
    
    def send_message(self, message: str) -> bool:
        """Envoyer un message Telegram"""
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            return True
        except Exception as e:
            print(f"❌ Erreur Telegram : {e}")
            return False
    
    def format_daily_report(self, stats: Dict[str, Any]) -> str:
        """Formater le rapport quotidien"""
        if not stats:
            return "📊 <b>Rapport Quotidien - Agent IA Nocturne</b>\n\n❌ Aucune donnée disponible"
        
        # Calculer les stats de la journée
        today = datetime.now().strftime("%d/%m/%Y")
        today_opportunities = []
        
        opportunities = load_opportunities()
        for opp in opportunities:
            opp_date = datetime.fromisoformat(opp["timestamp"].replace('Z', '+00:00')).strftime("%d/%m/%Y")
            if opp_date == today:
                today_opportunities.append(opp)
        
        # Stats de la journée
        today_stats = calculate_stats(today_opportunities)
        
        # Message principal
        message = f"📊 <b>Rapport Quotidien - Agent IA Nocturne</b>\n"
        message += f"📅 <b>{today}</b>\n\n"
        
        # Activité de la journée
        if today_opportunities:
            message += f"🆕 <b>Activité du jour :</b>\n"
            message += f"• 📧 {len(today_opportunities)} email(s) analysé(s)\n"
            
            missions_retenues = sum(1 for opp in today_opportunities if "✅ Mission retenue" in opp.get("decision", ""))
            reponses_envoyees = sum(1 for opp in today_opportunities if "Réponse envoyée" in opp.get("action", ""))
            
            message += f"• ✅ {missions_retenues} mission(s) retenue(s)\n"
            message += f"• 📤 {reponses_envoyees} réponse(s) envoyée(s)\n"
            
            if today_opportunities:
                pertinences = [opp.get("pertinence", 0) for opp in today_opportunities]
                moyenne = sum(pertinences) / len(pertinences)
                message += f"• 📈 Pertinence moyenne : {moyenne:.1f}/10\n"
        else:
            message += "😴 <b>Aucune activité aujourd'hui</b>\n"
        
        # Stats globales
        message += f"\n📈 <b>Statistiques globales :</b>\n"
        message += f"• 📧 Total : {stats['total_opportunities']} opportunité(s)\n"
        message += f"• ✅ Missions retenues : {stats['performance']['missions_retenues']} ({stats['performance']['taux_retention']}%)\n"
        message += f"• 📤 Réponses envoyées : {stats['performance']['reponses_envoyees']} ({stats['performance']['taux_reponse']}%)\n"
        message += f"• 📊 Pertinence moyenne : {stats['pertinence']['moyenne']}/10\n"
        
        # Top expéditeurs du jour
        if today_opportunities:
            senders = {}
            for opp in today_opportunities:
                sender = opp.get("sender", "Inconnu")
                senders[sender] = senders.get(sender, 0) + 1
            
            top_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)[:3]
            if top_senders:
                message += f"\n📧 <b>Top expéditeurs du jour :</b>\n"
                for i, (sender, count) in enumerate(top_senders, 1):
                    clean_sender = sender.replace('"', '').split('<')[0].strip()
                    message += f"{i}. {clean_sender} ({count})\n"
        
        # Opportunités récentes (max 3)
        if today_opportunities:
            message += f"\n🕒 <b>Dernières opportunités :</b>\n"
            for i, opp in enumerate(today_opportunities[-3:], 1):
                subject = opp.get("subject", "Sans objet")[:40] + "..." if len(opp.get("subject", "")) > 40 else opp.get("subject", "Sans objet")
                decision = opp.get("decision", "Non défini")
                pertinence = opp.get("pertinence", "N/A")
                message += f"{i}. {subject}\n   {decision} ({pertinence}/10)\n"
        
        message += f"\n🤖 <i>Agent IA Nocturne - Travaille pendant que vous dormez !</i>"
        
        return message
    
    def send_daily_report(self) -> bool:
        """Envoyer le rapport quotidien"""
        if not self.enabled or not self.daily_report.get("enabled", False):
            return False
        
        # Charger les statistiques
        opportunities = load_opportunities()
        if not opportunities:
            return self.send_message("📊 <b>Rapport Quotidien</b>\n\n❌ Aucune donnée disponible")
        
        stats = calculate_stats(opportunities)
        message = self.format_daily_report(stats)
        
        return self.send_message(message)
    
    def send_notification(self, title: str, message: str, priority: str = "normal") -> bool:
        """Envoyer une notification personnalisée"""
        if not self.enabled:
            return False
        
        emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
        
        formatted_message = f"{emoji} <b>{title}</b>\n\n{message}"
        return self.send_message(formatted_message)
    
    def send_opportunity_alert(self, email_info: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """Envoyer une alerte pour une opportunité importante"""
        if not self.enabled:
            return False
        
        pertinence = analysis.get("pertinence", 0)
        if pertinence < 8:  # Seulement les opportunités très pertinentes
            return False
        
        subject = email_info.get("subject", "Sans objet")
        sender = email_info.get("from", "Inconnu")
        decision = analysis.get("decision", "Non défini")
        raisons = analysis.get("raisons", [])
        
        message = f"🎯 <b>Opportunité Importante Détectée !</b>\n\n"
        message += f"📧 <b>Sujet :</b> {subject}\n"
        message += f"👤 <b>Expéditeur :</b> {sender}\n"
        message += f"📊 <b>Pertinence :</b> {pertinence}/10\n"
        message += f"✅ <b>Décision :</b> {decision}\n"
        
        if raisons:
            message += f"\n💡 <b>Raisons :</b>\n"
            for raison in raisons[:3]:  # Max 3 raisons
                message += f"• {raison}\n"
        
        return self.send_message(message)

def test_telegram_config(config: Dict[str, Any]) -> bool:
    """Tester la configuration Telegram"""
    notifier = TelegramNotifier(config)
    
    if not notifier.enabled:
        print("❌ Telegram non activé")
        return False
    
    print("🧪 Test de la configuration Telegram...")
    
    # Test simple
    test_message = "🤖 <b>Test Agent IA Nocturne</b>\n\n✅ Configuration Telegram fonctionnelle !"
    
    if notifier.send_message(test_message):
        print("✅ Configuration Telegram valide")
        return True
    else:
        print("❌ Erreur lors du test Telegram")
        return False

def schedule_daily_report(config: Dict[str, Any]):
    """Programmer le rapport quotidien"""
    daily_config = config.get("telegram", {}).get("daily_report", {})
    
    if not daily_config.get("enabled", False):
        return
    
    # Cette fonction sera appelée par le planificateur principal
    notifier = TelegramNotifier(config)
    notifier.send_daily_report() 