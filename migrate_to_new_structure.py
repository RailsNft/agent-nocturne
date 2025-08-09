#!/usr/bin/env python3
"""
Script de migration automatique pour l'Agent Nocturne
Transforme l'architecture actuelle en structure professionnelle
"""

import os
import shutil
import json
from pathlib import Path

class AgentNocturneMigrator:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.backup_dir = self.base_dir / "BACKUP_AVANT_MIGRATION"
        
    def create_backup(self):
        """Créer une sauvegarde de la structure actuelle"""
        print("🔄 Création de la sauvegarde...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Copier tous les fichiers sauf .git et __pycache__
        shutil.copytree(
            self.base_dir, 
            self.backup_dir,
            ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '.DS_Store')
        )
        
        print(f"✅ Sauvegarde créée dans : {self.backup_dir}")
        
    def create_new_structure(self):
        """Créer la nouvelle structure de dossiers"""
        print("🏗️ Création de la nouvelle architecture...")
        
        directories = [
            'core',
            'interface/web/routes', 
            'interface/web/static/css',
            'interface/web/static/js',
            'interface/web/static/images',
            'interface/web/templates/components',
            'services',
            'utils',
            'data/models',
            'data/storage',
            'tests/test_core',
            'tests/test_interface',
            'tests/test_services',
            'docs',
            'scripts',
            'config',
            'logs',
            'cache'
        ]
        
        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Créé : {directory}")
            
    def create_init_files(self):
        """Créer les fichiers __init__.py"""
        print("📝 Création des fichiers __init__.py...")
        
        init_dirs = ['core', 'interface', 'interface/web', 'interface/web/routes', 
                    'services', 'utils', 'data', 'data/models', 'data/storage', 
                    'tests', 'tests/test_core', 'tests/test_interface', 'tests/test_services']
        
        for directory in init_dirs:
            init_file = self.base_dir / directory / '__init__.py'
            if not init_file.exists():
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(f'"""Module {directory}"""\n')
                print(f"✅ Créé : {directory}/__init__.py")
                
    def move_files(self):
        """Déplacer les fichiers existants vers la nouvelle structure"""
        print("📦 Déplacement des fichiers...")
        
        moves = [
            ('agent-nocturne-python.py', 'core/agent.py'),
            ('stats_agent.py', 'core/stats.py'),
            ('telegram_notifications.py', 'services/telegram_service.py'),
            ('setup_config.py', 'utils/setup.py'),
            ('lancer_agent.py', 'scripts/start.py'),
            ('agent_config_example.json', 'config/default.json'),
            ('agent_config_local.json', 'config/local.json'),
            ('README.md', 'docs/README.md'),
            ('README_AGENT_NOCTURNE.md', 'docs/README_AGENT_NOCTURNE.md'),
            ('MIGRATION_PLAN.md', 'docs/MIGRATION_PLAN.md'),
            ('README_ARCHITECTURE.md', 'docs/README_ARCHITECTURE.md')
        ]
        
        for src, dst in moves:
            src_path = self.base_dir / src
            dst_path = self.base_dir / dst
            
            if src_path.exists():
                # Créer le dossier de destination si nécessaire
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Déplacer le fichier
                shutil.move(str(src_path), str(dst_path))
                print(f"✅ Déplacé : {src} → {dst}")
            else:
                print(f"⚠️ Fichier non trouvé : {src}")
                
    def move_interface_files(self):
        """Déplacer les fichiers de l'interface web"""
        print("🌐 Réorganisation de l'interface web...")
        
        # Déplacer l'interface web principale
        if (self.base_dir / 'interface' / 'web_interface.py').exists():
            shutil.move(
                str(self.base_dir / 'interface' / 'web_interface.py'),
                str(self.base_dir / 'interface' / 'web' / 'app.py')
            )
            print("✅ Déplacé : interface/web_interface.py → interface/web/app.py")
            
        # Déplacer les templates
        templates_src = self.base_dir / 'interface' / 'templates'
        templates_dst = self.base_dir / 'interface' / 'web' / 'templates'
        
        if templates_src.exists():
            if templates_dst.exists():
                shutil.rmtree(templates_dst)
            shutil.move(str(templates_src), str(templates_dst))
            print("✅ Déplacé : interface/templates → interface/web/templates")
            
    def create_new_files(self):
        """Créer de nouveaux fichiers pour la nouvelle architecture"""
        print("✨ Création de nouveaux fichiers...")
        
        # Nouveau README principal
        new_readme = """# 🌙 Agent IA Nocturne

## 🚀 Installation Rapide

```bash
# Cloner le dépôt
git clone [URL_DU_REPO]
cd agent-nocturne

# Configuration automatique
python3 utils/setup.py

# Lancer l'agent
python3 scripts/start.py
```

## 🌐 Interface Web
- **URL :** http://localhost:5002
- **Port :** 5002

## 📁 Structure du Projet
```
agent-nocturne/
├── core/           # Logique métier
├── interface/      # Interface utilisateur
├── services/       # Services externes
├── utils/          # Utilitaires
├── data/           # Données et stockage
├── tests/          # Tests automatisés
├── docs/           # Documentation
├── scripts/        # Scripts utilitaires
└── config/         # Configuration
```

## 🔧 Configuration
1. Exécutez `python3 utils/setup.py`
2. Modifiez `config/local.json` avec vos vraies informations
3. Lancez avec `python3 scripts/start.py`

---
**Développé avec ❤️ par l'équipe MicroWorkerLab**
"""
        
        with open(self.base_dir / 'README.md', 'w', encoding='utf-8') as f:
            f.write(new_readme)
        print("✅ Créé : README.md (nouveau)")
        
        # Fichier de configuration principal
        config_main = {
            "app": {
                "name": "Agent IA Nocturne",
                "version": "2.0.0",
                "port": 5002,
                "host": "localhost",
                "debug": False
            },
            "paths": {
                "config": "config/",
                "logs": "logs/",
                "cache": "cache/",
                "data": "data/"
            }
        }
        
        with open(self.base_dir / 'config' / 'app.json', 'w', encoding='utf-8') as f:
            json.dump(config_main, f, indent=2, ensure_ascii=False)
        print("✅ Créé : config/app.json")
        
        # Script de démarrage amélioré
        start_script = """#!/usr/bin/env python3
\"\"\"
Script de démarrage de l'Agent IA Nocturne
Version 2.0 - Architecture optimisée
\"\"\"

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    try:
        # Importer et lancer l'application
        from interface.web.app import create_app
        
        app = create_app()
        print("🚀 Agent IA Nocturne - Démarrage...")
        print("🌐 Interface web : http://localhost:5002")
        
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
"""
        
        with open(self.base_dir / 'scripts' / 'start.py', 'w', encoding='utf-8') as f:
            f.write(start_script)
        print("✅ Mis à jour : scripts/start.py")
        
    def update_gitignore(self):
        """Mettre à jour le .gitignore pour la nouvelle structure"""
        print("🔒 Mise à jour du .gitignore...")
        
        new_gitignore = """# Agent Nocturne - .gitignore (Architecture 2.0)

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environnement virtuel
venv/
env/
ENV/

# Logs et cache
logs/
cache/
*.log
opportunities_log.json

# Configuration locale et sensible
config/local.json
config/production.json
.env
*.key
*.pem
secrets.json

# Données
data/storage/*.json
data/storage/*.db

# Tests
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Fichiers temporaires
*.tmp
*.temp

# Backup
BACKUP_AVANT_MIGRATION/
"""
        
        with open(self.base_dir / '.gitignore', 'w', encoding='utf-8') as f:
            f.write(new_gitignore)
        print("✅ Mis à jour : .gitignore")
        
    def create_requirements_files(self):
        """Créer les fichiers de dépendances"""
        print("📦 Création des fichiers de dépendances...")
        
        requirements = """# Agent IA Nocturne - Dépendances principales
flask>=2.3.0
requests>=2.31.0
openai>=1.0.0
python-dotenv>=1.0.0
schedule>=1.2.0
psutil>=5.9.0
"""
        
        with open(self.base_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements)
        print("✅ Créé : requirements.txt")
        
        requirements_dev = """# Agent IA Nocturne - Dépendances développement
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
"""
        
        with open(self.base_dir / 'requirements-dev.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_dev)
        print("✅ Créé : requirements-dev.txt")
        
    def run_migration(self):
        """Exécuter la migration complète"""
        print("🚀 MIGRATION DE L'AGENT NOCTURNE")
        print("=" * 50)
        
        try:
            # 1. Sauvegarde
            self.create_backup()
            
            # 2. Nouvelle structure
            self.create_new_structure()
            
            # 3. Fichiers __init__.py
            self.create_init_files()
            
            # 4. Déplacement des fichiers
            self.move_files()
            self.move_interface_files()
            
            # 5. Nouveaux fichiers
            self.create_new_files()
            
            # 6. Mise à jour .gitignore
            self.update_gitignore()
            
            # 7. Fichiers de dépendances
            self.create_requirements_files()
            
            print("\n🎉 MIGRATION TERMINÉE AVEC SUCCÈS !")
            print("=" * 50)
            print("📁 Nouvelle structure créée")
            print("💾 Sauvegarde dans : BACKUP_AVANT_MIGRATION/")
            print("🔧 Prochaines étapes :")
            print("   1. Vérifier la nouvelle structure")
            print("   2. Tester le lancement : python3 scripts/start.py")
            print("   3. Commiter les changements")
            print("   4. Pousser vers GitHub")
            
        except Exception as e:
            print(f"\n❌ ERREUR LORS DE LA MIGRATION : {e}")
            print("🔄 Restauration de la sauvegarde...")
            
            # Restaurer depuis la sauvegarde
            if self.backup_dir.exists():
                for item in self.base_dir.iterdir():
                    if item.name not in ['.git', 'BACKUP_AVANT_MIGRATION']:
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                
                # Restaurer les fichiers
                for item in self.backup_dir.iterdir():
                    if item.name != 'BACKUP_AVANT_MIGRATION':
                        shutil.move(str(item), str(self.base_dir / item.name))
                
                print("✅ Restauration terminée")
            else:
                print("❌ Impossible de restaurer - sauvegarde non trouvée")

def main():
    migrator = AgentNocturneMigrator()
    
    # Demander confirmation
    print("⚠️ ATTENTION : Cette migration va réorganiser complètement l'architecture")
    print("💾 Une sauvegarde sera créée automatiquement")
    
    response = input("Continuer la migration ? (oui/non) : ").lower().strip()
    
    if response in ['oui', 'o', 'yes', 'y']:
        migrator.run_migration()
    else:
        print("❌ Migration annulée")

if __name__ == "__main__":
    main()
