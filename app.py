import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, render_template_string, redirect, url_for
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# --- CONFIGURATION EMAIL ---
GMAIL_USER = 'melcham61@gmail.com'
GMAIL_PASSWORD = 'xuegwqbxmvjotxms' # Sans espaces pour éviter les erreurs d'authentification
RECEIVER_EMAIL = 'melcham61@gmail.com'

def send_notification(action, details):
    try:
        subject = f"🚨 INPTIC ALERT : {action}"
        body = f"Le système a enregistré une nouvelle activité :\n\nAction : {action}\nDétails : {details}\nStatut : Succès."

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = GMAIL_USER
        msg['To'] = RECEIVER_EMAIL

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, RECEIVER_EMAIL, msg.as_string())
        print(f"Email envoyé pour l'action : {action}")
    except Exception as e:
        print(f"Erreur d'envoi du mail : {e}")

# --- MÉTRIQUES PROMETHEUS ---
REQUESTS = Counter('inptic_requests_total', 'Requêtes HTTP', ['method', 'endpoint'])
STUDENTS_COUNT = Gauge('inptic_students_total', 'Nombre total d\'étudiants')

etudiants = [
    {"id": 1, "nom": "Mel Cham", "filiere": "SRI"},
    {"id": 2, "nom": "Alice Doe", "filiere": "ASUR"}
]
STUDENTS_COUNT.set(len(etudiants))

