#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  5 16:02:45 2024

@author: ibrahima-bailodiallo
"""

import pandas as pd
import folium
from folium.features import CustomIcon
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static


import pandas as pd
import numpy as np

import io
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px    # pour avoir des plots inter-actif

from  wordcloud import WordCloud


# Chargement des données
place_name = pd.read_csv('place_name.csv')
place_name['rating_x_reviews'] = place_name['rating'] * place_name['reviews']
df_filtre = pd.read_csv('filtered.csv')




#""" diviser en 4 page"""
st.sidebar.title("AGOR'APP")
pages = ["Acceuil"," Carte","Général Tendance", "Détail Tendance", "WorldCloud Catégorie ", "WorldCloud Infrastructure"]
page = st.sidebar.radio("Aller vers ",pages)



if page == pages[0]:
    
    st.write("### Renforcez vos décisions, votre réputation avec des informations exploitables ! ")
    
    st.write("""Notre application Web AGOR'APP exploite l'analyse des tendances et le suivi des sentiments pour fournir des indicateurs clés, vous permettant de prendre des décisions éclairées en toute confiance""")
    
    st.image("AGORApp.png")
 
elif page == pages[2]:
    
    # Regroupement et calcul des moyennes pondérées
    results = place_name.groupby('Grande Categorie').agg(total_weighted_rating=('rating_x_reviews', 'sum'),total_reviews=('reviews', 'sum')).reset_index()
    results['weighted_average_rating'] = (results['total_weighted_rating'] / results['total_reviews']).round(2)
    
    # Calcul du nombre d'entrées pour chaque catégorie
    category_counts = place_name['Grande Categorie'].value_counts().rename('infrastructure_count').reset_index()
    category_counts.columns = ['Grande Categorie', 'infrastructure_count']
    results = pd.merge(results, category_counts, on='Grande Categorie')
    
    # Affichage des résultats
    st.write("### Tableau de classification des infrastructures par catégorie")
    results = results.drop("total_weighted_rating", axis=1)                    #Enlever la variable "total_weighted_rating"
    st.dataframe(results)


    ########### Evolution de la moyenne des avis 
    st.write("### Évolution des avis ")
    
    place_name.columns = ['place_id', 'name', 'main_category', 'rating moyen', 'total reviews', 'address',
           'link', 'categories', 'description', 'Grande Categorie',
           'rating_x_reviews','latitude', 'longitude']
    df_filtre = pd.read_csv('filtered.csv')
    df_merge = pd.merge(df_filtre,place_name, on='place_id',how='left')
    df_merge = df_merge[df_merge.address.str.contains('Trappes',na=False)]
    
    df_merge = df_merge[df_merge['total reviews']>10.]
    ## graphque
    annual_rating_average = df_merge.groupby('année')['rating moyen'].mean().reset_index()
        # Création du graphique
    fig1, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=annual_rating_average, x='année', y='rating moyen', marker='o', label='Moyenne Générale', ax=ax)
    plt.title('Évolution de la moyenne des avis par année')
    plt.xlabel('Année')
    plt.ylabel('Moyenne')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    st.pyplot(fig1)

  
    #Evololution du nombre d'avis 
    ## count graph
    annual_rating_count = df_merge.groupby('année')['rating moyen'].count().reset_index()

    # Création du graphique
    fig2, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=annual_rating_count, x='année', y='rating moyen', marker='o',label='Nombre Avis',ax=ax)
    plt.title("Évolution du nombre d'avis par année")
    plt.xlabel('Année')
    plt.ylabel("Nombre d'avis")
    plt.grid(True)
    plt.xticks(rotation=25)
    plt.tight_layout()
    st.pyplot(fig2)

elif page == pages[1]:
    
    st.write("## Carte inter-active")
    
    map_width, map_height = 1500, 700  # Taille en pixels

    # Création d'une carte centrée sur Trappes avec une taille spécifique
    mymap = folium.Map(
        location=[48.77413, 2.01781],
        zoom_start=14,
        width=f'{map_width}px',
        height=f'{map_height}px'
    )


    for index, row in place_name.iterrows():
        if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
            # Construction du texte pour le popup
            popup_text = f"<b>{row['name']}</b><br>Rating: {row['rating']}<br>Category: {row['main_category']}"
    
            # Sélection de l'icône en fonction du rating
            if row['rating'] < 3:
                icon_url = 'https://cdn-icons-png.flaticon.com/512/260/260222.png'  # Pour un rating inférieur à 3
            elif 3 <= row['rating'] < 4.5:
                icon_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Twemoji2_1f610.svg/1200px-Twemoji2_1f610.svg.png'  # Pour un rating entre 3 et 4.5
            else:
                icon_url = 'https://e7.pngegg.com/pngimages/919/260/png-clipart-smile-emoji-smiley-emoticon-happiness-green-smiley-face-face-smiley-thumbnail.png'  # Pour un rating supérieur à 4.5
    
            # Création de l'icône personnalisée
            icon = CustomIcon(icon_url, icon_size=(32, 32))
    
            # Ajout du marqueur à la carte
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=popup_text,
                icon=icon
            ).add_to(mymap)
            # Supposons que 'mymap' est votre objet Folium Map déjà créé
    folium_static(mymap)


elif page == pages[3]:
    
 
    # erreur normal si cellule lat and long pas exécute 'latitude', 'longitude'] PAS CRAMER MES CREDIT
    place_name.columns = ['place_id', 'name', 'main_category', 'rating moyen', 'total reviews', 'address',
           'link', 'categories', 'description', 'Grande Categorie',
           'rating_x_reviews','latitude', 'longitude']
    df_filtre = pd.read_csv('filtered.csv')
    df_merge = pd.merge(df_filtre,place_name, on='place_id',how='left')
    df_merge = df_merge[df_merge.address.str.contains('Trappes',na=False)]

    df_merge = df_merge[df_merge['total reviews']>10.]
    
    grouped = df_merge.groupby(['Grande Categorie', 'année'])['rating'].mean().reset_index()
    # Configuration de la page Streamlit

    
    # Configuration de la page Streamlit


    # Titre de la page
    st.title("Analyse de la Moyenne des Avis par Catégorie et par Année")

    # Sélecteur multiple pour choisir les catégories à afficher
    selected_categories = st.multiselect(
        'Choisissez les catégories à afficher:',
        options=grouped['Grande Categorie'].unique(),
        default=grouped['Grande Categorie'].unique()
    )

    # Filtrer les données basées sur les catégories sélectionnées
    filtered_data = grouped[grouped['Grande Categorie'].isin(selected_categories)]
    # Création du graphique Plotly
    fig = go.Figure()

    for category in selected_categories:
        category_data = filtered_data[filtered_data['Grande Categorie'] == category]
        fig.add_trace(
            go.Scatter(
                x=category_data['année'],
                y=category_data['rating'],
                mode='lines+markers',
                name=category
            )
        )

    # Mise à jour des layouts du graphique
    fig.update_layout(
        title='Évolution des Moyennes par Année',
        xaxis_title='Année',
        yaxis_title='Moyenne',
        legend_title='Grande Categorie'
    )

    # Affichage du graphique dans Streamlit
    st.plotly_chart(fig, use_container_width=True)

    ###

    grouped = df_merge.groupby(['place_name', 'année'])['rating'].mean().reset_index()

    # Titre de la page
    st.title("Analyse de la moyenne des avis par Infrastructure et par Année")

    # Sélecteur pour choisir plusieurs lieux spécifiques
    selected_place_names = st.multiselect(
        'Choisissez les lieux à afficher:',
        options=grouped['place_name'].unique(),
        default=[grouped['place_name'].unique()[0]]  # Définit un lieu par défaut pour éviter un graphique vide
    )

    # Création du graphique Plotly
    fig = go.Figure()

    # Ajout de traces pour chaque lieu sélectionné
    for place_name in selected_place_names:
        filtered_data = grouped[grouped['place_name'] == place_name]
        fig.add_trace(
            go.Scatter(
                x=filtered_data['année'],
                y=filtered_data['rating'],
                mode='lines+markers',
                name=place_name
            )
        )

    # Mise à jour des layouts du graphique
    fig.update_layout(
        title='Évolution des moyennes pour les Infrastructures sélectionnées',
        xaxis_title='Année',
        yaxis_title='Moyenne',
        legend_title='Lieux'
    )

    # Affichage du graphique dans Streamlit
    st.plotly_chart(fig, use_container_width=True)
    df_final = pd.read_csv('final_data.csv')
    
    
    
    
#     ###### WORDCLOUD
elif page == pages[4]:
       
#     df_final = pd.read_csv('final_data.csv')
#     # Fonction pour générer et afficher le WordCloud

#     def generate_wordcloud(data):
#         text = ' '.join(data['cleaned_text'].dropna())  # Concaténation de tous les textes nettoyés
#         wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
#         fig, ax = plt.subplots()
#         ax.imshow(wordcloud, interpolation='bilinear')
#         ax.axis('off')
#         st.pyplot(fig)

#     # Interface Streamlit
#     st.title('WordCloud Interactif pour la Ville de Trappes')
#     st.sidebar.header('Filtres Mots Clés')

#     # Sélection multiple des années, catégories et classe prédite
#     selected_years = st.sidebar.multiselect('Sélectionnez les années:', options=df_final['année'].unique())
#     selected_categories = st.sidebar.multiselect('Sélectionnez les grandes catégories:', options=df_final['Grande Categorie'].unique())
#     selected_classes = st.sidebar.multiselect('Sélectionnez la classe prédite:', options=df_final['Predicted_Class'].unique())

#     # Filtrage des données en fonction des sélections
#     filtered_data = df_final[
#         (df_final['année'].isin(selected_years)) &
#         (df_final['Grande Categorie'].isin(selected_categories)) &
#         (df_final['Predicted_Class'].isin(selected_classes))
#     ]

#     if not filtered_data.empty:
#         generate_wordcloud(filtered_data)
#     else:
#         st.write('Aucune donnée à afficher. Veuillez ajuster vos filtres.')
        
        
        

    df_final = pd.read_csv('final_data.csv')
    # Fonction pour générer et afficher le WordCloud
    from  wordcloud import WordCloud
    def generate_wordcloud(data):
        text = ' '.join(data['cleaned_text'].dropna())  # Concaténation de tous les textes nettoyés
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    
        # Interface Streamlit
    st.title('WordCloud Interactif par catégorie pour la Ville de Trappes')
    st.sidebar.header('Filtres')
        
        # Sélection multiple des années, catégories et classe prédite
    selected_years = st.sidebar.multiselect('Sélectionnez les années:', options=df_final['année'].unique())
    selected_categories = st.sidebar.multiselect('Sélectionnez les grandes catégories:', options=df_final['Grande Categorie'].unique())
    selected_classes = st.sidebar.multiselect('Sélectionnez la classe prédite:', options=df_final['Predicted_Class'].unique())
    
        # Filtrage des données en fonction des sélections
    filtered_data = df_final[
        (df_final['année'].isin(selected_years)) &
        (df_final['Grande Categorie'].isin(selected_categories)) &
        (df_final['Predicted_Class'].isin(selected_classes))]

    if not filtered_data.empty:
        generate_wordcloud(filtered_data)
    else:
        st.write('Aucune donnée à afficher. Veuillez ajuster vos filtres.')
            
        
        
elif page == pages[5]:    
    df_final = pd.read_csv('final_data.csv')
    
    def generate_wordcloud(data):
        text = ' '.join(data['cleaned_text'].dropna())  # Concaténation de tous les textes nettoyés
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    
    # Interface Streamlit
    st.title('WordCloud Interactif par Infrastructure pour la Ville de  Trappes')
    st.sidebar.header('Filtres')
    
    # Sélection multiple des années, noms de lieu et classe prédite
    # Utilisation des clés uniques pour chaque widget
    selected_years = st.sidebar.multiselect('Sélectionnez les années:', options=df_final['année'].unique(), key='year_select')
    selected_places = st.sidebar.multiselect('Sélectionnez les noms des lieux:', options=df_final['place_name'].unique(), key='place_select')
    selected_classes = st.sidebar.multiselect('Sélectionnez la classe prédite:', options=df_final['Predicted_Class'].unique(), key='class_select')

# Filtrage des données en fonction des sélections
    filtered_data = df_final[
        (df_final['année'].isin(selected_years)) &
        (df_final['place_name'].isin(selected_places)) &
        (df_final['Predicted_Class'].isin(selected_classes))]


    if not filtered_data.empty:
        generate_wordcloud(filtered_data)
    else:
        st.write('Aucune donnée à afficher. Veuillez ajuster vos filtres.')
        