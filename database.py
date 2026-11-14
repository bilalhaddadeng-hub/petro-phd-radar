import sqlite3
import hashlib
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from config import DB_PATH, CLOSING_SOON_DAYS

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS opportunities (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        link TEXT NOT NULL,
        institution TEXT NOT NULL,
        country TEXT NOT NULL,
        source_type TEXT NOT NULL,
        sub_specialty TEXT NOT NULL,
        deadline TEXT,
        tuition_fee TEXT,
        registration_fee TEXT,
        monthly_salary TEXT,
        is_funded TEXT,
        seats TEXT,
        acceptance_difficulty TEXT,
        status TEXT DEFAULT 'NEW',
        first_seen_at TEXT NOT NULL,
        last_updated_at TEXT NOT NULL,
        notified_as_new INTEGER DEFAULT 0,
        notified_closing_soon INTEGER DEFAULT 0,
        experience_required TEXT,
        category TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscribers (
        chat_id TEXT PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        joined_at TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def add_subscriber(chat_id: str, username: str = "", first_name: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT OR REPLACE INTO subscribers (chat_id, username, first_name, joined_at)
    VALUES (?, ?, ?, ?)
    """, (str(chat_id), username, first_name, now_str))
    conn.commit()
    conn.close()

def get_subscribers() -> List[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM subscribers")
    rows = cursor.fetchall()
    conn.close()
    return [r["chat_id"] for r in rows]

def generate_id(link: str, title: str = "") -> str:
    key = f"{link.strip()}::{title.strip()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]

def save_or_update_opportunity(data: Dict) -> Tuple[str, bool]:
    """
    حفظ أو تحديث فرصة:
    ترجع (status, is_new):
    - is_new: True إذا كانت فرصة جديدة تماماً
    - status: 'NEW', 'UPDATED', 'EXISTING'
    """
    conn = get_connection()
    cursor = conn.cursor()
    title = data.get("title", "بدون عنوان")
    link = data.get("link", "").strip()
    opp_id = generate_id(link, title)
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT id, deadline, status FROM opportunities WHERE id = ? OR link = ?", (opp_id, link))
    row = cursor.fetchone()

    if row is None:
        # فرصة جديدة
        cursor.execute("""
        INSERT OR REPLACE INTO opportunities (
            id, title, link, institution, country, source_type, sub_specialty,
            deadline, tuition_fee, registration_fee, monthly_salary, is_funded,
            seats, acceptance_difficulty, status, first_seen_at, last_updated_at,
            notified_as_new, notified_closing_soon
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NEW', ?, ?, 0, 0)
        """, (
            opp_id,
            title,
            link,
            data.get("institution", "جهة غير محددة"),
            data.get("country", "دولي"),
            data.get("source_type", "UNIVERSITY"),
            data.get("sub_specialty", "هندسة بترول عامة"),
            data.get("deadline", "غير محدد"),
            data.get("tuition_fee", "معفاة بالكامل"),
            data.get("registration_fee", "رسوم إدارية قياسية"),
            data.get("monthly_salary", "ممولة"),
            data.get("is_funded", "نعم"),
            data.get("seats", "1 مقعد"),
            data.get("acceptance_difficulty", "متوسطة"),
            now_str,
            now_str
        ))
        conn.commit()
        conn.close()
        return "NEW", True
    else:
        # فرصة موجودة مسبقاً، تحديث
        existing_id = row["id"]
        old_deadline = row["deadline"]
        new_deadline = data.get("deadline", old_deadline)
        is_updated = (old_deadline != new_deadline)

        new_status = "UPDATED" if is_updated else row["status"]
        cursor.execute("""
        UPDATE opportunities SET
            title = ?,
            deadline = ?,
            last_updated_at = ?,
            status = ?,
            institution = ?,
            country = ?,
            sub_specialty = ?,
            tuition_fee = ?,
            registration_fee = ?,
            monthly_salary = ?,
            is_funded = ?,
            seats = ?,
            acceptance_difficulty = ?
        WHERE id = ?
        """, (
            title,
            new_deadline,
            now_str,
            new_status,
            data.get("institution", "جهة غير محددة"),
            data.get("country", "دولي"),
            data.get("sub_specialty", "هندسة بترول عامة"),
            data.get("tuition_fee", "معفاة بالكامل"),
            data.get("registration_fee", "رسوم إدارية قياسية"),
            data.get("monthly_salary", "ممولة"),
            data.get("is_funded", "نعم"),
            data.get("seats", "1 مقعد"),
            data.get("acceptance_difficulty", "متوسطة"),
            existing_id
        ))
        conn.commit()
        conn.close()
        return ("UPDATED" if is_updated else "EXISTING"), False

def get_new_opportunities_for_alert() -> List[Dict]:
    """جلب الفرص الجديدة التي لم يتم إرسال تنبيه عنها بعد"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM opportunities WHERE notified_as_new = 0")
    rows = cursor.fetchall()
    result = [dict(r) for r in rows]
    conn.close()
    return result

def mark_as_notified_new(opp_ids: List[str]):
    if not opp_ids:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany("UPDATE opportunities SET notified_as_new = 1, status = 'OPEN' WHERE id = ?", [(i,) for i in opp_ids])
    conn.commit()
    conn.close()

def get_closing_soon_opportunities() -> List[Dict]:
    """جلب الفرص التي ستغلق قريباً ولم يتم التنبيه عنها"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM opportunities 
    WHERE status IN ('OPEN', 'NEW', 'UPDATED')
      AND notified_closing_soon = 0
    """)
    rows = cursor.fetchall()
    conn.close()
    
    closing_soon = []
    today = date.today()
    for r in rows:
        dl_str = r["deadline"]
        if dl_str and len(dl_str) >= 10:
            try:
                dl_date = datetime.strptime(dl_str[:10], "%Y-%m-%d").date()
                days_left = (dl_date - today).days
                if 0 <= days_left <= CLOSING_SOON_DAYS:
                    d = dict(r)
                    d["days_left"] = days_left
                    closing_soon.append(d)
            except ValueError:
                pass
    return closing_soon

def mark_as_notified_closing(opp_ids: List[str]):
    if not opp_ids:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany("UPDATE opportunities SET notified_closing_soon = 1, status = 'CLOSING_SOON' WHERE id = ?", [(i,) for i in opp_ids])
    conn.commit()
    conn.close()

def get_all_active_open(source_filter: Optional[str] = None) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM opportunities WHERE status != 'CLOSED'"
    params = []
    if source_filter:
        query += " AND source_type = ?"
        params.append(source_filter)
    query += " ORDER BY deadline ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_corporate_opportunities() -> List[Dict]:
    return get_all_active_open(source_filter="COMPANY_INTERNAL")

def get_internship_opportunities() -> List[Dict]:
    return get_all_active_open(source_filter="INTERNSHIP_RD")

