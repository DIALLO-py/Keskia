from sentence_transformers import SentenceTransformer, util # recherche de simularite avec sentence transformer car les mots clef sont pas aser..
import torch
import pandas as pd
# https://huggingface.co/mixedbread-ai/mxbai-embed-large-v1
model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1')
category_sentences = {
    "Culture": "les musées, mosquee, eglise,cynagogue,Librairie,bibliotheque",
    "Enseignement": "Établissements d'enseignement et activités éducatives. ecole, college, lycee, creche",
    "Sante": "Services de santé tels que hôpitaux, médecins et pharmacies, pediatre,clinique,Docteur ",
    "Aide sociale": "Associations, centres sociaux, et aide sociale comme emaus.",
    "Services Publics, Administration": "Services administratifs et institutions publiques, Administration locale, Commissariat de police, Mairie, Service d'assainissement, Centre des impôts, organisation, Agence pour l'emploi travail, transport,gare, bus",
    "Commerce et Restauration": "Magasins, restaurants, marche, supermarche, hôtels, Magasin de matériaux de construction, Agence immobilière, Hôtel",
    "Sport et loisir": "Activités sportives et de loisirs comme les gymnases et les parcs,Salle de spectacles,Inclut Complexe sportif, Terrain de football, Salle de fitness, Piscine municipale, Parc de loisirs,salle de fete et de reception,Le Petit Gibus,cinéma,les théâtres"
}

def classify_with_sentence_similarity(text):
    if pd.isna(text) or text.strip() == '':
        return "Autre"  # Ou une autre catégorie par défaut si on a pas
    text_embedding = model.encode(text, convert_to_tensor=True)
    category_embeddings = {cat: model.encode(desc, convert_to_tensor=True) for cat, desc in category_sentences.items()}
    similarities = {cat: util.pytorch_cos_sim(text_embedding, emb).item() for cat, emb in category_embeddings.items()}
    return max(similarities, key=similarities.get)
import streamlit as st
import pandas as pd

# Configuration du style du DataFrame
def style_specific_columns(df):
    # Définir les colonnes à styliser (toutes sauf la première)
    columns = df.columns[1:]  # Exclut la première colonne

    # Appliquer le style
    styled_df = df.style.apply(
        lambda x: ['background-color: green' if v == x.max() else 'background-color: red' if v == x.min() else '' for v in x],
        subset=columns
    ).set_properties(**{'text-align': 'center'}, subset=columns) \
     .set_properties(**{'text-align': 'left'}, subset=[df.columns[0]]) \
     .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])

    return styled_df
