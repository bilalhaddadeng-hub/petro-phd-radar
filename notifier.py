# -*- coding: utf-8 -*-
from typing import Dict, List, Optional
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def format_opportunity_card(opp: Dict, tag: str = "", current_idx: int = 0, total_count: int = 0) -> str:
    source_emoji = {
        "UNIVERSITY": "🏛️ جامعة",
        "INSTITUTE": "🔬 معهد بحثي متقدم",
        "GOVERNMENT": "👑 منحة حكومية / وطنية",
        "PROFESSOR_LAB": "👨‍🏫 مقعد ممول من أستاذ / مختبر",
        "COMPANY_INTERNAL": "🏢 دكتوراه صناعية / شركة عالمية (R&D)",
        "INTERNSHIP_RD": "💼 تدريب وتربص أطروحة (R&D Internship)"
    }.get(opp.get("source_type", "UNIVERSITY"), "📌 فرصة")

    pagination_str = f" [{current_idx + 1} من {total_count}]" if total_count > 0 else ""
    header_tag = f"【 {tag}{pagination_str} 】\n" if tag or pagination_str else ""

    key_reqs = opp.get("key_requirements", "")
    reqs_block = f"\n⚠️ *أصعب الشروط ونقاط الحسم:*\n{key_reqs}\n" if key_reqs else ""

    duration_str = opp.get("duration", "")
    if not duration_str:
        duration_str = "6 أشهر (تربص أطروحة ماستر)" if opp.get("source_type") == "INTERNSHIP_RD" else "3 إلى 4 سنوات (دكتوراه كاملة)"

    seats_str = str(opp.get("seats", "1 مقعد"))
    if "أشهر" in seats_str or "شهر" in seats_str:
        seats_str = "1 مقعد مخصص للمختبر"

    app_method = opp.get("application_method", "")
    method_block = f"\n📨 *طريقة والرمز المرجعي للتقديم المباشر:*\n{app_method}\n" if app_method else ""

    card = f"""
{header_tag}🛢️ *{opp['title']}*
{source_emoji} | 📍 *الجهة:* {opp['institution']} ({opp['country']})
━━━━━━━━━━━━━━━━━━━━━━
🎯 *1. التخصص الدقيق:* {opp['sub_specialty']}
💰 *2. التمويل:* {opp['is_funded']}
💵 *3. الراتب الشهري:* {opp['monthly_salary']}
🎓 *4. رسوم الدراسة:* {opp['tuition_fee']}
📝 *5. رسوم التسجيل:* {opp['registration_fee']}
👥 *6. عدد المقاعد:* {seats_str}
⏱️ *7. مدة العقد / التربص:* {duration_str}
📅 *تاريخ الإغلاق:* {opp.get('deadline', 'مفتوح حتى ملء الشواغر')}
💼 *الخبرة المطلوبة:* 0 سنوات (مفتوحة لحديثي التخرج من الماستر R1)
{method_block}{reqs_block}
📊 *تقييم القبول لملف بلال حداد:*
{opp['acceptance_difficulty']}
━━━━━━━━━━━━━━━━━━━━━━
"""
    return card.strip()

