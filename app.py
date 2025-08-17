import streamlit as st
import sqlite3
import random
import time

# --- Initialisation de la base SQLite ---
conn = sqlite3.connect("molecules.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS molecules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    formule TEXT,
    famille_pharma TEXT,
    famille_chimique TEXT,
    specialites TEXT,
    role TEXT,
    image TEXT
)
""")
conn.commit()

# --- Fonctions utiles ---
def ajouter_molecule(nom, formule, famille_pharma, famille_chimique, specialites, role, image):
    c.execute("INSERT INTO molecules (nom, formule, famille_pharma, famille_chimique, specialites, role, image) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (nom, formule, famille_pharma, famille_chimique, specialites, role, image))
    conn.commit()

def get_molecules():
    c.execute("SELECT * FROM molecules")
    return c.fetchall()

def get_random_molecule():
    c.execute("SELECT * FROM molecules ORDER BY RANDOM() LIMIT 1")
    return c.fetchone()

# --- Interface Streamlit ---
st.set_page_config(page_title="MolCard", page_icon="💊", layout="centered")

st.title("💊 MolCard - Révision des PA")

menu = st.sidebar.radio("Menu", ["Ajouter une molécule", "Voir la base", "Quiz"])

# --- 1. Ajouter une molécule ---
if menu == "Ajouter une molécule":
    st.subheader("➕ Ajouter une molécule")
    with st.form("ajout_form"):
        nom = st.text_input("Nom du PA")
        formule = st.text_input("Formule semi-développée")
        famille_pharma = st.text_input("Famille pharmaceutique")
        famille_chimique = st.text_input("Famille chimique")
        specialites = st.text_area("Spécialités (séparées par des virgules)")
        role = st.text_area("Rôle thérapeutique")
        image = st.text_input("Nom du fichier image (ex: mol.png)")
        submit = st.form_submit_button("Ajouter")

        if submit:
            ajouter_molecule(nom, formule, famille_pharma, famille_chimique, specialites, role, image)
            st.success(f"{nom} ajouté à la base ✅")

# --- 2. Voir la base ---
elif menu == "Voir la base":
    st.subheader("📂 Base de données")
    data = get_molecules()
    if data:
        for mol in data:
            st.markdown(f"""
            **Nom :** {mol[1]}  
            **Formule :** {mol[2]}  
            **Famille Pharma :** {mol[3]}  
            **Famille Chimique :** {mol[4]}  
            **Spécialités :** {mol[5]}  
            **Rôle :** {mol[6]}  
            """)
            if mol[7]:
                st.image(mol[7], width=200)
            st.divider()
    else:
        st.info("Aucune molécule enregistrée pour le moment.")

# --- 3. Quiz ---
elif menu == "Quiz":
    st.subheader("📝 Mode Quiz")

    if "score" not in st.session_state:
        st.session_state.score = 0
        st.session_state.start_time = time.time()

    mol = get_random_molecule()
    if mol:
        question_type = random.choice(["nom", "formule"])
        if question_type == "nom":
            st.write(f"💡 Trouve les infos pour la molécule : **{mol[1]}**")
        else:
            st.write(f"💡 Trouve les infos pour la formule : **{mol[2]}**")

        reponse_famille = st.text_input("Famille pharmaceutique ?")
        reponse_specialite = st.text_input("Spécialités ?")
        reponse_role = st.text_input("Rôle ?")

        if st.button("Valider"):
            if (reponse_famille.lower() in mol[3].lower()
                and reponse_specialite.lower() in mol[5].lower()
                and reponse_role.lower() in mol[6].lower()):
                st.success("✅ Bonne réponse !")
                st.session_state.score += 1
            else:
                st.error(f"❌ Mauvaise réponse.\n\n👉 Famille : {mol[3]}\n👉 Spécialités : {mol[5]}\n👉 Rôle : {mol[6]}")

        elapsed_time = int(time.time() - st.session_state.start_time)
        st.info(f"⏱ Temps écoulé : {elapsed_time} sec | 🎯 Score : {st.session_state.score}")
    else:
        st.warning("⚠️ Pas de molécules dans la base pour lancer le quiz.")
