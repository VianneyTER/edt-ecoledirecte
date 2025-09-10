import requests
import datetime
from ics import Calendar, Event
from flask import Flask, Response
import os

app = Flask(__name__)

# Identifiants stockés dans Render (variables d'environnement)
USER = os.environ.get("ED_USER")
PWD = os.environ.get("ED_PASS")

def get_edt():
    # 1. Connexion à l’API
    login_url = "https://api.ecoledirecte.com/v3/login.awp"
    data = {"identifiant": USER, "motdepasse": PWD, "isReLogin": False}
    resp = requests.post(login_url, json=data)
    token = resp.json()["token"]
    eleve_id = resp.json()["data"]["accounts"][0]["id"]

    # 2. Dates de la semaine courante
    today = datetime.date.today()
    lundi = today - datetime.timedelta(days=today.weekday())
    dimanche = lundi + datetime.timedelta(days=6)

    # 3. Récupérer EDT
    edt_url = f"https://api.ecoledirecte.com/v3/E/{eleve_id}/emploidutemps.awp?verbe=get"
    headers = {"X-Token": token}
    payload = {"dateDebut": str(lundi), "dateFin": str(dimanche)}
    resp = requests.post(edt_url, headers=headers, json=payload)
    cours = resp.json()["data"]

    # 4. Générer calendrier ICS
    cal = Calendar()
    for c in cours:
        e = Event()
        e.name = c.get("matiere", "Cours")
        e.begin = c["start_date"]
        e.end = c["end_date"]
        e.location = c.get("salle", "")
        cal.events.add(e)

    return str(cal)

@app.route("/")
def ics():
    cal = get_edt()
    return Response(cal, mimetype="text/calendar")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
