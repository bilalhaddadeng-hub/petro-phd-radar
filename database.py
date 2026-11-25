import sqlite3
import hashlib
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from config import DB_PATH, CLOSING_SOON_DAYS, OWNER_CHAT_IDS, AUTHORIZED_USERNAMES, MAX_USERS

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
    except sqlite3.DatabaseError:
        pass
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
        key_requirements TEXT,
        duration TEXT,
        application_method TEXT
    )
    """)
    cursor.execute("PRAGMA table_info(opportunities)")
    cols = [r[1] for r in cursor.fetchall()]
    if "key_requirements" not in cols:
        cursor.execute("ALTER TABLE opportunities ADD COLUMN key_requirements TEXT")
    if "duration" not in cols:
        cursor.execute("ALTER TABLE opportunities ADD COLUMN duration TEXT")
    if "application_method" not in cols:
        cursor.execute("ALTER TABLE opportunities ADD COLUMN application_method TEXT")
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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        chat_id TEXT NOT NULL,
        opp_id TEXT NOT NULL,
        status TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (chat_id, opp_id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sources (
        url TEXT PRIMARY KEY,
        kind TEXT NOT NULL DEFAULT 'jobs',
        added_by TEXT,
        added_at TEXT
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opp_status ON opportunities(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opp_deadline ON opportunities(deadline)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fav_chat ON favorites(chat_id)")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portal_audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        portal_name TEXT,
        portal_url TEXT,
        http_status INTEGER,
        response_time_ms INTEGER,
        links_scanned INTEGER,
        petro_matches INTEGER,
        status_text TEXT,
        sample_matches_json TEXT,
        scanned_at TEXT
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

def add_user_source(url: str, kind: str = "jobs", added_by: str = "") -> bool:
    conn = get_connection()
    try:
        cur = conn.execute("INSERT OR IGNORE INTO user_sources (url, kind, added_by, added_at) VALUES (?, ?, ?, ?)",
                           (url, kind, str(added_by), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def remove_user_source(url: str) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM user_sources WHERE url = ?", (url,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def list_user_sources() -> List[Dict]:
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute("SELECT url, kind FROM user_sources ORDER BY added_at").fetchall()]
    finally:
        conn.close()


def try_claim_slot(chat_id: str, username: str = "", first_name: str = "") -> bool:
    """يمنح مقعداً لمن يضغط /start إن بقي مقعد (المالك + مقعد واحد افتراضياً)، وإلا يرفض. ذرّي."""
    chat_id = str(chat_id)
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        rows = conn.execute("SELECT chat_id FROM authorized_users").fetchall()
        members = {r[0] for r in rows} | {str(x) for x in OWNER_CHAT_IDS}
        if chat_id in members or len(members) < MAX_USERS:
            now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("INSERT OR REPLACE INTO authorized_users (chat_id, username, first_name, authorized_at) "
                         "VALUES (?, ?, ?, ?)", (chat_id, username, first_name, now_str))
            conn.commit()
            return True
        conn.rollback()
        return False
    finally:
        conn.close()


def is_user_authorized(chat_id: str, username: str = "") -> bool:
    if str(chat_id) in OWNER_CHAT_IDS:
        return True
    if username and username.lower().strip().replace("@", "") in AUTHORIZED_USERNAMES:
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

    exp_req = data.get("experience_required", "")
    category = data.get("category", "RESERVOIR_STORAGE")
    key_reqs = data.get("key_requirements", "")
    duration = data.get("duration", "3 إلى 4 سنوات (دكتوراه كاملة)" if data.get("source_type") != "INTERNSHIP_RD" else "6 أشهر (تربص أطروحة ماستر)")
    app_method = data.get("application_method", "عبر بوابة التقديم الرسمية المباشرة")

    if row is None:
        cursor.execute("""
        INSERT OR REPLACE INTO opportunities (
            id, title, link, institution, country, source_type, sub_specialty,
            deadline, tuition_fee, registration_fee, monthly_salary, is_funded,
            seats, duration, application_method, acceptance_difficulty, status,
            first_seen_at, last_updated_at, notified_as_new, notified_closing_soon,
            experience_required, category, key_requirements
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NEW', ?, ?, 0, 0, ?, ?, ?)
        """, (
            opp_id,
            title,
            link,
            data.get("institution", "جهة غير محددة"),
            data.get("country", "دولي"),
            data.get("source_type", "UNIVERSITY"),
            data.get("sub_specialty", "هندسة بترول عامة"),
            data.get("deadline", "غير محدد"),
            data.get("tuition_fee", ""),
            data.get("registration_fee", ""),
            data.get("monthly_salary", "ممولة"),
            data.get("is_funded", "نعم"),
            data.get("seats", "1 مقعد"),
            duration,
            app_method,
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
            duration = ?,
            application_method = ?,
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
            data.get("tuition_fee", ""),
            data.get("registration_fee", ""),
            data.get("monthly_salary", "ممولة"),
            data.get("is_funded", "نعم"),
            data.get("seats", "1 مقعد"),
            duration,
            app_method,
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
    return [o for o in all_opps if "سهلة" in o.get("acceptance_difficulty", "")]

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

def save_portal_audit_log(portal_name: str, portal_url: str, http_status: int, response_time_ms: int, links_scanned: int, petro_matches: int, status_text: str, sample_matches_json: str = "[]"):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO portal_audit_logs (portal_name, portal_url, http_status, response_time_ms, links_scanned, petro_matches, status_text, sample_matches_json, scanned_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (portal_name, portal_url, http_status, response_time_ms, links_scanned, petro_matches, status_text, sample_matches_json, now_str))
    conn.commit()
    conn.close()

def get_latest_portal_audits() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT p1.* FROM portal_audit_logs p1
    JOIN (
        SELECT portal_name, MAX(id) as max_id
        FROM portal_audit_logs
        GROUP BY portal_name
    ) p2 ON p1.id = p2.max_id
    ORDER BY p1.http_status DESC, p1.response_time_ms ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

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


# ----------------- متابعة التقديمات (Application Tracker) -----------------
APP_STATUSES = ["APPLIED", "INTERVIEW", "OFFER", "REJECTED"]

def get_application_status(chat_id: str, opp_id: str) -> Optional[str]:
    conn = get_connection()
    row = conn.execute("SELECT status FROM applications WHERE chat_id = ? AND opp_id = ?", (str(chat_id), opp_id)).fetchone()
    conn.close()
    return row["status"] if row else None

def cycle_application_status(chat_id: str, opp_id: str) -> Optional[str]:
    """none -> APPLIED -> INTERVIEW -> OFFER -> REJECTED -> none. يرجع الحالة الجديدة."""
    cur = get_application_status(chat_id, opp_id)
    order = [None] + APP_STATUSES
    new = order[(order.index(cur) + 1) % len(order)]
    conn = get_connection()
    if new is None:
        conn.execute("DELETE FROM applications WHERE chat_id = ? AND opp_id = ?", (str(chat_id), opp_id))
    else:
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("INSERT OR REPLACE INTO applications (chat_id, opp_id, status, updated_at) VALUES (?, ?, ?, ?)",
                     (str(chat_id), opp_id, new, now_str))
    conn.commit()
    conn.close()
    return new

def get_user_applications(chat_id: str) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("""
    SELECT o.*, a.status AS app_status FROM opportunities o
    JOIN applications a ON o.id = a.opp_id
    WHERE a.chat_id = ? ORDER BY a.updated_at DESC
    """, (str(chat_id),)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ----------------- المواعيد والإحصاءات -----------------
def _days_left(deadline: str) -> Optional[int]:
    if not deadline or len(deadline) < 10:
        return None
    try:
        return (datetime.strptime(deadline[:10], "%Y-%m-%d").date() - date.today()).days
    except ValueError:
        return None

def get_upcoming_deadlines(days: int = 30) -> List[Dict]:
    """الفرص المفتوحة التي تغلق خلال `days` يوماً، مرتبة بالأقرب."""
    out = []
    for o in get_all_active_open():
        d = _days_left(o.get("deadline"))
        if d is not None and 0 <= d <= days:
            o["days_left"] = d
            out.append(o)
    return sorted(out, key=lambda x: x["days_left"])

def close_expired_opportunities() -> int:
    """تعليم الفرص التي انتهى موعدها بـ CLOSED. يرجع عددها."""
    expired = [o["id"] for o in get_all_active_open() if (_days_left(o.get("deadline")) or 0) < 0
               and _days_left(o.get("deadline")) is not None]
    if expired:
        conn = get_connection()
        conn.executemany("UPDATE opportunities SET status = 'CLOSED' WHERE id = ?", [(i,) for i in expired])
        conn.commit()
        conn.close()
    return len(expired)

def get_stats() -> Dict:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) c FROM opportunities WHERE status != 'CLOSED'").fetchone()["c"]
    by_country = conn.execute("SELECT country, COUNT(*) c FROM opportunities WHERE status != 'CLOSED' GROUP BY country ORDER BY c DESC LIMIT 8").fetchall()
    by_type = conn.execute("SELECT source_type, COUNT(*) c FROM opportunities WHERE status != 'CLOSED' GROUP BY source_type ORDER BY c DESC").fetchall()
    conn.close()
    return {"total": total, "by_country": [(r[0], r[1]) for r in by_country], "by_type": [(r[0], r[1]) for r in by_type]}

def get_favorite_reminders(days_set) -> List[Tuple[str, Dict]]:
    """(chat_id, opp) للمفضلة والتقديمات النشطة التي يتبقى لإغلاقها عدد أيام ضمن days_set."""
    conn = get_connection()
    rows = conn.execute("""
    SELECT f.chat_id AS chat_id, o.* FROM favorites f JOIN opportunities o ON o.id = f.opp_id
    WHERE o.status != 'CLOSED'
    """).fetchall()
    conn.close()
    seen, out = set(), []
    for r in rows:
        d = _days_left(r["deadline"])
        if d in days_set and (r["chat_id"], r["id"]) not in seen:
            seen.add((r["chat_id"], r["id"]))
            o = dict(r); o["days_left"] = d
            out.append((r["chat_id"], o))
    return out


# ------------------------------ فجوات مكتشفة تلقائياً ------------------------------
def init_gap_tables():
    conn = get_connection()
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS discovered_gaps (
            key TEXT PRIMARY KEY, topic TEXT, sentence TEXT, title TEXT, year INTEGER, pub_date TEXT,
            venue TEXT, url TEXT, cites INTEGER DEFAULT 0, found_at TEXT, notified INTEGER DEFAULT 0)""")
        conn.commit()
    finally:
        conn.close()


