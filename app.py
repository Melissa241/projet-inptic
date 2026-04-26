import smtplib
from email.mime.text import MIMEText
from flask import Flask, jsonify, request, render_template_string, redirect, url_for
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# --- CONFIGURATION EMAIL ---
GMAIL_USER = 'melcham61@gmail.com'  # Remplacer par ton adresse Gmail
GMAIL_PASSWORD = 'xueg wqbx mvjo txms'  # Remplacer par ton mot de passe d'application
RECEIVER_EMAIL = 'melcham61@gmail.com' # Où tu recevras les alertes

def send_notification(action, student_name):
    try:
        subject = f"🚨 ALERTE SYSTÈME : {action}"
        body = f"Le système INPTIC détecte une modification :\nAction : {action}\nÉtudiant : {student_name}\nStatut : Opération Réussie."
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = GMAIL_USER
        msg['To'] = RECEIVER_EMAIL

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, RECEIVER_EMAIL, msg.as_string())
        print("Email envoyé avec succès !")
    except Exception as e:
        print(f"Erreur lors de l'envoi du mail : {e}")

# --- MÉTRIQUES PROMETHEUS ---
REQUESTS = Counter('inptic_requests_total', 'Requêtes HTTP', ['method', 'endpoint'])
STUDENTS_COUNT = Gauge('inptic_students_total', 'Nombre total d\'étudiants')

etudiants = [
    {"id": 1, "nom": "Mel Cham", "filiere": "SRI"},
    {"id": 2, "nom": "Alice Doe", "filiere": "ASUR"}
]
STUDENTS_COUNT.set(len(etudiants))

# --- INTERFACE MYSTIFIANTE (MATRIX) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>INPTIC - Secure System</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        body { background: #000; color: #0f0; font-family: 'Orbitron', sans-serif; display: flex; flex-direction: column; align-items: center; padding: 20px; }
        .container { border: 2px solid #0f0; padding: 30px; box-shadow: 0 0 20px #0f0; border-radius: 10px; width: 80%; max-width: 900px; }
        input { background: #111; border: 1px solid #0f0; color: #0f0; padding: 10px; margin-bottom: 10px; width: 200px; }
        button { background: #0f0; color: #000; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer; transition: 0.5s; }
        button:hover { background: #000; color: #0f0; border: 1px solid #0f0; box-shadow: 0 0 15px #0f0; }
        table { width: 100%; margin-top: 30px; border-collapse: collapse; }
        th, td { border: 1px solid #0f0; padding: 10px; text-align: left; }
        .alert-msg { color: #f00; font-size: 0.8em; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>INPTIC REAL-TIME MONITORING</h1>
    <div class="container">
        <p class="alert-msg">>> SYSTEM NOTIFICATION: EMAILS ACTIVE ON PORT 465</p>
        <form action="/etudiants" method="post">
            <input type="text" name="nom" placeholder="NOM ÉTUDIANT" required>
            <input type="text" name="filiere" placeholder="FILIÈRE" required>
            <button type="submit">AJOUTER & NOTIFIER</button>
        </form>

        <table>
            <thead>
                <tr><th>ID</th><th>NOM</th><th>FILIÈRE</th><th>ACTION</th></tr>
            </thead>
            <tbody>
                {% for e in etudiants %}
                <tr>
                    <td>#{{ e.id }}</td>
                    <td>{{ e.nom }}</td>
                    <td>{{ e.filiere }}</td>
                    <td><a href="/delete/{{ e.id }}"><button style="background:#f00; color:white;">SUPPRIMER</button></a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    <p style="margin-top:20px; font-size:0.7em;">Connected to: Prometheus | Grafana | Gmail SMTP</p>
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
        # ENVOI DU MAIL
        send_notification("AJOUT ÉTUDIANT", f"{nom} ({filiere})")
    return redirect(url_for('home'))

@app.route('/delete/<int:id>')
def delete_etudiant(id):
    global etudiants
    target = next((e for e in etudiants if e['id'] == id), None)
    if target:
        etudiants = [e for e in etudiants if e['id'] != id]
        STUDENTS_COUNT.set(len(etudiants))
        # ENVOI DU MAIL
        send_notification("SUPPRESSION ÉTUDIANT", target['nom'])
    return redirect(url_for('home'))

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
