import pandas as pd
import folium
from folium.features import CustomIcon
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static

# Configuration de la page Streamlit
st.set_page_config(page_title="Analyse des Infrastructures", layout="wide", initial_sidebar_state="expanded")


# Chargement des données
place_name = pd.read_csv('place_name.csv')
place_name['rating_x_reviews'] = place_name['rating'] * place_name['reviews']
## filterde df


# Regroupement et calcul des moyennes pondérées
results = place_name.groupby('Grande Categorie').agg(
    total_weighted_rating=('rating_x_reviews', 'sum'),
    total_reviews=('reviews', 'sum')
).reset_index()
results['weighted_average_rating'] = (results['total_weighted_rating'] / results['total_reviews']).round(2)

# Calcul du nombre d'entrées pour chaque catégorie
category_counts = place_name['Grande Categorie'].value_counts().rename('infrastructure_count').reset_index()
category_counts.columns = ['Grande Categorie', 'infrastructure_count']
results = pd.merge(results, category_counts, on='Grande Categorie')

# Affichage des résultats


title_html = '''
             <h3 align="center" style="font-size:20px"><b>Avis sur les Infrastructures à Trappes</b></h3>
             <p align="center">E-réputation des lieux et services</p>
             '''
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
st.title("Avis sur les Infrastructures à Trappes - E-réputation")

##
# erreur normal si cellule lat and long pas exécute 'latitude', 'longitude'] PAS CRAMER MES CREDIT
place_name.columns = ['place_id', 'name', 'main_category', 'rating moyen', 'total reviews', 'address',
       'link', 'categories', 'description', 'Grande Categorie',
       'rating_x_reviews','latitude', 'longitude']
df_filtre = pd.read_csv('filtered.csv')
df_merge = pd.merge(df_filtre,place_name, on='place_id',how='left')
df_merge = df_merge[df_merge.address.str.contains('Trappes',na=False)]

df_merge = df_merge[df_merge['total reviews']>10.]
## graphque
annual_rating_average = df_merge.groupby('année')['rating moyen'].mean().reset_index()
import matplotlib.pyplot as plt
import seaborn as sns
# Création du graphique
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(data=annual_rating_average, x='année', y='rating moyen', marker='o', label='Rating Moyen Général', ax=ax)
plt.title('Évolution de la note moyenne par année')
plt.xlabel('Année')
plt.ylabel('Rating Moyen')
plt.grid(True)
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

# Affichage dans Streamlit avec mise en page en colonnes
col1, col2 = st.columns(2)

with col1:
    # Supposons que 'mymap' est votre objet Folium Map déjà créé
    st.dataframe(results)

with col2:
    st.pyplot(fig)

## count graph
annual_rating_count = df_merge.groupby('année')['rating moyen'].count().reset_index()

# Création du graphique
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(data=annual_rating_count, x='année', y='rating moyen', marker='o', ax=ax)
plt.title('Évolution du nombre de notes')
plt.xlabel('Année')
plt.ylabel('Nombre de notes')
plt.grid(True)
plt.xticks(rotation=25)
plt.tight_layout()


# Utilisez st.columns pour organiser la carte et le graphique côte à côte
col1, col2 = st.columns(2)

with col1:
    # Supposons que 'mymap' est votre objet Folium Map déjà créé
    folium_static(mymap)

with col2:
    # Utiliser st.pyplot pour afficher le graphique matplotlib
    st.pyplot(fig)
grouped = df_merge.groupby(['Grande Categorie', 'année'])['rating'].mean().reset_index()
# Configuration de la page Streamlit


# Titre de la page
st.title("Analyse des Ratings par Catégorie et par Année")

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
    title='Évolution des Ratings Moyens par Année',
    xaxis_title='Année',
    yaxis_title='Rating Moyen',
    legend_title='Grande Categorie'
)

# Affichage du graphique dans Streamlit
st.plotly_chart(fig, use_container_width=True)

###

grouped = df_merge.groupby(['place_name', 'année'])['rating'].mean().reset_index()

# Titre de la page
st.title("Analyse des Ratings par Lieu et par Année")

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
    title='Évolution des Ratings pour les lieux sélectionnés',
    xaxis_title='Année',
    yaxis_title='Rating Moyen',
    legend_title='Lieux'
)

# Affichage du graphique dans Streamlit
st.plotly_chart(fig, use_container_width=True)
df_final = pd.read_csv('final_data.csv')