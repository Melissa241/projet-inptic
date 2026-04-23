from flask import Flask, jsonify, request, render_template_string, redirect, url_for
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# --- MÉTRIQUES ---
REQUESTS = Counter('inptic_requests_total', 'Requêtes HTTP', ['method', 'endpoint'])
STUDENTS_COUNT = Gauge('inptic_students_total', 'Nombre total d\'étudiants')

etudiants = [
    {"id": 1, "nom": "Mel Cham", "filiere": "SRI"},
    {"id": 2, "nom": "Alice Doe", "filiere": "ASUR"}
]
STUDENTS_COUNT.set(len(etudiants))

# --- INTERFACE HTML/CSS MYSTIFIANTE ---
# Utilisation de Google Fonts et de styles néon
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>INPTIC - Matrix Student Management</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400&display=swap');
        
        body { 
            background: #0d0d0d; color: #00ff41; font-family: 'Roboto', sans-serif; 
            display: flex; flex-direction: column; align-items: center; min-height: 100vh; margin: 0;
        }
        h1 { font-family: 'Orbitron', sans-serif; text-shadow: 0 0 10px #00ff41; margin-top: 30px; }
        
        .container { background: #1a1a1a; padding: 25px; border-radius: 15px; border: 1px solid #00ff41; 
                     box-shadow: 0 0 20px rgba(0, 255, 65, 0.2); width: 80%; max-width: 800px; margin-top: 20px; }
        
        input { background: #333; border: 1px solid #00ff41; color: white; padding: 10px; border-radius: 5px; margin: 5px; }
        button { background: #00ff41; color: black; border: none; padding: 10px 20px; font-weight: bold; 
                 border-radius: 5px; cursor: pointer; transition: 0.3s; font-family: 'Orbitron', sans-serif; }
        button:hover { background: #008f11; box-shadow: 0 0 15px #00ff41; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 20px; color: white; }
        th, td { border-bottom: 1px solid #333; padding: 12px; text-align: left; }
        th { color: #00ff41; text-transform: uppercase; font-size: 0.8em; }
        
        .btn-delete { background: #ff3131; margin-left: 5px; color: white; }
        .btn-delete:hover { background: #b90000; box-shadow: 0 0 15px #ff3131; }
        .btn-edit { background: #39ff14; color: black; }

        .stats-link { margin-top: 20px; color: #888; text-decoration: none; font-size: 0.9em; }
        .stats-link:hover { color: #00ff41; }
    </style>
</head>
<body>
    <h1>INPTIC SYSTEM ACCESS</h1>
    
    <div class="container">
        <h3>INSCRIPTION NOUVEL UNITÉ</h3>
        <form action="/etudiants" method="post">
            <input type="text" name="nom" placeholder="IDENTITÉ" required>
            <input type="text" name="filiere" placeholder="SECTEUR / FILIÈRE" required>
            <button type="submit">INJECTER</button>
        </form>

        <table>
            <thead>
                <tr>
                    <th>ID</th><th>NOM</th><th>FILIÈRE</th><th>ACTIONS</th>
                </tr>
            </thead>
            <tbody>
                {% for e in etudiants %}
                <tr>
                    <td>#{{ e.id }}</td>
                    <td>{{ e.nom }}</td>
                    <td>{{ e.filiere }}</td>
                    <td>
                        <form action="/update/{{ e.id }}" method="post" style="display:inline;">
                            <input type="text" name="nom" placeholder="Nouveau nom" style="font-size: 0.7em; padding: 5px; width: 80px;">
                            <button type="submit" class="btn-edit" style="padding: 5px 10px; font-size: 0.6em;">MOD</button>
                        </form>
                        <a href="/delete/{{ e.id }}"><button class="btn-delete" style="padding: 5px 10px; font-size: 0.6em;">X</button></a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <a href="http://192.168.23.129:3000" target="_blank" class="stats-link">CONSULTER LES MÉTRIQUES GRAFANA</a>
</body>
</html>
"""

@app.route('/')
def home():
    REQUESTS.labels(method='GET', endpoint='/').inc()
    return render_template_string(HTML_TEMPLATE, etudiants=etudiants)

@app.route('/etudiants', methods=['POST'])
def add_etudiant():
    REQUESTS.labels(method='POST', endpoint='/etudiants').inc()
    nom = request.form.get('nom')
    filiere = request.form.get('filiere')
    if nom and filiere:
        nouveau_id = max([e['id'] for e in etudiants]) + 1 if etudiants else 1
        etudiants.append({"id": nouveau_id, "nom": nom, "filiere": filiere})
        STUDENTS_COUNT.set(len(etudiants))
    return redirect(url_for('home'))

@app.route('/delete/<int:id>')
def delete_etudiant(id):
    global etudiants
    REQUESTS.labels(method='GET', endpoint='/delete').inc()
    etudiants = [e for e in etudiants if e['id'] != id]
    STUDENTS_COUNT.set(len(etudiants))
    return redirect(url_for('home'))

@app.route('/update/<int:id>', methods=['POST'])
def update_etudiant(id):
    REQUESTS.labels(method='POST', endpoint='/update').inc()
    nouveau_nom = request.form.get('nom')
    for e in etudiants:
        if e['id'] == id and nouveau_nom:
            e['nom'] = nouveau_nom
    return redirect(url_for('home'))

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
