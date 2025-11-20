# ============================================================
# BASE DE DATOS — PROYECTO-GRUPO-4
# TimescaleDB optimizado para telemetría + ML + EMS
# ============================================================

import psycopg2
from psycopg2.extras import RealDictCursor
import os

# ------------------------------------------------------------
# CONFIG DB — valores por defecto para Docker/K8s
# ------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "timescaledb")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "microred")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "admin123")


# ------------------------------------------------------------
# CONEXIÓN
# ------------------------------------------------------------
def get_conn():
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
    except Exception as e:
        print("❌ Error conectando a TimescaleDB:", e)
        return None


# ------------------------------------------------------------
# CREAR TABLA COMPLETA DE TELEMETRÍA
# ------------------------------------------------------------
def create_table():
    conn = get_conn()
    if conn is None:
        return

    cur = conn.cursor()

    # Tabla optimizada según RF y RNF
    cur.execute("""
        CREATE TABLE IF NOT EXISTS telemetria (
            timestamp BIGINT PRIMARY KEY,

            pv_voltage FLOAT,
            pv_current FLOAT,
            pv_power   FLOAT,

            battery_voltage FLOAT,
            battery_current FLOAT,
            battery_power   FLOAT,

            load_current FLOAT,
            soc FLOAT,

            temperature_ambient FLOAT,
            temperature_battery FLOAT,

            modo TEXT,
            prediccion_ml FLOAT
        );
    """)

    cur.execute("""
        SELECT create_hypertable(
            'telemetria', 'timestamp',
            if_not_exists => TRUE
        );
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_ts
        ON telemetria (timestamp DESC);
    """)

    conn.commit()
    conn.close()
    print("✔ Tabla 'telemetria' lista (v2 optimizada).")


# ------------------------------------------------------------
# FUNCIÓN PRINCIPAL PARA GUARDAR TELEMETRÍA
# ------------------------------------------------------------
def insertar_telemetria(data: dict):
    conn = get_conn()
    if conn is None:
        return

    cur = conn.cursor()

    ts = data.get("timestamp")
    if ts is None:
        return  # /telemetria siempre envía timestamp

    # Extraer datos del backend
    pv_v = data.get("pv_voltage")
    pv_i = data.get("pv_current")
    pv_p = pv_v * pv_i if pv_v and pv_i else None

    bat_v = data.get("battery_voltage")
    bat_i = data.get("battery_current")
    bat_p = bat_v * bat_i if bat_v and bat_i else None

    load_i = data.get("load_current")

    soc = data.get("soc")
    t_amb = data.get("temperature_ambient")
    t_bat = data.get("temperature_battery")

    modo = data.get("modo")
    pred_ml = data.get("prediccion_ml")

    try:
        cur.execute("""
            INSERT INTO telemetria (
                timestamp,
                pv_voltage, pv_current, pv_power,
                battery_voltage, battery_current, battery_power,
                load_current, soc,
                temperature_ambient, temperature_battery,
                modo, prediccion_ml
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (timestamp) DO NOTHING;
        """, (
            ts,
            pv_v, pv_i, pv_p,
            bat_v, bat_i, bat_p,
            load_i, soc,
            t_amb, t_bat,
            modo, pred_ml
        ))

        conn.commit()

    except Exception as e:
        print("❌ Error guardando telemetría:", e)

    finally:
        conn.close()


# ------------------------------------------------------------
# OBTENER HISTÓRICO PARA FRONTEND / ML
# ------------------------------------------------------------
def obtener_historico(limit=300):
    conn = get_conn()
    if conn is None:
        return []

    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT *
            FROM telemetria
            ORDER BY timestamp DESC
            LIMIT %s;
        """, (limit,))

        rows = cur.fetchall()
        return rows[::-1]  # ascendente para gráficos

    except Exception as e:
        print("❌ Error obteniendo histórico:", e)
        return []

    finally:
        conn.close()


# ------------------------------------------------------------
# AUTO-CREACIÓN AL INICIAR
# ------------------------------------------------------------
create_table()
