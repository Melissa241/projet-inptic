from flask import Flask, jsonify, request
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# --- MÉTRIQUES POUR GRAFANA ---
# 1. Un compteur pour le nombre total de requêtes (ne fait qu'augmenter)
REQUESTS = Counter('inptic_requests_total', 'Total des requêtes HTTP', ['method', 'endpoint'])
# 2. Une jauge pour le nombre d'étudiants (peut monter et descendre, parfait pour les graphiques !)
STUDENTS_COUNT = Gauge('inptic_students_total', 'Nombre total d\'étudiants dans la base')

# Base de données temporaire en mémoire
etudiants = [
    {"id": 1, "nom": "Mel Cham", "filiere": "SRI"},
    {"id": 2, "nom": "Alice Doe", "filiere": "ASUR"}
]

# On initialise la jauge avec le nombre d'étudiants actuels (2)
STUDENTS_COUNT.set(len(etudiants))

@app.route('/')
def home():
    REQUESTS.labels(method='GET', endpoint='/').inc()
    # C'est CE texte que tu pourras modifier plus tard pour tester Git/Jenkins
    return jsonify({"message": "Version 1.0 - API INPTIC en ligne !"})

@app.route('/etudiants', methods=['GET'])
def get_etudiants():
    REQUESTS.labels(method='GET', endpoint='/etudiants').inc()
    return jsonify(etudiants)

@app.route('/etudiants', methods=['POST'])
def add_etudiant():
    REQUESTS.labels(method='POST', endpoint='/etudiants').inc()

    # On ajoute un faux étudiant juste pour tester la route
    nouvel_etudiant = {"id": len(etudiants) + 1, "nom": "Nouveau", "filiere": "Dev"}
    etudiants.append(nouvel_etudiant)

    # On met à jour la métrique pour que Grafana réagisse !
    STUDENTS_COUNT.set(len(etudiants))

    return jsonify({"message": "Étudiant ajouté avec succès !", "total": len(etudiants)}), 201

# --- ENDPOINT OBLIGATOIRE POUR PROMETHEUS ---
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    # Écoute sur toutes les interfaces pour Docker
    app.run(host='0.0.0.0', port=5000)
