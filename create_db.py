import sqlite3
import os

# Créer dossier images s'il n'existe pas
if not os.path.exists("images"):
    os.makedirs("images")

# Connexion à la base
conn = sqlite3.connect("molecules.db")
c = conn.cursor()

# Création de la table
c.execute('''
CREATE TABLE IF NOT EXISTS molecules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    formule TEXT NOT NULL,
    famille_pharmaceutique TEXT,
    famille_chimique TEXT,
    specialites TEXT,
    role TEXT,
    image TEXT
)
''')

conn.commit()
conn.close()
print("✅ Base SQLite 'molecules.db' créée avec succès !")
