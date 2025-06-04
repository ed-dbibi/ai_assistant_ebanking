import sqlite3

conn = sqlite3.connect('bank.db')
cursor = conn.cursor()

# Recréation des tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS comptes (
    id INTEGER PRIMARY KEY,
    numero TEXT NOT NULL,
    solde REAL NOT NULL,
    type TEXT NOT NULL,
    client_id INTEGER,
    FOREIGN KEY (client_id) REFERENCES clients(id)
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    compte_id INTEGER,
    date TEXT,
    montant REAL,
    type TEXT,
    description TEXT,
    FOREIGN KEY (compte_id) REFERENCES comptes(id)
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS frais (
    id INTEGER PRIMARY KEY,
    compte_id INTEGER,
    mois TEXT,
    montant REAL,
    FOREIGN KEY (compte_id) REFERENCES comptes(id)
)
''')

# Ajout des données
cursor.execute("INSERT OR REPLACE INTO clients (id, nom, prenom) VALUES (1, 'ELMOURABIT', 'Houda')")
cursor.execute("INSERT OR REPLACE INTO clients (id, nom, prenom) VALUES (2, 'Bencheikh', 'Yassine')")

cursor.execute("INSERT OR REPLACE INTO comptes (id, numero, solde, type, client_id) VALUES (1, 'CPT-HOUDA-001', 8400.0, 'COURANT', 1)")
cursor.execute("INSERT OR REPLACE INTO comptes (id, numero, solde, type, client_id) VALUES (2, 'CPT-YASSINE-001', 2000.0, 'EPARGNE', 2)")

transactions = [
    (1, '2025-05-01', -100.0, 'debit', 'Paiement électricité'),
    (1, '2025-05-03', -50.0, 'debit', 'Netflix'),
    (1, '2025-05-05', 1500.0, 'credit', 'Salaire'),
    (1, '2025-05-07', -70.0, 'debit', 'Course'),
]
cursor.executemany("INSERT INTO transactions (compte_id, date, montant, type, description) VALUES (?, ?, ?, ?, ?)", transactions)

frais = [
    (1, '2025-05', 12.5),
    (1, '2025-04', 10.0)
]
cursor.executemany("INSERT INTO frais (compte_id, mois, montant) VALUES (?, ?, ?)", frais)

conn.commit()
conn.close()
