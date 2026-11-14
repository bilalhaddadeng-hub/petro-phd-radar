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
        category TEXT,
        key_requirements TEXT
    )
    """)
    cursor.execute("PRAGMA table_info(opportunities)")
    cols = [r[1] for r in cursor.fetchall()]
    if "key_requirements" not in cols:
        cursor.execute("ALTER TABLE opportunities ADD COLUMN key_requirements TEXT")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscribers (
        chat_id TEXT PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        joined_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        chat_id TEXT NOT NULL,
        opp_id TEXT NOT NULL,
        saved_at TEXT NOT NULL,
        PRIMARY KEY (chat_id, opp_id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hunting_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        scanned_sources INTEGER NOT NULL,
        new_found INTEGER NOT NULL,
        updated_found INTEGER NOT NULL,
        details TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authorized_users (
        chat_id TEXT PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        authorized_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def authorize_user(chat_id: str, username: str = "", first_name: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT OR REPLACE INTO authorized_users (chat_id, username, first_name, authorized_at)
    VALUES (?, ?, ?, ?)
    """, (str(chat_id), username, first_name, now_str))
    conn.commit()
    conn.close()

def is_user_authorized(chat_id: str, username: str = "") -> bool:
    if username and username.lower().strip().replace("@", "") in ["haddadbilal", "bilalhaddad", "bilalhaddadeng"]:
        return True
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM authorized_users WHERE chat_id = ?", (str(chat_id),))
    row = cursor.fetchone()
    conn.close()
    return row is not None

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
    import re
    clean_title = re.sub(r'[^\w\s]', '', title).strip().lower()
    clean_title = " ".join(clean_title.split())
    # الاعتماد على العنوان المعياري لتوليد المعرف لضمان ثبات المعرف وعدم تكرار الفرص عند تحديث الروابط
    key = clean_title if clean_title else link.strip().lower()
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]

def save_or_update_opportunity(data: Dict) -> Tuple[str, bool]:
    import re
    conn = get_connection()
    cursor = conn.cursor()
    title = data.get("title", "بدون عنوان")
    link = data.get("link", "").strip()
    opp_id = generate_id(link, title)
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # فحص مانع التكرار الصارم (البحث بالمعرف، أو العنوان المطابق، أو البداية المعيارية)
    clean_title = re.sub(r'^[^\w]+', '', title).strip().lower()
    cursor.execute("""
    SELECT id, title, deadline, status FROM opportunities 
    WHERE id = ? OR LOWER(title) = ?
    """, (opp_id, title.strip().lower()))
    row = cursor.fetchone()

    if row is None:
        cursor.execute("SELECT id, title, deadline, status FROM opportunities")
        all_rows = cursor.fetchall()
        for r in all_rows:
            r_norm = re.sub(r'^[^\w]+', '', r["title"]).strip().lower()
            if len(clean_title) > 20 and len(r_norm) > 20:
                if clean_title[:35] == r_norm[:35]:
                    row = r
                    break

    exp_req = data.get("experience_required", "0 سنوات (مفتوحة بالكامل لحديثي التخرج من الماستر / Early Stage Researcher)")
    category = data.get("category", "RESERVOIR_STORAGE")
    key_reqs = data.get("key_requirements", "")

    if row is None:
        cursor.execute("""
        INSERT OR REPLACE INTO opportunities (
            id, title, link, institution, country, source_type, sub_specialty,
            deadline, tuition_fee, registration_fee, monthly_salary, is_funded,
            seats, acceptance_difficulty, status, first_seen_at, last_updated_at,
            notified_as_new, notified_closing_soon, experience_required, category, key_requirements
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NEW', ?, ?, 0, 0, ?, ?, ?)
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
            now_str,
            exp_req,
            category,
            key_reqs
        ))
        conn.commit()
        conn.close()
        return "NEW", True
    else:
        existing_id = row["id"]
        old_deadline = row["deadline"]
        new_deadline = data.get("deadline", old_deadline)
        is_updated = (old_deadline != new_deadline)

        new_status = "UPDATED" if is_updated else row["status"]
        cursor.execute("""
        UPDATE opportunities SET
            title = ?,
            link = ?,
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
            acceptance_difficulty = ?,
            experience_required = ?,
            category = ?,
            key_requirements = ?
        WHERE id = ?
        """, (
            title,
            link,
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
            exp_req,
            category,
            key_reqs,
            existing_id
        ))
        conn.commit()
        conn.close()
        return ("UPDATED" if is_updated else "EXISTING"), False

def get_opportunity_by_id(opp_id: str) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

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

def get_reservoir_storage_opportunities() -> List[Dict]:
    all_opps = get_all_active_open()
    keywords = ["reservoir", "storage", "ccus", "flow", "gas", "multiphase", "co2", "hydrogen", "مكامن", "كربون", "غاز"]
    matched = [
        o for o in all_opps
        if any(k in o["sub_specialty"].lower() or k in o["title"].lower() for k in keywords)
    ]
    return matched

def get_easy_opportunities() -> List[Dict]:
    all_opps = get_all_active_open()
    return [o for o in all_opps if "سهلة" in o.get("acceptance_difficulty", "") or "إيطاليا" in o.get("country", "")]

def get_opportunities_by_country(country_name: str) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM opportunities WHERE country LIKE ? AND status != 'CLOSED' ORDER BY deadline ASC", (f"%{country_name}%",))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def search_opportunities(keyword: str) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    pattern = f"%{keyword.strip()}%"
    cursor.execute("""
    SELECT * FROM opportunities 
    WHERE (title LIKE ? OR institution LIKE ? OR sub_specialty LIKE ? OR country LIKE ?)
      AND status != 'CLOSED'
    ORDER BY deadline ASC
    """, (pattern, pattern, pattern, pattern))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ----------------- المفضلة (Favorites) -----------------
def add_favorite(chat_id: str, opp_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT OR REPLACE INTO favorites (chat_id, opp_id, saved_at) VALUES (?, ?, ?)", (str(chat_id), opp_id, now_str))
    conn.commit()
    conn.close()

def remove_favorite(chat_id: str, opp_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE chat_id = ? AND opp_id = ?", (str(chat_id), opp_id))
    conn.commit()
    conn.close()

def is_favorite(chat_id: str, opp_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM favorites WHERE chat_id = ? AND opp_id = ?", (str(chat_id), opp_id))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def get_user_favorites(chat_id: str) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT o.* FROM opportunities o
    JOIN favorites f ON o.id = f.opp_id
    WHERE f.chat_id = ?
    ORDER BY f.saved_at DESC
    """, (str(chat_id),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ----------------- سجل الصيد (Hunting Logs) -----------------
def log_hunting_session(scanned: int, new_found: int, updated: int, details: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO hunting_logs (timestamp, scanned_sources, new_found, updated_found, details)
    VALUES (?, ?, ?, ?, ?)
    """, (now_str, scanned, new_found, updated, details))
    conn.commit()
    conn.close()

def get_latest_hunting_stats() -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hunting_logs ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_new_opportunities_for_alert() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM opportunities WHERE notified_as_new = 0")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_as_notified_new(opp_ids: List[str]):
    if not opp_ids:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany("UPDATE opportunities SET notified_as_new = 1, status = 'OPEN' WHERE id = ?", [(i,) for i in opp_ids])
    conn.commit()
    conn.close()

def get_closing_soon_opportunities() -> List[Dict]:
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