# --- INTERFACE DESIGN (NEON DASHBOARD) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>INPTIC - Secure Dashboard</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&display=swap');
        :root { --primary: #00ffcc; --bg: #0a0f16; --panel: #111a24; --danger: #ff3366; --warning: #ffcc00; }
        body { background: var(--bg); color: var(--primary); font-family: 'Rajdhani', sans-serif; display: flex; flex-direction: column; align-items: center; padding: 20px; margin: 0; }
        h1 { font-size: 2.5em; text-shadow: 0 0 10px var(--primary); margin-bottom: 5px; }
        .status { color: #888; margin-bottom: 30px; letter-spacing: 2px; }
        
        .container { background: var(--panel); border: 1px solid rgba(0, 255, 204, 0.3); padding: 30px; box-shadow: 0 8px 32px rgba(0, 255, 204, 0.1); border-radius: 12px; width: 90%; max-width: 1000px; }
        
        .form-group { display: flex; gap: 15px; margin-bottom: 30px; }
        input { flex: 1; background: rgba(0, 0, 0, 0.5); border: 1px solid var(--primary); color: white; padding: 12px; border-radius: 6px; font-family: 'Rajdhani', sans-serif; font-size: 1.1em; outline: none; transition: 0.3s; }
        input:focus { box-shadow: 0 0 10px rgba(0, 255, 204, 0.5); }
        
        button { background: rgba(0, 255, 204, 0.1); color: var(--primary); border: 1px solid var(--primary); padding: 12px 25px; border-radius: 6px; font-weight: bold; font-size: 1.1em; cursor: pointer; transition: 0.3s; font-family: 'Rajdhani', sans-serif; text-transform: uppercase; }
        button:hover { background: var(--primary); color: #000; box-shadow: 0 0 15px var(--primary); }
        button.btn-danger { color: var(--danger); border-color: var(--danger); background: rgba(255, 51, 102, 0.1); }
        button.btn-danger:hover { background: var(--danger); color: #fff; box-shadow: 0 0 15px var(--danger); }
        button.btn-edit { color: var(--warning); border-color: var(--warning); background: rgba(255, 204, 0, 0.1); }
        button.btn-edit:hover { background: var(--warning); color: #000; box-shadow: 0 0 15px var(--warning); }
        
        table { width: 100%; border-collapse: collapse; }
        th { background: rgba(0, 255, 204, 0.1); padding: 15px; text-align: left; border-bottom: 2px solid var(--primary); font-size: 1.2em; }
        td { padding: 15px; border-bottom: 1px solid rgba(0, 255, 204, 0.2); color: #e0e0e0; font-size: 1.1em; }
        tr:hover td { background: rgba(0, 255, 204, 0.05); }
        .actions { display: flex; gap: 10px; }

        /* Modal Styles */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(5px); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: var(--panel); border: 1px solid var(--warning); padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(255, 204, 0, 0.3); width: 400px; }
        .modal-content h2 { color: var(--warning); margin-top: 0; }
    </style>
</head>
<body>
    <h1>INPTIC CENTRAL COMMAND</h1>
    <div class="status">● GMAIL SMTP: SECURE & ACTIVE</div>
    
    <div class="container">
        <form action="/etudiants" method="post" class="form-group">
            <input type="text" name="nom" placeholder="Nom de l'étudiant" required>
            <input type="text" name="filiere" placeholder="Filière (ex: SRI)" required>
            <button type="submit">✚ AJOUTER</button>
        </form>

        <table>
            <thead>
                <tr><th>ID</th><th>NOM COMPLET</th><th>FILIÈRE</th><th>ACTIONS</th></tr>
            </thead>
            <tbody>
                {% for e in etudiants %}
                <tr>
                    <td style="color: var(--primary);">#{{ e.id }}</td>
                    <td>{{ e.nom }}</td>
                    <td>{{ e.filiere }}</td>
                    <td class="actions">
                        <button class="btn-edit" onclick="openModal({{ e.id }}, '{{ e.nom }}', '{{ e.filiere }}')">✎ MODIFIER</button>
                        <form action="/delete/{{ e.id }}" method="post" style="margin:0;">
                            <button type="submit" class="btn-danger">🗑 SUPPRIMER</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div id="editModal" class="modal">
        <div class="modal-content">
            <h2>Éditer l'étudiant</h2>
            <form id="editForm" method="post" style="display: flex; flex-direction: column; gap: 15px;">
                <input type="text" id="editNom" name="nom" required>
                <input type="text" id="editFiliere" name="filiere" required>
                <div style="display: flex; gap: 10px; justify-content: space-between;">
                    <button type="button" class="btn-danger" onclick="closeModal()">ANNULER</button>
                    <button type="submit" style="color:var(--warning); border-color:var(--warning);">SAUVEGARDER</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        function openModal(id, nom, filiere) {
            document.getElementById('editForm').action = '/edit/' + id;
            document.getElementById('editNom').value = nom;
            document.getElementById('editFiliere').value = filiere;
            document.getElementById('editModal').style.display = 'flex';
        }
        function closeModal() {
            document.getElementById('editModal').style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    REQUESTS.labels(method='GET', endpoint='/').inc()
    return render_template_string(HTML_TEMPLATE, etudiants=etudiants)

@app.route('/etudiants', methods=['POST'])
def add_etudiant():
    nom = request.form.get('nom')
    filiere = request.form.get('filiere')
    if nom and filiere:
        new_id = max([e['id'] for e in etudiants]) + 1 if etudiants else 1
        etudiants.append({"id": new_id, "nom": nom, "filiere": filiere})
        STUDENTS_COUNT.set(len(etudiants))
        send_notification("AJOUT", f"L'étudiant {nom} a été inscrit en {filiere}.")
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_etudiant(id):
    nom = request.form.get('nom')
    filiere = request.form.get('filiere')
    for e in etudiants:
        if e['id'] == id:
            ancien_nom = e['nom']
            e['nom'] = nom
            e['filiere'] = filiere
            send_notification("MODIFICATION", f"L'étudiant {ancien_nom} s'appelle maintenant {nom} (Filière: {filiere}).")
            break
    return redirect(url_for('home'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_etudiant(id):
    global etudiants
    target = next((e for e in etudiants if e['id'] == id), None)
    if target:
        etudiants = [e for e in etudiants if e['id'] != id]
        STUDENTS_COUNT.set(len(etudiants))
        send_notification("SUPPRESSION", f"L'étudiant {target['nom']} ({target['filiere']}) a été retiré du système.")
    return redirect(url_for('home'))

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
