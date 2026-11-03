import psycopg
from psycopg.rows import dict_row

DB_PARAMS = {
    "host": "localhost",
    "port": 5432,
    "dbname": "rivers_db",
    "user": "postgres",
    "password": "postgrespassword",
}


def get_db_connection():
    return psycopg.connect(**DB_PARAMS, row_factory=dict_row)


def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Створення таблиці 1: Річки (Rivers)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS rivers (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    length_km INT NOT NULL,
                    continent VARCHAR(50) NOT NULL
                );
            """)

            # Створення таблиці 2: Притоки (Tributaries) — зв'язок з rivers
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tributaries (
                    id SERIAL PRIMARY KEY,
                    river_id INT REFERENCES rivers(id) ON DELETE CASCADE,
                    name VARCHAR(100) NOT NULL,
                    length_km INT NOT NULL
                );
            """)

            # Перевірка, чи база порожня, щоб заповнити 50+ записами
            cur.execute("SELECT COUNT(*) as count FROM rivers;")
            if cur.fetchone()["count"] == 0:
                print("Заповнення бази 50+ записами...")
                # Додаємо 10 основних річок
                rivers_data = [
                    ("Amazon", 6992, "South America"),
                    ("Nile", 6650, "Africa"),
                    ("Yangtze", 6300, "Asia"),
                    ("Mississippi", 6275, "North America"),
                    ("Yenisei", 5539, "Asia"),
                    ("Yellow River", 5464, "Asia"),
                    ("Ob", 5410, "Asia"),
                    ("Parana", 4880, "South America"),
                    ("Congo", 4700, "Africa"),
                    ("Danube", 2850, "Europe"),
                ]

                river_ids = []
                for r in rivers_data:
                    cur.execute(
                        "INSERT INTO rivers (name, length_km, continent) VALUES (%s, %s, %s) RETURNING id;",
                        r,
                    )
                    river_ids.append(cur.fetchone()["id"])

                # Генеруємо 50 приток (по 5 приток для кожної річки = 50 записів)
                tributaries_data = []
                for r_id in river_ids:
                    for i in range(1, 6):
                        tributaries_data.append(
                            (r_id, f"Tributary_{r_id}_{i}", 100 + i * 25)
                        )

                for t in tributaries_data:
                    cur.execute(
                        "INSERT INTO tributaries (river_id, name, length_km) VALUES (%s, %s, %s);",
                        t,
                    )

                conn.commit()
                print("Успішно додано 10 річок та 50 приток!")


if __name__ == "__main__":
    init_db()
