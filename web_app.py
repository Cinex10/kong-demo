#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
import sys
import json
from werkzeug.utils import secure_filename
import importlib.util
import dotenv

# Charger les variables d'environnement depuis .env
dotenv.load_dotenv()

# Ajouter le répertoire parent au chemin Python pour accéder aux modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules seulement après avoir ajusté le sys.path
try:
    from ai_model_client import GroqAiModelClient
    from demo_generator import DemoProjectGenerator
    from fs_manager import FileSystemManager
    from template_renderer import TemplateRenderer
except ImportError as e:
    print(f"Erreur d'importation: {e}")
    print(f"Chemins Python disponibles: {sys.path}")
    sys.exit(1)

app = Flask(__name__, template_folder='templates_web')
app.secret_key = "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"  # Nécessaire pour flash messages

# Configuration
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'output')
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json', 'yaml', 'yml'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Vérifier si l'API key est disponible
groq_api_key = os.getenv("GROQ_API_KEY") or dotenv.get_key(".env.example", "GROQ_API_KEY")
if not groq_api_key:
    print("Attention: GROQ_API_KEY n'est pas définie dans les variables d'environnement.")
    print("L'interface web fonctionnera, mais la génération de contenu pourrait échouer.")

# Initialisez les composants avec une gestion d'erreur
try:
    fs_manager = FileSystemManager(OUTPUT_DIR)
    
    # Créer le client AI avec une gestion d'erreur personnalisée
    class MockAiClient:
        def generate_content(self, *args, **kwargs):
            return "Contenu simulé - API key non disponible"
    
    # Utiliser un client mock si la clé API n'est pas disponible
    ai_client = GroqAiModelClient() if groq_api_key else MockAiClient()
    
    template_renderer = TemplateRenderer(ai_client=ai_client)
    generator = DemoProjectGenerator(fs_manager=fs_manager, template_renderer=template_renderer)
except Exception as e:
    print(f"Erreur d'initialisation: {e}")
    sys.exit(1)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Page d'accueil avec options pour générer un projet"""
    # Liste des projets existants
    projects = []
    if os.path.exists(OUTPUT_DIR):
        projects = [d for d in os.listdir(OUTPUT_DIR) if os.path.isdir(os.path.join(OUTPUT_DIR, d))]
    
    return render_template('base.html', projects=projects)

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    """Formulaire pour la génération interactive de projet"""
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            project_data = {
                'project_name': request.form.get('project_name'),
                'api_name': request.form.get('api_name'),
                'api_path': request.form.get('api_path'),
                'upstream_url': request.form.get('upstream_url'),
                'plugins': request.form.getlist('plugins'),
                # Ajoutez d'autres champs selon les besoins de votre générateur
            }
            
            # Utiliser votre générateur pour créer le projet
            project_name = generator.generate_from_web_input(project_data)
            
            flash(f'Projet {project_name} généré avec succès!', 'success')
            return redirect(url_for('project_details', project_name=project_name))
            
        except Exception as e:
            flash(f'Erreur lors de la génération du projet: {str(e)}', 'error')
            return redirect(url_for('generate'))
    
    # Méthode GET: afficher le formulaire
    return render_template('generate_form.html')

@app.route('/upload-config', methods=['GET', 'POST'])
def upload_config():
    """Traiter le téléchargement d'un fichier de configuration"""
    if request.method == 'POST':
        if 'config_file' not in request.files:
            flash('Aucun fichier trouvé', 'error')
            return redirect(request.url)
            
        file = request.files['config_file']
        project_name = request.form.get('project_name', '')
        
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Utiliser le générateur avec le fichier de configuration
                generated_project = generator.generate_from_config_file(filepath, project_name)
                flash(f'Projet {generated_project} généré avec succès!', 'success')
                return redirect(url_for('project_details', project_name=generated_project))
            except Exception as e:
                flash(f'Erreur lors de la génération: {str(e)}', 'error')
                return redirect(url_for('upload_config'))
    
    return render_template('upload_config.html')

@app.route('/project/<project_name>')
def project_details(project_name):
    """Afficher les détails d'un projet généré"""
    project_path = os.path.join(OUTPUT_DIR, project_name)
    
    if not os.path.exists(project_path):
        flash(f'Projet {project_name} introuvable', 'error')
        return redirect(url_for('index'))
    
    # Collecte des fichiers du projet
    files = []
    for root, _, filenames in os.walk(project_path):
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(root, filename), project_path)
            files.append(rel_path)
    
    return render_template('project_details.html', project_name=project_name, files=files)

@app.route('/project/<project_name>/download/<path:filepath>')
def download_file(project_name, filepath):
    """Télécharger un fichier spécifique d'un projet"""
    project_path = os.path.join(OUTPUT_DIR, project_name)
    return send_from_directory(project_path, filepath)

@app.route('/deploy', methods=['POST'])
def deploy():
    """Déployer un projet sur Kong Admin API"""
    project_name = request.form.get('project_name')
    kong_admin_url = request.form.get('kong_admin_url')
    
    if not project_name or not kong_admin_url:
        flash('Le nom du projet et l\'URL Kong Admin sont requis', 'error')
        return redirect(url_for('index'))
    
    try:
        # Utiliser la fonction de déploiement existante
        generator.deploy_to_kong(kong_admin_url, project_name)
        flash(f'Projet {project_name} déployé avec succès sur {kong_admin_url}!', 'success')
    except Exception as e:
        flash(f'Erreur lors du déploiement: {str(e)}', 'error')
    
    return redirect(url_for('project_details', project_name=project_name))

# Adaptez cette méthode dans votre classe DemoProjectGenerator
def generate_from_web_input(self, form_data):
    """
    Version adaptée de generate_from_interactive_input qui accepte les données 
    d'un formulaire web au lieu de les demander via input()
    """
    # Récupérer les données du formulaire
    project_name = form_data.get('project_name')
    api_name = form_data.get('api_name')
    api_path = form_data.get('api_path')
    upstream_url = form_data.get('upstream_url')
    plugins = form_data.get('plugins', [])
    
    if not project_name:
        raise ValueError("Le nom du projet est requis")
    
    # Créer le projet en utilisant ces valeurs
    project_dir = os.path.join(self.fs_manager.output_dir, project_name)
    os.makedirs(project_dir, exist_ok=True)
    
    # Dans un cas simple, on pourrait stocker ces données dans un fichier de configuration
    config_data = {
        'project_name': project_name,
        'api': {
            'name': api_name,
            'path': api_path,
            'upstream_url': upstream_url
        },
        'plugins': plugins
    }
    
    # Sauvegarder la configuration
    config_path = os.path.join(project_dir, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    # Générer les fichiers basés sur la configuration
    # Si vous avez une méthode pour générer des fichiers à partir d'une configuration, utilisez-la ici
    # Par exemple:
    # self.generate_project_files(config_data, project_dir)
    
    print(f"Projet '{project_name}' créé avec succès dans {project_dir}")
    return project_name

# Attacher cette méthode à votre classe
DemoProjectGenerator.generate_from_web_input = generate_from_web_input

if __name__ == '__main__':
    print(f"Démarrage du serveur web Kong Demo Generator")
    print(f"Répertoire de sortie: {OUTPUT_DIR}")
    app.run(debug=True)