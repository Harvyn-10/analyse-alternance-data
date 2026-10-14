import pandas as pd

# ---------- 1. CHARGER LES DONNÉES ----------
# sep=None : pandas devine tout seul si c'est "," ou ";"
df = pd.read_csv("offres.csv", sep=None, engine="python", encoding="utf-8-sig")

# ---------- 2. NETTOYER ----------
# Noms de colonnes en minuscules, sans espaces autour
df.columns = df.columns.str.strip().str.lower()

# On enlève les lignes sans description et les doublons
df = df.dropna(subset=["description"])
df = df.drop_duplicates(subset=["titre", "entreprise"])

# On nettoie le texte des colonnes principales
for col in ["titre", "entreprise", "ville"]:
    df[col] = df[col].astype(str).str.strip()

print(f"{len(df)} offres après nettoyage")

# ---------- 3. DÉTECTER LES COMPÉTENCES ----------
# Dictionnaire : nom affiché -> motif recherché dans le texte
COMPETENCES = {
    "Python": r"\bpython\b",
    "SQL": r"\bsql\b",
    "Power BI": r"power\s?bi",
    "Tableau": r"\btableau\b(?! de bord)",
    "Excel": r"\bexcel\b",
    "Machine Learning": r"machine learning|apprentissage automatique",
    "Deep Learning": r"deep learning",
    "IA générative / LLM": r"\bllm\b|ia g[ée]n[ée]rative|genai|chatgpt|gpt",
    "Pandas": r"\bpandas\b",
    "Scikit-learn": r"scikit|sklearn",
    "TensorFlow / PyTorch": r"tensorflow|pytorch",
    "Spark": r"\bspark\b",
    "Cloud (AWS/Azure/GCP)": r"\baws\b|azure|\bgcp\b|google cloud",
    "Git": r"\bgit\b|github|gitlab",
    "Docker": r"docker",
    "API": r"\bapi\b",
    "Statistiques": r"statisti",
    "Data visualisation": r"visuali[sz]ation|dataviz|dashboard|tableaux? de bord",
    "JavaScript": r"javascript|\bjs\b",
    "Communication": r"communication|vulgaris",
}

texte = df["description"].str.lower()
for nom, motif in COMPETENCES.items():
    # True si la compétence apparaît dans l'offre
    df[nom] = texte.str.contains(motif, regex=True)

# ---------- 4. ANALYSER ----------
top = (
    df[list(COMPETENCES)].sum()          # nb d'offres qui citent chaque compétence
    .sort_values(ascending=False)
    .to_frame("nb_offres")
)
top["pourcentage"] = (top["nb_offres"] / len(df) * 100).round(0)

print("\nTop compétences demandées :")
print(top.head(10))

print("\nTop villes :")
print(df["ville"].value_counts().head(5))

# On sauvegarde le résultat propre pour le dashboard
df.to_csv("offres_propres.csv", index=False)
print("\nFichier offres_propres.csv créé ✅")
