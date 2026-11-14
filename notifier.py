from typing import Dict, List

def format_opportunity_card(opp: Dict, tag: str = "") -> str:
    source_emoji = {
        "UNIVERSITY": "🏛️ جامعة",
        "INSTITUTE": "🔬 معهد بحثي متقدم",
        "GOVERNMENT": "👑 منحة حكومية / وطنية",
        "PROFESSOR_LAB": "👨‍🏫 مقعد ممول من أستاذ / مختبر",
        "COMPANY_INTERNAL": "🏢 دكتوراه صناعية / شركة عالمية (R&D)",
        "INTERNSHIP_RD": "💼 تدريب وتربص أطروحة (R&D Internship)"
    }.get(opp.get("source_type", "UNIVERSITY"), "📌 فرصة")

    header_tag = f"【 {tag} 】\n" if tag else ""

    card = f"""
{header_tag}🛢️ **{opp['title']}**
{source_emoji} | 📍 **الجهة:** {opp['institution']} ({opp['country']})
━━━━━━━━━━━━━━━━━━━━━━
🎯 **1. التخصص الدقيق:** {opp['sub_specialty']}
💰 **2. هل هي منحة / ممولة؟:** {opp['is_funded']}
💵 **3. الراتب الشهري:** {opp['monthly_salary']}
🎓 **4. رسوم الدراسة (Tuition):** {opp['tuition_fee']}
📝 **5. رسوم التسجيل (Registration):** {opp['registration_fee']}
👥 **6. عدد المقاعد المتاحة:** {opp['seats']}
📅 **تاريخ الإغلاق (Deadline):** {opp.get('deadline', 'مفتوح حتى ملء الشواغر')}
💼 **الخبرة المطلوبة:** 0 سنوات (مخصصة لحديثي التخرج من الماستر / R1 Early Stage)

📊 **7. تقييم القبول لملف بلال حداد:**
{opp['acceptance_difficulty']}
━━━━━━━━━━━━━━━━━━━━━━
🔗 [اضغط هنا لفتح رابط التقديم المباشر]({opp['link']})
"""
    return card.strip()

def build_daily_digest(new_opps: List[Dict], closing_soon: List[Dict], updated_opps: List[Dict]) -> List[str]:
    """
    بناء التقرير الصباحي اليومي المنسق في رسائل واضحة
    """
    messages = []
    summary_header = (
        "🌅 **التقرير اليومي لفرص دكتوراه هندسة البترول والطاقة الجوفية** 🛢️\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ **فرص جديدة فتحت اليوم:** {len(new_opps)}\n"
        f"⏳ **فرص تقترب من الإغلاق (خلال 7 أيام):** {len(closing_soon)}\n"
        f"🔄 **فرص تم تحديثها:** {len(updated_opps)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "إليك التفاصيل الكاملة لكل فرصة مرتبة بالأسفل 👇"
    )
    messages.append(summary_header)

    for opp in new_opps:
        messages.append(format_opportunity_card(opp, tag="⚡ فرصة جديدة فتحت اليوم"))

    for opp in closing_soon:
        days = opp.get("days_left", "")
        tag_str = f"⏳ تغلق قريباً (متبقي {days} أيام)" if days != "" else "⏳ تغلق قريباً"
        messages.append(format_opportunity_card(opp, tag=tag_str))

    for opp in updated_opps:
        messages.append(format_opportunity_card(opp, tag="🔄 تم تحديث التواريخ أو الشروط"))

    return messages
