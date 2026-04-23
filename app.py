from flask import Flask, jsonify, request
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# --- MÉTRIQUES POUR GRAFANA ---
# Compteur de requêtes (par méthode et par route)
REQUESTS = Counter('inptic_requests_total', 'Total des requêtes HTTP', ['method', 'endpoint'])
# Jauge pour le nombre d'étudiants (idéal pour les graphiques Grafana)
STUDENTS_COUNT = Gauge('inptic_students_total', 'Nombre total d\'étudiants dans la base')

# Base de données temporaire
etudiants = [
    {"id": 1, "nom": "Mel Cham", "filiere": "SRI"},
    {"id": 2, "nom": "Alice Doe", "filiere": "ASUR"}
]

# Initialisation de la jauge
STUDENTS_COUNT.set(len(etudiants))

@app.route('/')
def home():
    REQUESTS.labels(method='GET', endpoint='/').inc()
    # Cette fois, on renvoie une interface visuelle (HTML)
    return """
    <html>
        <head><title>INPTIC - Gestion Étudiants</title></head>
        <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
            <h1 style="color: #2c3e50;">🎓 Système de Gestion des Étudiants INPTIC</h1>
            <p style="font-size: 1.2em;">Statut : <span style="color: green;">En ligne (v1.0)</span></p>
            <div style="margin: 30px;">
                <a href="/etudiants" style="padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px;">Afficher la liste des étudiants</a>
            </div>
            <form action="/etudiants" method="post">
                <button type="submit" style="padding: 10px 20px; background: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    ➕ Ajouter un étudiant (Test Graphique)
                </button>
            </form>
            <p style="margin-top: 50px; color: #7f8c8d;">Surveillance active : Prometheus & Grafana</p>
        </body>
    </html>
    """

@app.route('/etudiants', methods=['GET'])
def get_etudiants():
    REQUESTS.labels(method='GET', endpoint='/etudiants').inc()
    return jsonify(etudiants)

@app.route('/etudiants', methods=['POST'])
def add_etudiant():
    REQUESTS.labels(method='POST', endpoint='/etudiants').inc()

    # Simuler l'ajout d'un étudiant pour faire bouger Grafana
    nouveau_id = len(etudiants) + 1
    nouvel_etudiant = {"id": nouveau_id, "nom": f"Etudiant_{nouveau_id}", "filiere": "Informatique"}
    etudiants.append(nouvel_etudiant)

    # Mise à jour de la jauge
    STUDENTS_COUNT.set(len(etudiants))

    # Redirection vers l'accueil après l'ajout
    return '<html><body><h2>Etudiant ajouté !</h2><a href="/">Retour</a></body></html>'

# --- ENDPOINT POUR PROMETHEUS ---
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
