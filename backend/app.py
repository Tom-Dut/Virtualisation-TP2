from flask import Flask, jsonify, request
from flask_cors import CORS
import os, json, time
import joblib
import psycopg2
import redis

app = Flask(__name__)
CORS(app)

modele_charge = joblib.load("data/model.joblib")

def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ.get("DB_NAME", "mtudb"),
        user=os.environ.get("DB_USER", "mtu"),
        password=os.environ.get("DB_PASSWORD", ""))

def get_cache():
    return redis.Redis(
        host=os.environ.get("CACHE_HOST", "cache"),
        port=6379,
        decode_responses=True)

def enregistrer(revenu, prets, retard, historique, prediction, source):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO predictions (revenu_annuel, nombre_prets, jours_retard, "
        "historique_credit, score_predit, source) VALUES (%s,%s,%s,%s,%s,%s)",
        (revenu, prets, retard, historique, prediction, source))
    conn.commit()
    conn.close()

@app.route("/api/predire")
def predire():
    revenu = float(request.args.get("revenu"))
    prets = int(request.args.get("prets"))
    retard = int(request.args.get("retard"))
    historique = request.args.get("historique")

    cache = get_cache()
    cle = f"prediction:{revenu}:{prets}:{retard}:{historique}"
    resultat_cache = cache.get(cle)

    if resultat_cache:
        data = json.loads(resultat_cache)
        data["source"] = "cache"
        enregistrer(
            revenu,
            prets,
            retard,
            historique,
            data["score_predit"],
            "cache")
        return jsonify(data)

    time.sleep(1)  # simule un modele plus lourd en production

    historique_enc = modele_charge["encodeur"].transform([historique])[0]

    prediction = modele_charge["modele"].predict(
        [[revenu, prets, retard, historique_enc]])[0]

    resultat = {
        "revenu": revenu,
        "prets": prets,
        "retard": retard,
        "historique": historique,
        "score_predit": prediction,
        "source": "calcul"
    }

    cache.setex(cle, 60, json.dumps(resultat))

    enregistrer(
        revenu,
        prets,
        retard,
        historique,
        prediction,
        "calcul")

    return jsonify(resultat)

@app.route("/api/performance")
def performance():
    with open("data/metrics.json") as f:
        return jsonify(json.load(f))

@app.route("/api/historique")
def historique():
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT revenu_annuel, nombre_prets, jours_retard, historique_credit, "
        "score_predit, source FROM predictions ORDER BY id DESC LIMIT 20")

    rows = cur.fetchall()
    conn.close()

    return jsonify([
        {
            "revenu": r[0],
            "prets": r[1],
            "retard": r[2],
            "historique": r[3],
            "score_predit": r[4],
            "source": r[5]
        }
        for r in rows
    ])

@app.route("/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)