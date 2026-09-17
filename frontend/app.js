const API_BASE = "http://localhost:5000";

async function predire() {
    const revenu = document.getElementById("revenu").value;
    const prets = document.getElementById("prets").value;
    const retard = document.getElementById("retard").value;
    const historique = document.getElementById("historique").value;

    const url = `${API_BASE}/api/predire?revenu=${revenu}&prets=${prets}`
              + `&retard=${retard}&historique=${historique}`;

    const reponse = await fetch(url);
    const data = await reponse.json();

    document.getElementById("resultat").textContent =
        `Score predit : ${data.score_predit} (source : ${data.source})`;
}

async function chargerHistorique() {
    const reponse = await fetch(API_BASE + "/api/historique");
    const lignes = await reponse.json();

    const liste = document.getElementById("historiqueListe");
    liste.innerHTML = "";

    lignes.forEach(l => {
        const li = document.createElement("li");

        li.textContent =
            `revenu ${l.revenu}, ${l.prets} prets, ${l.retard}j retard, `
            + `historique ${l.historique} -> ${l.score_predit} (${l.source})`;

        liste.appendChild(li);
    });
}