def add_discovered_gaps(items: List[Dict]) -> int:
    """يضيف الجديد فقط (المفتاح DOI/معرّف). يعيد عدد المضاف فعلاً."""
    init_gap_tables()
    conn = get_connection()
    added = 0
    try:
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        for d in items:
            cur = conn.execute(
                "INSERT OR IGNORE INTO discovered_gaps (key, topic, sentence, title, year, pub_date, venue, url, cites, found_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (d["key"], d["topic"], d["sentence"], d["title"], d.get("year"), d.get("date", ""),
                 d.get("venue", ""), d.get("url", ""), d.get("cites", 0), now_str))
            added += cur.rowcount
        conn.commit()
    finally:
        conn.close()
    return added


def list_discovered_gaps(limit: int = 1, offset: int = 0) -> List[Dict]:
    init_gap_tables()
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM discovered_gaps ORDER BY pub_date DESC, found_at DESC LIMIT ? OFFSET ?",
                            (limit, offset)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def count_discovered_gaps() -> int:
    init_gap_tables()
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM discovered_gaps").fetchone()[0]
    finally:
        conn.close()


def take_unnotified_gaps(limit: int = 3) -> List[Dict]:
    """أحدث الفجوات التي لم تُرسَل بعد، ويعلّمها كمُرسَلة."""
    init_gap_tables()
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM discovered_gaps WHERE notified = 0 ORDER BY pub_date DESC LIMIT ?",
                            (limit,)).fetchall()
        items = [dict(r) for r in rows]
        # ما زاد على الحد يُعلَّم أيضاً كي لا يتراكم ويُغرق المستخدم لاحقاً
        conn.execute("UPDATE discovered_gaps SET notified = 1 WHERE notified = 0")
        conn.commit()
        return items
    finally:
        conn.close()


def list_recipient_ids() -> List[str]:
    conn = get_connection()
    try:
        ids = {r[0] for r in conn.execute("SELECT chat_id FROM authorized_users").fetchall()}
    finally:
        conn.close()
    return sorted(ids | {str(x) for x in OWNER_CHAT_IDS})
