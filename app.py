from flask import Flask, jsonify, request, render_template_string
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# --- MÉTRIQUES ---
REQUESTS = Counter('inptic_requests_total', 'Total des requêtes', ['method', 'endpoint'])
STUDENTS_COUNT = Gauge('inptic_students_total', 'Nombre total d\'étudiants')

etudiants = [
    {"id": 1, "nom": "Mel Cham", "filiere": "SRI"},
    {"id": 2, "nom": "Alice Doe", "filiere": "ASUR"}
]
STUDENTS_COUNT.set(len(etudiants))

# --- INTERFACE HTML AVEC FORMULAIRE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>INPTIC - Gestion</title>
    <style>
        body { font-family: sans-serif; text-align: center; background: #f4f7f6; padding: 50px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block; }
        input { padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #219150; }
        .stats { margin-top: 20px; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="card">
        <h1 style="color: #2c3e50;">🎓 Inscrire un Étudiant</h1>
        <form action="/etudiants" method="post">
            <input type="text" name="nom" placeholder="Nom de l'étudiant" required>
            <input type="text" name="filiere" placeholder="Filière (ex: SRI, ASUR)" required>
            <br><br>
            <button type="submit">Enregistrer l'étudiant</button>
        </form>
        <div class="stats">
            <a href="/etudiants">Voir la liste JSON</a> | 
            <a href="http://192.168.23.129:3000">Voir Grafana</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    REQUESTS.labels(method='GET', endpoint='/').inc()
    return render_template_string(HTML_TEMPLATE)

@app.route('/etudiants', methods=['GET'])
def get_etudiants():
    REQUESTS.labels(method='GET', endpoint='/etudiants').inc()
    return jsonify(etudiants)

@app.route('/etudiants', methods=['POST'])
def add_etudiant():
    REQUESTS.labels(method='POST', endpoint='/etudiants').inc()

    # On récupère les données saisies dans le formulaire
    nom = request.form.get('nom')
    filiere = request.form.get('filiere')

    if nom and filiere:
        nouveau_id = len(etudiants) + 1
        etudiants.append({"id": nouveau_id, "nom": nom, "filiere": filiere})
        STUDENTS_COUNT.set(len(etudiants))

    return f'<html><body style="text-align:center;"><h2>L\'étudiant {nom} a été ajouté !</h2><a href="/">Retourner au formulaire</a></body></html>'

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
