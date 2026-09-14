import psycopg2


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "legal_mind_ai",
    "user": "postgres",
    "password": "Ziy@1234"
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)