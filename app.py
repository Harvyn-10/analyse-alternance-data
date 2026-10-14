import pandas as pd
import plotly.express as px
import streamlit as st

# ---------- CONFIGURATION DE LA PAGE ----------
st.set_page_config(page_title="Marché de l'alternance data", page_icon="📊", layout="wide")

COULEUR = "#2F5BEA"  # une seule couleur pour tous les graphiques : plus lisible


# ---------- CHARGEMENT DES DONNÉES ----------
# @st.cache_data : Streamlit garde le résultat en mémoire, le fichier n'est lu qu'une fois
@st.cache_data
def charger_donnees():
    df = pd.read_csv("offres_propres.csv")

    # Les colonnes de compétences sont celles qui contiennent des Vrai/Faux
    competences = [col for col in df.columns if df[col].dtype == bool]

    # On classe chaque offre dans une famille de poste à partir de son titre
    def famille(titre):
        t = titre.lower()
        if "analyst" in t:
            return "Data Analyst"
        if "scien" in t:
            return "Data Scientist"
        if "ia" in t.replace("/", " ").split() or "chatbot" in t:
            return "IA / IA générative"
        return "Autre"

    df["famille"] = df["titre"].apply(famille)

    # Vraie alternance = le contrat ne commence pas par "Stage"
    df["vraie_alternance"] = ~df["contrat"].str.lower().str.startswith("stage")
    return df, competences


df, COMPETENCES = charger_donnees()


# ---------- EN-TÊTE ----------
st.title("📊 Quelles compétences pour décrocher une alternance en data ?")
st.caption(
    "Analyse d'offres d'alternance data / IA en Île-de-France collectées sur Indeed. "
    "Pipeline : collecte → nettoyage (pandas) → détection des compétences (regex) → dashboard (Streamlit)."
)


# ---------- FILTRES (barre latérale) ----------
st.sidebar.header("Filtres")
familles = st.sidebar.multiselect(
    "Famille de poste",
    options=sorted(df["famille"].unique()),
    default=sorted(df["famille"].unique()),
)
seulement_alternance = st.sidebar.checkbox("Exclure les stages", value=False)

filtre = df[df["famille"].isin(familles)]
if seulement_alternance:
    filtre = filtre[filtre["vraie_alternance"]]

if filtre.empty:
    st.warning("Aucune offre ne correspond à ces filtres.")
    st.stop()


# ---------- CHIFFRES CLÉS ----------
top = (filtre[COMPETENCES].mean() * 100).round(0).sort_values(ascending=False)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Offres analysées", len(filtre))
c2.metric("Entreprises", filtre["entreprise"].nunique())
c3.metric("Vraies alternances", f"{filtre['vraie_alternance'].mean() * 100:.0f} %")
c4.metric("Compétence n°1", top.index[0], f"{top.iloc[0]:.0f} % des offres", delta_color="off")


# ---------- GRAPHIQUE : TOP COMPÉTENCES ----------
st.subheader("Les compétences les plus demandées")
top_df = top[top > 0].head(12).reset_index()
top_df.columns = ["Compétence", "Pourcentage"]

fig = px.bar(
    top_df.sort_values("Pourcentage"),
    x="Pourcentage",
    y="Compétence",
    orientation="h",
    text="Pourcentage",
    color_discrete_sequence=[COULEUR],
)
fig.update_traces(texttemplate="%{text:.0f} %", textposition="outside", cliponaxis=False)
fig.update_layout(xaxis_title="% des offres qui la citent", yaxis_title="", height=450, margin=dict(l=0, r=40))
st.plotly_chart(fig, width="stretch")


# ---------- MON PROFIL FACE AU MARCHÉ ----------
st.subheader("🎯 Mon profil face au marché")
mes_competences = st.multiselect(
    "Sélectionne les compétences que tu maîtrises :",
    options=COMPETENCES,
    default=[c for c in ["Python", "SQL", "JavaScript", "API", "Git", "Communication"] if c in COMPETENCES],
)

if mes_competences:
    # Pour chaque offre : part des compétences demandées que je possède
    demandees = filtre[COMPETENCES].sum(axis=1)
    possedees = filtre[mes_competences].sum(axis=1)
    couverture = (possedees / demandees.where(demandees > 0)).fillna(0)

    a, b = st.columns(2)
    a.metric("Couverture moyenne des offres", f"{couverture.mean() * 100:.0f} %")
    a.caption("En moyenne, part des compétences demandées par une offre que tu possèdes déjà.")

    manquantes = top.drop(mes_competences, errors="ignore")
    manquantes = manquantes[manquantes > 0].head(3)
    b.markdown("**À travailler en priorité :**")
    for nom, pct in manquantes.items():
        b.markdown(f"- {nom} : demandée dans {pct:.0f} % des offres")


# ---------- RÉPARTITIONS ----------
g1, g2 = st.columns(2)

with g1:
    st.subheader("Familles de poste")
    fam = filtre["famille"].value_counts().reset_index()
    fam.columns = ["Famille", "Offres"]
    fig2 = px.bar(fam, x="Famille", y="Offres", text="Offres", color_discrete_sequence=[COULEUR])
    fig2.update_layout(xaxis_title="", yaxis_title="Nombre d'offres", height=350)
    st.plotly_chart(fig2, width="stretch")

with g2:
    st.subheader("Stage ou vraie alternance ?")
    typ = filtre["vraie_alternance"].map({True: "Alternance", False: "Stage"}).value_counts().reset_index()
    typ.columns = ["Type", "Offres"]
    fig3 = px.bar(typ, x="Type", y="Offres", text="Offres", color_discrete_sequence=[COULEUR])
    fig3.update_layout(xaxis_title="", yaxis_title="Nombre d'offres", height=350)
    st.plotly_chart(fig3, width="stretch")
    st.caption("Une recherche « alternance » sur Indeed renvoie aussi des stages : il faut vérifier chaque offre.")


# ---------- TABLEAU DES OFFRES ----------
st.subheader("Les offres")
st.dataframe(
    filtre[["titre", "entreprise", "ville", "contrat", "famille", "lien"]],
    column_config={"lien": st.column_config.LinkColumn("Lien", display_text="Voir l'offre")},
    hide_index=True,
    width="stretch",
)

st.caption("Prochaine étape : automatiser la collecte via l'API France Travail et suivre l'évolution dans le temps.")
