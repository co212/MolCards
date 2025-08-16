# MolCards – App Streamlit de révision des molécules (version FR)
# -------------------------------------------------
# Application Streamlit pour créer votre propre base de
# molécules (nom, groupe thérapeutique, rôle/indication) et réviser en mode quiz.
#
# ▶ Installation (dans le terminal):
#   pip install streamlit pandas unidecode
#
# ▶ Lancement:
#   streamlit run molcards_app.py
#
# Un fichier CSV "molecules.csv" sera créé à côté de ce script au premier démarrage.

import os
import io
import re
import random
import pandas as pd
import streamlit as st
from unidecode import unidecode

DATA_FILE = "molecules.csv"
SCORE_FILE = "scores.csv"

REQUIRED_COLUMNS = ["molecule", "groupe", "role"]

# ----------------------------- Utils -----------------------------

def load_data() -> pd.DataFrame:
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
        except Exception:
            df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    else:
        df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    for c in REQUIRED_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    return df.fillna("")

def save_data(df: pd.DataFrame):
    df.to_csv(DATA_FILE, index=False)

def _normalize(s):
    return unidecode(str(s).strip().lower())

# ----------------------------- Quiz Engine -----------------------------

def build_questions(df: pd.DataFrame, mode: str):
    questions = []
    for _, row in df.iterrows():
        if mode == "Nom → Groupe & Rôle":
            q = {"molecule": row["molecule"],
                 "prompt": row["molecule"],
                 "answer": f"Groupe : {row['groupe']}\nRôle : {row['role']}"}
        elif mode == "Groupe → Nom":
            q = {"molecule": row["molecule"],
                 "prompt": row["groupe"],
                 "answer": f"Molécule : {row['molecule']}"}
        else:  # Rôle → Nom
            q = {"molecule": row["molecule"],
                 "prompt": row["role"],
                 "answer": f"Molécule : {row['molecule']}"}
        questions.append(q)
    random.shuffle(questions)
    return questions

# ----------------------------- Streamlit UI -----------------------------

st.set_page_config(page_title="MolCards – Révision molécules", page_icon="💊", layout="wide")

st.title("💊 MolCards – Révision des molécules")

with st.sidebar:
    st.header("⚙️ Menu")
    page = st.radio("Aller à", ["Réviser (Quiz)", "Gérer ma base", "Importer/Exporter"], index=0)

# Charger données
_df = load_data()

# ----------------------------- Page: Gérer ma base -----------------------------
if page == "Gérer ma base":
    st.subheader("📚 Ma base de molécules")
    st.dataframe(_df, use_container_width=True)

    st.markdown("### ➕ Ajouter une molécule")
    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        mol = c1.text_input("Nom de la molécule*")
        grp = c2.text_input("Groupe thérapeutique*")
        rol = c3.text_input("Rôle / Indication*")
        submitted = st.form_submit_button("Ajouter")
        if submitted:
            if mol and grp and rol:
                _df = pd.concat([_df, pd.DataFrame([{ "molecule": mol, "groupe": grp, "role": rol }])], ignore_index=True)
                save_data(_df)
                st.success(f"✅ {mol} ajoutée.")
            else:
                st.error("Veuillez remplir tous les champs.")

# ----------------------------- Page: Import/Export -----------------------------
elif page == "Importer/Exporter":
    st.subheader("🔁 Importer / Exporter")
    st.markdown("#### 📤 Exporter la base actuelle")
    buf = io.StringIO()
    _df.to_csv(buf, index=False)
    st.download_button("Télécharger la base en CSV", buf.getvalue(), file_name="molecules.csv", mime="text/csv")

    st.markdown("#### 📥 Importer un fichier CSV (colonnes : molecule,groupe,role)")
    uploaded = st.file_uploader("Choisir un fichier CSV", type=["csv"])
    if uploaded is not None:
        try:
            new_df = pd.read_csv(uploaded)
            for c in REQUIRED_COLUMNS:
                if c not in new_df.columns:
                    new_df[c] = ""
            _df = pd.concat([_df, new_df], ignore_index=True).drop_duplicates("molecule").reset_index(drop=True)
            save_data(_df)
            st.success("✅ Import réussi.")
        except Exception as e:
            st.error(f"Erreur lors de l'import : {e}")

# ----------------------------- Page: Réviser (Quiz) ----------------------------
else:
    st.subheader("🧠 Mode Quiz")
    mode = st.selectbox("Choisissez un mode de révision", ["Nom → Groupe & Rôle", "Groupe → Nom", "Rôle → Nom"])
    nb = st.slider("Nombre de questions", 5, 30, 10)
    lancer = st.button("Démarrer une session")

    if lancer:
        if _df.empty:
            st.warning("Votre base est vide, ajoutez des molécules dans l’onglet 'Gérer ma base'.")
        else:
            questions = build_questions(_df, mode)[:nb]
            score = 0
            for i, q in enumerate(questions, start=1):
                st.markdown(f"#### Question {i}/{nb}")
                st.info(q["prompt"])
                if st.button(f"👀 Révéler la réponse {i}"):
                    st.success(q["answer"])

            st.success("✅ Session terminée !")
