import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Connexion à la base SQLite
conn = sqlite3.connect("hotel.db")
c = conn.cursor()

st.set_page_config(page_title="Gestion Hôtelière", layout="wide")

# Ajout d'un fond et amélioration du titre
st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #f8f9fa, #e3e6e8);
            font-family: 'Open Sans', sans-serif;
        }
        h1 {
            text-align: center; 
            color: #2E3A59; 
            font-size: 2.5em; 
            font-weight: bold;
            font-family: 'Montserrat', sans-serif;
        }
        .stButton>button {
            background-color: #2E3A59;
            color: white;
            border-radius: 10px;
            padding: 12px;
            transition: 0.3s ease-in-out;
            font-size: 16px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #506690;
            transform: scale(1.05);
            border:none;
        }
        .stDataFrame {
            border-radius: 12px;
            border: 1px solid #2E3A59;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)


# Ajout d'une image en haut à gauche
col1, col2 = st.columns([1, 3])
with col1:
    st.image("hotel_banner.jpg", use_container_width=True)
with col2:
    st.markdown("<h1>🏨 Gestion Hôtelière</h1>", unsafe_allow_html=True)

# Section définition SQL & Structure de la base
st.markdown("""
### 🗂 Définition & Structure de la Base de Données
La base `hotel.db` contient plusieurs tables :
- **Hotel** : Stocke les informations des hôtels.
- **Client** : Gère les clients enregistrés.
- **Chambre** : Liste les chambres disponibles.
- **Reservation** : Enregistre les réservations effectuées.
- **Évaluation** : Stocke les avis et notes des clients.

Chaque table est liée avec des **clés primaires** et **clés étrangères** pour gérer les relations.
""")
# === Onglets principaux ===
tabs = st.tabs(["🏠 Hôtels", "👤 Clients", "🛏️ Chambres", "📅 Réservations", "📝 Évaluations", "➕ Nouvelle réservation", "➕ Ajouter un client"])

# Onglet Hôtels
with tabs[0]:
    st.header("📍 Liste des Hôtels")
    hotels = pd.read_sql_query("SELECT * FROM Hotel", conn)
    st.dataframe(hotels)

# Onglet Clients
with tabs[1]:
    st.header("👥 Liste des Clients")
    clients = pd.read_sql_query("SELECT * FROM Client", conn)
    st.dataframe(clients)

# Onglet Chambres
with tabs[2]:
    st.header("🛏️ Liste des Chambres")
    query = """
    SELECT Chambre.Id_Chambre, Numero, Etage, 
           CASE WHEN Binaire = 1 THEN 'Disponible' ELSE 'Occupée' END AS Statut,
           Hotel.Ville AS Hotel, Type_Chambre.Type, Type_Chambre.Tarif
    FROM Chambre
    JOIN Hotel ON Chambre.Id_Hotel = Hotel.Id_Hotel
    JOIN Type_Chambre ON Chambre.Id_Type = Type_Chambre.Id_Type
    """
    chambres = pd.read_sql_query(query, conn)
    st.dataframe(chambres)

# Onglet Réservations
with tabs[3]:
    st.header("📅 Réservations")
    query = """
    SELECT R.Id_Reservation, C.Nom_complet, R.Date_arrivee, R.Date_depart
    FROM Reservation R
    JOIN Client C ON R.Id_Client = C.Id_Client
    """
    reservations = pd.read_sql_query(query, conn)
    st.dataframe(reservations)

# Onglet Évaluations
with tabs[4]:
    st.header("📝 Évaluations clients")
    evaluations = pd.read_sql_query("""
        SELECT E.Id_Evaluation, C.Nom_complet, E.Note, E.Commentaire, E.Date_eval
        FROM Evaluation E
        JOIN Client C ON E.Id_Client = C.Id_Client
    """, conn)
    st.dataframe(evaluations)

# Onglet Ajouter une Réservation
with tabs[5]:
    st.header("➕ Ajouter une nouvelle réservation")

    clients_df = pd.read_sql_query("SELECT Id_Client, Nom_complet FROM Client", conn)
    chambres_df = pd.read_sql_query("SELECT Id_Chambre, Numero FROM Chambre", conn)

    if clients_df.empty:
        st.warning("❌ Aucun client enregistré.")
    elif chambres_df.empty:
        st.warning("❌ Aucune chambre disponible.")
    else:
        selected_client = st.selectbox("👤 Client", clients_df["Nom_complet"])
        selected_chambre = st.selectbox("🛏️ Chambre disponible", chambres_df["Numero"])

        date_arr = st.date_input("📅 Date d'arrivée", min_value=date.today())
        date_dep = st.date_input("📅 Date de départ", min_value=date_arr)

        if date_dep <= date_arr:
            st.error("⚠️ La date de départ doit être postérieure à la date d'arrivée.")
        else:
            if st.button("✅ Ajouter la réservation"):
                try:
                    id_client = int(clients_df[clients_df["Nom_complet"] == selected_client]["Id_Client"].values[0])
                    id_chambre = int(chambres_df[chambres_df["Numero"] == selected_chambre]["Id_Chambre"].values[0])

                    c.execute("INSERT INTO Reservation (Date_arrivee, Date_depart, Id_Client) VALUES (?, ?, ?)",
                              (date_arr, date_dep, id_client))
                    id_reservation = c.lastrowid

                    c.execute("INSERT INTO Chambre_Reservation (Id_Chambre, Id_Reservation) VALUES (?, ?)",
                              (id_chambre, id_reservation))

                    c.execute("UPDATE Chambre SET Binaire = 0 WHERE Id_Chambre = ?", (id_chambre,))

                    conn.commit()
                    st.success(f"🎉 Réservation ajoutée avec succès (ID: {id_reservation})")

                except Exception as e:
                    st.error(f"❌ Une erreur est survenue : {e}")

# Onglet Ajouter un client
with tabs[6]:
    st.header("➕ Ajouter un nouveau client")

    nom_complet = st.text_input("Nom complet")
    adresse = st.text_input("Adresse")
    ville = st.text_input("Ville")
    code_postal = st.number_input("Code Postal", min_value=1000, max_value=99999)
    email = st.text_input("Email")
    telephone = st.text_input("Numéro de téléphone")

    if st.button("Ajouter le client"):
        if not nom_complet or not adresse or not ville or not email or not telephone:
            st.error("⚠️ Tous les champs doivent être remplis !")
        else:
            c.execute("""
                INSERT INTO Client (Nom_complet, Adresse, Ville, Code_postal, Email, Telephone) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nom_complet, adresse, ville, code_postal, email, telephone))

            conn.commit()
            st.success("✅ Client ajouté avec succès.")





