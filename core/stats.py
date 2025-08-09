#!/usr/bin/env python3
"""
Script de statistiques pour l'Agent IA Nocturne
Affiche les performances et analyses des opportunités
"""

import json
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any
import statistics
import email.header

def load_opportunities() -> List[Dict[str, Any]]:
    """Charger les opportunités depuis le fichier JSON"""
    log_file = "opportunities_log.json"
    
    if not os.path.exists(log_file):
        print("❌ Aucun fichier de log trouvé. L'agent n'a pas encore traité d'emails.")
        return []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("❌ Erreur lors de la lecture du fichier de log.")
        return []

def parse_timestamp(timestamp_str: str) -> datetime:
    """Parser un timestamp ISO"""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        return datetime.now()

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
        # En cas d'erreur, retourner le sujet original
        return subject

def calculate_stats(opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculer les statistiques"""
    if not opportunities:
        return {}
    
    stats = {
        "total_opportunities": len(opportunities),
        "period": {},
        "decisions": {},
        "pertinence": {},
        "senders": {},
        "actions": {},
        "daily_activity": {},
        "top_keywords": {},
        "performance": {}
    }
    
    # Période d'activité
    timestamps = [parse_timestamp(opp["timestamp"]) for opp in opportunities]
    stats["period"]["debut"] = min(timestamps).strftime("%d/%m/%Y %H:%M")
    stats["period"]["fin"] = max(timestamps).strftime("%d/%m/%Y %H:%M")
    stats["period"]["duree"] = (max(timestamps) - min(timestamps)).days
    
    # Décisions
    decisions = [opp.get("decision", "Non défini") for opp in opportunities]
    stats["decisions"] = dict(Counter(decisions))
    
    # Pertinence
    pertinences = [opp.get("pertinence", 0) for opp in opportunities]
    if pertinences:
        stats["pertinence"]["moyenne"] = round(statistics.mean(pertinences), 2)
        stats["pertinence"]["mediane"] = statistics.median(pertinences)
        stats["pertinence"]["min"] = min(pertinences)
        stats["pertinence"]["max"] = max(pertinences)
        stats["pertinence"]["distribution"] = dict(Counter(pertinences))
    
    # Expéditeurs
    senders = [opp.get("sender", "Inconnu") for opp in opportunities]
    stats["senders"] = dict(Counter(senders).most_common(10))
    
    # Actions
    actions = [opp.get("action", "Aucune") for opp in opportunities]
    stats["actions"] = dict(Counter(actions))
    
    # Activité quotidienne
    daily_activity = defaultdict(int)
    for opp in opportunities:
        date = parse_timestamp(opp["timestamp"]).strftime("%d/%m/%Y")
        daily_activity[date] += 1
    stats["daily_activity"] = dict(daily_activity)
    
    # Mots-clés dans les raisons
    all_reasons = []
    for opp in opportunities:
        reasons = opp.get("raisons", [])
        all_reasons.extend(reasons)
    stats["top_keywords"] = dict(Counter(all_reasons).most_common(10))
    
    # Performance
    missions_retennes = sum(1 for opp in opportunities if "✅ Mission retenue" in opp.get("decision", ""))
    reponses_envoyees = sum(1 for opp in opportunities if "Réponse envoyée" in opp.get("action", ""))
    
    stats["performance"]["missions_retennes"] = missions_retennes
    stats["performance"]["reponses_envoyees"] = reponses_envoyees
    stats["performance"]["taux_retention"] = round((missions_retennes / len(opportunities)) * 100, 1) if opportunities else 0
    stats["performance"]["taux_reponse"] = round((reponses_envoyees / len(opportunities)) * 100, 1) if opportunities else 0
    
    return stats

def display_overview(stats: Dict[str, Any]):
    """Afficher le résumé général"""
    print("📊 RÉSUMÉ GÉNÉRAL")
    print("=" * 50)
    
    if not stats:
        print("❌ Aucune donnée disponible")
        return
    
    print(f"📧 Total d'opportunités analysées : {stats['total_opportunities']}")
    print(f"📅 Période : {stats['period']['debut']} → {stats['period']['fin']} ({stats['period']['duree']} jours)")
    print()
    
    # Performance
    perf = stats["performance"]
    print(f"✅ Missions retenues : {perf['missions_retennes']} ({perf['taux_retention']}%)")
    print(f"📤 Réponses envoyées : {perf['reponses_envoyees']} ({perf['taux_reponse']}%)")
    print(f"📈 Pertinence moyenne : {stats['pertinence']['moyenne']}/10")
    print()

def display_decisions(stats: Dict[str, Any]):
    """Afficher les décisions"""
    print("🎯 DÉCISIONS PRISES")
    print("=" * 50)
    
    decisions = stats.get("decisions", {})
    for decision, count in decisions.items():
        percentage = round((count / stats["total_opportunities"]) * 100, 1)
        print(f"{decision}: {count} ({percentage}%)")
    print()

def display_pertinence(stats: Dict[str, Any]):
    """Afficher les statistiques de pertinence"""
    print("📈 ANALYSE DE PERTINENCE")
    print("=" * 50)
    
    pertinence = stats.get("pertinence", {})
    if pertinence:
        print(f"Moyenne : {pertinence['moyenne']}/10")
        print(f"Médiane : {pertinence['mediane']}/10")
        print(f"Min/Max : {pertinence['min']}/10 - {pertinence['max']}/10")
        print()
        
        print("Distribution :")
        for score in sorted(pertinence.get("distribution", {}).keys()):
            count = pertinence["distribution"][score]
            percentage = round((count / stats["total_opportunities"]) * 100, 1)
            bar = "█" * int(percentage / 2)
            print(f"  {score}/10: {count} ({percentage}%) {bar}")
    print()

def display_senders(stats: Dict[str, Any]):
    """Afficher les expéditeurs principaux"""
    print("📧 EXPÉDITEURS PRINCIPAUX")
    print("=" * 50)
    
    senders = stats.get("senders", {})
    for i, (sender, count) in enumerate(senders.items(), 1):
        percentage = round((count / stats["total_opportunities"]) * 100, 1)
        # Nettoyer le nom de l'expéditeur
        clean_sender = sender.replace('"', '').split('<')[0].strip()
        print(f"{i:2d}. {clean_sender}: {count} ({percentage}%)")
    print()

def display_daily_activity(stats: Dict[str, Any]):
    """Afficher l'activité quotidienne"""
    print("📅 ACTIVITÉ QUOTIDIENNE")
    print("=" * 50)
    
    daily = stats.get("daily_activity", {})
    if daily:
        for date, count in sorted(daily.items()):
            print(f"{date}: {count} opportunité(s)")
    else:
        print("Aucune activité enregistrée")
    print()

def display_keywords(stats: Dict[str, Any]):
    """Afficher les mots-clés principaux"""
    print("🔍 MOTS-CLÉS PRINCIPAUX")
    print("=" * 50)
    
    keywords = stats.get("top_keywords", {})
    if keywords:
        for i, (keyword, count) in enumerate(keywords.items(), 1):
            print(f"{i:2d}. {keyword}: {count} fois")
    else:
        print("Aucun mot-clé enregistré")
    print()

def display_recent_opportunities(opportunities: List[Dict[str, Any]], limit: int = 10):
    """Afficher les opportunités récentes"""
    print(f"🕒 {limit} DERNIÈRES OPPORTUNITÉS")
    print("=" * 50)
    
    if not opportunities:
        print("Aucune opportunité enregistrée")
        return
    
    # Trier par timestamp
    sorted_opps = sorted(opportunities, key=lambda x: parse_timestamp(x["timestamp"]), reverse=True)
    
    for i, opp in enumerate(sorted_opps[:limit], 1):
        timestamp = parse_timestamp(opp["timestamp"]).strftime("%d/%m %H:%M")
        raw_subject = opp.get("subject", "Sans objet")
        decoded_subject = decode_email_subject(raw_subject)
        subject = decoded_subject[:50] + "..." if len(decoded_subject) > 50 else decoded_subject
        decision = opp.get("decision", "Non défini")
        pertinence = opp.get("pertinence", "N/A")
        
        print(f"{i:2d}. [{timestamp}] {subject}")
        print(f"    Pertinence: {pertinence}/10 | {decision}")
        print()

def show_menu():
    """Afficher le menu des statistiques"""
    print("📊 MENU DES STATISTIQUES")
    print("1. 📈 Résumé général")
    print("2. 🎯 Décisions prises")
    print("3. 📈 Analyse de pertinence")
    print("4. 📧 Expéditeurs principaux")
    print("5. 📅 Activité quotidienne")
    print("6. 🔍 Mots-clés principaux")
    print("7. 🕒 Opportunités récentes")
    print("8. 📋 Toutes les statistiques")
    print("0. ❌ Quitter")
    print()

def main():
    """Fonction principale"""
    print("🤖 Statistiques de l'Agent IA Nocturne")
    print("=" * 50)
    print()
    
    # Charger les données
    opportunities = load_opportunities()
    
    if not opportunities:
        print("❌ Aucune donnée disponible. L'agent n'a pas encore traité d'emails.")
        print("💡 Lancez l'agent avec : python3 agent-nocturne-python.py --force")
        return
    
    # Calculer les statistiques
    stats = calculate_stats(opportunities)
    
    while True:
        show_menu()
        choice = input("Votre choix (0-8): ").strip()
        
        if choice == "1":
            display_overview(stats)
        elif choice == "2":
            display_decisions(stats)
        elif choice == "3":
            display_pertinence(stats)
        elif choice == "4":
            display_senders(stats)
        elif choice == "5":
            display_daily_activity(stats)
        elif choice == "6":
            display_keywords(stats)
        elif choice == "7":
            display_recent_opportunities(opportunities)
        elif choice == "8":
            print("\n" + "="*60)
            display_overview(stats)
            display_decisions(stats)
            display_pertinence(stats)
            display_senders(stats)
            display_daily_activity(stats)
            display_keywords(stats)
            display_recent_opportunities(opportunities, 5)
        elif choice == "0":
            print("👋 Au revoir !")
            break
        else:
            print("❌ Choix invalide, veuillez réessayer")
        
        if choice != "0":
            input("\nAppuyez sur Entrée pour continuer...")
            print("\n" + "="*60)

if __name__ == "__main__":
    main() 