def build_opportunity_keyboard(opp: Dict, category: str, page: int, total: int, is_fav: bool = False) -> InlineKeyboardMarkup:
    """
    إنشاء لوحة أزرار تفاعلية أنيقة ملحقة بكل فرصة:
    - رابط التقديم المباشر كزر خارجي (URL Button)
    - حفظ/إزالة من المفضلة
    - تجهيز إيميل الأستاذ
    - أزرار التنقل (السابق / التالي)
    """
    fav_text = "❌ إزالة من المفضلة" if is_fav else "⭐ حفظ بالمفضلة"
    fav_data = f"unfav:{opp['id']}:{category}:{page}" if is_fav else f"fav:{opp['id']}:{category}:{page}"

    keyboard = [
        # زر الرابط المباشر
        [InlineKeyboardButton("🌐 فتح رابط التقديم المباشر (200 OK)", url=opp["link"])],
        # أزرار الإجراءات
        [
            InlineKeyboardButton("✉️ جهز إيميل المشرف", callback_data=f"mail:{opp['id']}"),
            InlineKeyboardButton(fav_text, callback_data=fav_data)
        ]
    ]

    # أزرار التنقل الدائري السلس بين الصفحات
    nav_buttons = []
    if total > 1:
        prev_page = (page - 1) % total
        next_page = (page + 1) % total
        nav_buttons.append(InlineKeyboardButton("◀️ السابق", callback_data=f"page:{category}:{prev_page}"))
        nav_buttons.append(InlineKeyboardButton(f"📄 {page+1} / {total}", callback_data="noop"))
        nav_buttons.append(InlineKeyboardButton("التالي ▶️", callback_data=f"page:{category}:{next_page}"))
    else:
        nav_buttons.append(InlineKeyboardButton("📄 1 / 1", callback_data="noop"))

    keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu:main")])

    return InlineKeyboardMarkup(keyboard)

def format_professor_card(prof: Dict, current_idx: int = 0, total_count: int = 0) -> str:
    pagination_str = f" [{current_idx + 1} من {total_count}]" if total_count > 0 else ""
    return f"""
👨‍🏫 *{prof['name']}* - {prof['title']}{pagination_str}
🏛️ *الجامعة / المركز:* {prof['institution']} ({prof['country']})
📧 *البريد المباشر:* `{prof['email']}`
🌐 *موقع المختبر:* {prof['lab_website']}
━━━━━━━━━━━━━━━━━━━━━━
🔬 *المشاريع الحالية المفتوحة:*
{prof['current_projects']}

💰 *نوع الفرص المتاحة:*
{prof['open_positions']}

💡 *تقييم الملاءمة لملف بلال حداد:*
{prof['advice_for_user']}
━━━━━━━━━━━━━━━━━━━━━━
""".strip()

def build_professor_keyboard(prof: Dict, page: int, total: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🌐 زيارة موقع مختبر الأستاذ", url=prof["lab_website"])],
        [InlineKeyboardButton("✉️ توليد إيميل مخصص لهذا الأستاذ", callback_data=f"prof_mail:{page}")],
    ]
    nav_buttons = []
    if total > 1:
        prev_page = (page - 1) % total
        next_page = (page + 1) % total
        nav_buttons.append(InlineKeyboardButton("◀️ السابق", callback_data=f"prof_page:{prev_page}"))
        nav_buttons.append(InlineKeyboardButton(f"👨‍🏫 {page+1} / {total}", callback_data="noop"))
        nav_buttons.append(InlineKeyboardButton("التالي ▶️", callback_data=f"prof_page:{next_page}"))
    else:
        nav_buttons.append(InlineKeyboardButton("👨‍🏫 1 / 1", callback_data="noop"))

    keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu:main")])
    return InlineKeyboardMarkup(keyboard)

def build_daily_digest(new_opps: List[Dict], closing_soon: List[Dict], updated_opps: List[Dict]) -> List[str]:
    messages = []
    summary_header = (
        "🌅 *التقرير اليومي لفرص دكتوراه هندسة البترول والطاقة الجوفية* 🛢️\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ *فرص جديدة فتحت اليوم:* {len(new_opps)}\n"
        f"⏳ *فرص تقترب من الإغلاق:* {len(closing_soon)}\n"
        f"🔄 *فرص تم تحديثها:* {len(updated_opps)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "إليك ملخص أبرز الفرص الجديدة المصطادة اليوم 👇"
    )
    messages.append(summary_header)

    for opp in new_opps[:4]:
        messages.append(format_opportunity_card(opp, tag="⚡ فرصة جديدة"))

    for opp in closing_soon[:3]:
        days = opp.get("days_left", "")
        tag_str = f"⏳ تغلق قريباً (متبقي {days} أيام)" if days != "" else "⏳ تغلق قريباً"
        messages.append(format_opportunity_card(opp, tag=tag_str))

    return messages
