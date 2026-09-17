import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import json

df = pd.read_csv("data.csv")

encodeur_historique = LabelEncoder()
df["historique_enc"] = encodeur_historique.fit_transform(df["historique_credit"])

X = df[["revenu_annuel", "nombre_prets", "jours_retard_paiement", "historique_enc"]]
y = df["score_credit"]

# Division en ensemble d'entrainement (80%) et de test (20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

modele = DecisionTreeClassifier(random_state=0)
modele.fit(X_train, y_train)

y_pred = modele.predict(X_test)

metriques = {
    "accuracy": accuracy_score(y_test, y_pred),
    "precision": precision_score(y_test, y_pred, average="macro", zero_division=0),
    "recall": recall_score(y_test, y_pred, average="macro", zero_division=0),
    "f1": f1_score(y_test, y_pred, average="macro", zero_division=0),
    "taille_train": len(X_train),
    "taille_test": len(X_test),
}

joblib.dump(
    {"modele": modele, "encodeur": encodeur_historique},
    "data/model.joblib"
)

with open("data/metrics.json", "w") as f:
    json.dump(metriques, f, indent=2)

print("Modele entraine.")
print(metriques)