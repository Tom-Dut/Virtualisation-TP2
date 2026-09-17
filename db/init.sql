CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    revenu_annuel NUMERIC NOT NULL,
    nombre_prets INTEGER NOT NULL,
    jours_retard INTEGER NOT NULL,
    historique_credit TEXT NOT NULL,
    score_predit TEXT NOT NULL,
    source TEXT NOT NULL,
    cree_le TIMESTAMP DEFAULT NOW()
);