import os
import requests
from flask import Flask, Response
from icalendar import Calendar, Event
from datetime import datetime, timedelta

app = Flask(__name__)

ED_USER = os.environ.get("ED_USER")
ED_PASS = os.environ.get("ED_PASS")

def get_edt():
    # Login URL avec version
    login_url = "https://api.ecoledirecte.com/v3/login.awp?v=4.63.1"

    # JSON corrigé pour éviter "Format JSON invalide"
    data = {
        "identifiant": ED_USER,
        "motdepasse": ED_PASS,
        "isReLogin": False,
        "device": "web"
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    # Requête de login
    resp = requests.post(login_url, json=data, headers=headers)
    print("RAW LOGIN RESPONSE:", resp.text)  # debug

    j = resp.json()
    if "data" not in j or "accounts" not in j["data"] or not j["data"]["accounts"]:
        raise Exception(f"Login failed: {j}")  # stop si pas d’élève

    eleve_id = j["data"]["accounts"][0]["id"]
    token = j["token"]

    # Requête emploi du temps
    edt_url = f"https://api.ecoledirecte.com/v3/E/{eleve_id}/emploidutemps.awp?v=4.63.1&verbe=get"
    today = datetime.today()
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    payload = {
        "dateDebut": start_date,
        "dateFin": end_date,
        "avecTrous": False
    }

    headers_edt = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "X-Token": token,
    }

    resp = requests.post(edt_url, json=payload, headers=headers_edt)
    print("RAW EDT RESPONSE:", resp.text)  # debug

    edt_json = resp.json()

    # Création du calendrier iCal
    cal = Calendar()
    for cours in edt_json.get("data", []):
        event = Event()
        event.add("summary", cours.get("matiere", "Cours"))
        start = datetime.strptime(cours["start_date"], "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(cours["end_date"], "%Y-%m-%d %H:%M:%S")
        event.add("dtstart", start)
        event.add("dtend", end)
        event.add("location", cours.get("salle", ""))
        cal.add_component(event)

    return cal

@app.route("/")
def ics():
    cal = get_edt()
    return Response(cal.to_ical(), mimetype="text/calendar")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
