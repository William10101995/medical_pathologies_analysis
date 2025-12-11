import os
import time
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Cargo variables de entorno desde docker-compose
DB = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST", "localhost")

# Leo el CSV limpio
csv_path = "/app/data/cleaned/diabetes_cleaned.csv"
df = pd.read_csv(csv_path)

# Conecto a PostgreSQL con reintentos por si la base de datos no está lista
for attempt in range(10):
    try:
        conn = psycopg2.connect(
            dbname=DB, user=USER, password=PASSWORD, host=HOST, port=5432
        )
        print("Conectado a PostgreSQL")
        break
    except Exception as e:
        print(f"Postgres no disponible ({attempt+1}/10)...")
        time.sleep(3)
else:
    raise Exception("No se pudo conectar a Postgres.")

cur = conn.cursor()

# Creo las tablas del esquema estrella
schema_sql = """
CREATE TABLE IF NOT EXISTS dim_gender (
    gender_id SERIAL PRIMARY KEY,
    gender TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_smoking (
    smoking_id SERIAL PRIMARY KEY,
    smoking_status TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_condition (
    condition_id SERIAL PRIMARY KEY,
    condition TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_patient (
    patient_id INT PRIMARY KEY,
    full_name TEXT,
    age INT,
    bmi FLOAT,
    blood_pressure FLOAT,
    glucose_levels FLOAT
);

CREATE TABLE IF NOT EXISTS fact_diabetes (
    fact_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES dim_patient(patient_id),
    gender_id INT REFERENCES dim_gender(gender_id),
    smoking_id INT REFERENCES dim_smoking(smoking_id),
    condition_id INT REFERENCES dim_condition(condition_id)
);
"""

cur.execute(schema_sql)
conn.commit()

# Cargo dimension genero
execute_values(
    cur,
    "INSERT INTO dim_gender (gender) VALUES %s ON CONFLICT (gender) DO NOTHING",
    [(g,) for g in df["gender"].unique()],
)

# Cargo dimensión tabaquismo
execute_values(
    cur,
    "INSERT INTO dim_smoking (smoking_status) VALUES %s ON CONFLICT (smoking_status) DO NOTHING",
    [(s,) for s in df["smoking_status"].unique()],
)

# Cargo dimensión condición médica
execute_values(
    cur,
    "INSERT INTO dim_condition (condition) VALUES %s ON CONFLICT (condition) DO NOTHING",
    [(c,) for c in df["condition"].unique()],
)

conn.commit()

# Cargo dimensión paciente
patient_rows = (
    df[["id", "full_name", "age", "bmi", "blood_pressure", "glucose_levels"]]
    .to_records(index=False)
    .tolist()
)

execute_values(
    cur,
    """
    INSERT INTO dim_patient (
        patient_id, full_name, age, bmi, blood_pressure, glucose_levels
    ) VALUES %s
    ON CONFLICT (patient_id) DO NOTHING;
    """,
    patient_rows,
)
conn.commit()

# Cargo tabla de hechos
fact_rows = []
for _, row in df.iterrows():

    cur.execute("SELECT gender_id FROM dim_gender WHERE gender=%s", (row["gender"],))
    gender_id = cur.fetchone()[0]

    cur.execute(
        "SELECT smoking_id FROM dim_smoking WHERE smoking_status=%s",
        (row["smoking_status"],),
    )
    smoking_id = cur.fetchone()[0]

    cur.execute(
        "SELECT condition_id FROM dim_condition WHERE condition=%s", (row["condition"],)
    )
    condition_id = cur.fetchone()[0]

    fact_rows.append((row["id"], gender_id, smoking_id, condition_id))  # patient_id FK

execute_values(
    cur,
    """
    INSERT INTO fact_diabetes (
        patient_id, gender_id, smoking_id, condition_id
    ) VALUES %s
    """,
    fact_rows,
)

conn.commit()
cur.close()
conn.close()

print("Carga de datos completada.")
