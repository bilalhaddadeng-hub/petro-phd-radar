# -*- coding: utf-8 -*-
import os
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["DB_PATH"] = str(Path(__file__).resolve().parent / "test.db")
os.environ["OWNER_CHAT_IDS"] = "111"

import pytest

import database as db


@pytest.fixture(autouse=True)
def fresh_db():
    p = Path(os.environ["DB_PATH"])
    for suffix in ("", "-wal", "-shm"):
        Path(str(p) + suffix).unlink(missing_ok=True)
    db.init_db()
    yield
    for suffix in ("", "-wal", "-shm"):
        Path(str(p) + suffix).unlink(missing_ok=True)


def opp(title, days):
    return {"title": title, "link": "https://example.org/" + title.replace(" ", "-"),
            "institution": "Uni", "country": "Italy", "sub_specialty": "reservoir",
            "deadline": (date.today() + timedelta(days=days)).isoformat()}


def test_dedup_same_title():
    assert db.save_or_update_opportunity(opp("PhD A", 10))[1] is True
    assert db.save_or_update_opportunity(opp("PhD A", 10))[1] is False


def test_upcoming_and_expiry():
    db.save_or_update_opportunity(opp("Soon", 5))
    db.save_or_update_opportunity(opp("Later", 60))
    db.save_or_update_opportunity(opp("Past", -3))
    assert [o["title"] for o in db.get_upcoming_deadlines(30)] == ["Soon"]
    assert db.close_expired_opportunities() == 1
    assert all(o["title"] != "Past" for o in db.get_all_active_open())


def test_application_cycle():
    db.save_or_update_opportunity(opp("PhD B", 10))
    oid = db.get_all_active_open()[0]["id"]
    seq = [db.cycle_application_status("1", oid) for _ in range(5)]
    assert seq == ["APPLIED", "INTERVIEW", "OFFER", "REJECTED", None]
    assert db.get_application_status("1", oid) is None


def test_reminders():
    db.save_or_update_opportunity(opp("PhD C", 3))
    oid = db.get_all_active_open()[0]["id"]
    db.add_favorite("1", oid)
    r = db.get_favorite_reminders({7, 3, 1})
    assert len(r) == 1 and r[0][0] == "1" and r[0][1]["days_left"] == 3


def test_auth_owner_only():
    assert db.is_user_authorized("111", "")
    assert not db.is_user_authorized("999", "stranger")


def test_callback_data_fits_64_bytes():
    import hashlib
    sys.modules.pop("bot", None)
    os.environ.setdefault("TELEGRAM_BOT_TOKEN", "1:x")
    import bot
    cat = "search:" + "مكامن" * 10
    key = bot.cat_key(cat)
    data = f"trk:{'a' * 16}:{key}:99"
    assert len(data.encode()) <= 64
    assert bot.resolve_cat(key) == cat


def test_fee_display_never_claims_unverified_zero():
    from fees import display_registration_fee as r, display_tuition_fee as t
    assert "غير مؤكدة" in r("0 €")
    assert "غير مؤكدة" in r("")
    assert "تقدير" in r("حوالي 30 €")
    assert "حسب شروط التمويل" in t("0 € (معفاة بالكامل)")


def test_catalog_audit_marks_unverified():
    from catalog_audit import apply_audit
    from rebuild_perfect_database import OPPORTUNITIES_DATA as D
    out = apply_audit(D)
    assert len(out) == len(D)
    assert not any(o["deadline"].startswith("2027") for o in out)
    miskolc = next(o for o in out if "miskolc" in o["link"])
    assert "150" in miskolc["registration_fee"]
    assert D[0]["deadline"].startswith("2027")  # الأصل لا يتغير
