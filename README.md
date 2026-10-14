# 📊 Analyse du marché de l'alternance data / IA

Quelles compétences les entreprises demandent-elles vraiment pour une alternance en data ?
Ce projet analyse des offres d'alternance data / IA en Île-de-France et présente les résultats dans un dashboard interactif.

## Pipeline

1. **Collecte** : offres d'alternance data / IA publiées sur Indeed (Île-de-France)
2. **Nettoyage** (`analyse.py`, pandas) : harmonisation des colonnes, suppression des doublons et des offres incomplètes
3. **Détection des compétences** : expressions régulières sur la description de chaque offre (Python, SQL, Power BI, LLM…)
4. **Dashboard** (`app.py`, Streamlit + Plotly) : top des compétences, filtres, comparaison de son profil au marché

## Premiers résultats (échantillon de 18 offres)

- **Python** est cité dans 56 % des offres, devant la **data visualisation** (50 %)
- La **communication** arrive 3e (44 %), devant SQL : les entreprises veulent des profils capables d'expliquer leurs résultats
- **1 offre sur 3** trouvée en cherchant « alternance » est en réalité un **stage**

## Lancer le projet

```bash
pip install -r requirements.txt
python analyse.py
streamlit run app.py
```

## Prochaines étapes

- Automatiser la collecte via l'API France Travail (OAuth2)
- Élargir l'échantillon et suivre l'évolution des compétences dans le temps
