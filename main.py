import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from database import get_db_connection, init_db

app = FastAPI(title="Rivers & Tributaries API")


class RiverCreate(BaseModel):
    name: str
    length_km: int
    continent: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        # Regex-валідація: назва має починатися з великої літери (латиниця/кирилиця)
        # та містити лише літери, пробіли або дефіси
        regex = r"^[A-ZА-ЯІЇЄҐ][a-zA-Zа-яА-ЯіїєґІЇЄҐ\s\-]+$"
        if not re.match(regex, value):
            raise ValueError(
                "Назва річки повинна починатися з великої літери та містити лише літери!"
            )
        return value


class RiverUpdate(BaseModel):
    name: str
    length_km: int
    continent: str


@app.on_event("startup")
def startup():
    init_db()


# 1. GET (отримання списку)
@app.get("/rivers")
def get_rivers():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rivers ORDER BY id;")
            return cur.fetchall()


# 2. GET (отримання окремого запису за ID)
@app.get("/rivers/{river_id}")
def get_river_by_id(river_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rivers WHERE id = %s;", (river_id,))
            river = cur.fetchone()
            if not river:
                raise HTTPException(status_code=404, detail="Річку не знайдено")
            return river


# 3. POST (створення запису)
@app.post("/rivers", status_code=201)
def create_river(river: RiverCreate):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO rivers (name, length_km, continent) VALUES (%s, %s, %s) RETURNING *;",
                (river.name, river.length_km, river.continent),
            )
            res = cur.fetchone()
            conn.commit()
            return res


# 4. PUT (повне оновлення запису)
@app.put("/rivers/{river_id}")
def update_river(river_id: int, river: RiverUpdate):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE rivers SET name = %s, length_km = %s, continent = %s WHERE id = %s RETURNING *;",
                (river.name, river.length_km, river.continent, river_id),
            )
            updated_river = cur.fetchone()
            if not updated_river:
                raise HTTPException(status_code=404, detail="Річку не знайдено")
            conn.commit()
            return updated_river


# 5. DELETE (видалення запису)
@app.delete("/rivers/{river_id}")
def delete_river(river_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM rivers WHERE id = %s RETURNING id;", (river_id,)
            )
            deleted = cur.fetchone()
            if not deleted:
                raise HTTPException(status_code=404, detail="Річку не знайдено")
            conn.commit()
            return {"message": f"Річку з ID {river_id} успішно видалено"}
        