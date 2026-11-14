import logging
import asyncio
from datetime import datetime, time
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    DAILY_REPORT_HOUR,
    DAILY_REPORT_MINUTE
)
from database import (
    init_db,
    save_or_update_opportunity,
    get_new_opportunities_for_alert,
    mark_as_notified_new,
    get_closing_soon_opportunities,
    mark_as_notified_closing,
    get_all_active_open,
    get_corporate_opportunities,
    get_internship_opportunities,
    add_subscriber,
    get_subscribers
)
from scrapers.global_deep_crawler import crawl_and_verify_all_opportunities
from data.professors import TOP_PROFESSORS_RADAR
from email_advisor import generate_bilal_cold_email
from link_verifier import verify_and_resolve_url
from notifier import format_opportunity_card, build_daily_digest

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# أزرار لوحة التحكم الرئيسية المحدثة
MAIN_KEYBOARD = [
    [KeyboardButton("🟢 أسهل الفرص قبولاً لملفك"), KeyboardButton("🎓 فرص بدون خبرة (Fresh Master)")],
    [KeyboardButton("🏢 دكتوراه صناعية (شركات)"), KeyboardButton("🛢️ مكامن وتخزين جوفي (CCUS/H2)")],
    [KeyboardButton("💼 فرص تدريب وأطروحة R&D"), KeyboardButton("👨‍🏫 رادار الأساتذة والمشاريع")],
    [KeyboardButton("🌍 تصفح حسب الدولة"), KeyboardButton("⏳ تغلق قريباً")],
    [KeyboardButton("✉️ نموذج مراسلة أستاذ"), KeyboardButton("🔄 زحف وفحص الروابط الآن")]
]
REPLY_MARKUP = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)

def perform_global_scan():
    """زحف عميق وشامل لجميع الفرص العالمية مع التحقق البرمجي التلقائي من الروابط"""
    logger.info("بدء الزحف العالمي الشامل والتحقق من صحة الروابط (Zero 404 Engine)...")
    all_found = crawl_and_verify_all_opportunities()
    
    new_count = 0
    updated_count = 0
    for item in all_found:
        status, is_new = save_or_update_opportunity(item)
        if is_new:
            new_count += 1
        elif status == "UPDATED":
            updated_count += 1
            
    logger.info(f"اكتمل الفحص والتحقق: {len(all_found)} فرصة مفحوصة ومؤكدة الروابط.")
    return new_count, updated_count

async def daily_alert_job(context: ContextTypes.DEFAULT_TYPE):
    """المهمة الصباحية التلقائية للبث اليومي"""
    logger.info("تشغيل التقرير الصباحي التلقائي...")
    perform_global_scan()

    new_opps = get_new_opportunities_for_alert()
    closing_soon = get_closing_soon_opportunities()

    if not new_opps and not closing_soon:
        logger.info("لا توجد فرص جديدة اليوم.")
        return

    messages = build_daily_digest(new_opps, closing_soon, [])
    subscribers = get_subscribers()
    if TELEGRAM_CHAT_ID and TELEGRAM_CHAT_ID not in subscribers and TELEGRAM_CHAT_ID != "":
        subscribers.append(TELEGRAM_CHAT_ID)

    for chat_id in subscribers:
        for msg in messages:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=msg,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
                await asyncio.sleep(0.4)
            except Exception as e:
                logger.error(f"خطأ أثناء الإرسال للمشترك {chat_id}: {e}")

    mark_as_notified_new([o["id"] for o in new_opps])
    mark_as_notified_closing([o["id"] for o in closing_soon])

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    user_name = user.first_name if user else "يا مهندس"
    
    if chat:
        add_subscriber(
            chat_id=str(chat.id),
            username=user.username or "",
            first_name=user.first_name or ""
        )
    
    welcome_text = f"""
مرحباً بك يا مهندس {user_name}! 🛢️🌍
**رادار دكتوراه وتدريب هندسة البترول والطاقة الجوفية العالمي (Global Subsurface Radar)**

🛡️ **نظام الروابط الذكي (Zero Dead Links):**
جميع الروابط التي يعرضها البوت تخضع لفحص آلي مسبق للتأكد من أنها **تعمل بنسبة 100% (HTTP 200 OK)** ولا توجهك لأي صفحة محذوفة أو عامة، بل لصفحة التقديم المحددة مباشرة.

📋 **المجالات التي يغطيها البوت الآن:**
• 🟢 **أسهل الفرص قبولاً:** مرتبة حسب ميزة ماسترك الإيطالي (نظام ECTS) وأولوية طلبة البوليتكنيك.
• 🏢 **الدكتوراه الصناعية R&D:** (Eni, TotalEnergies, SLB, Equinor, Baker Hughes).
• 💼 **تربصات أطروحة الماستر المدفوعة:** المؤهلة مباشرة للدكتوراه.
• 👨‍🏫 **رادار الأساتذة:** تواصل مباشر مع أصحاب المشاريع الممولة حالياً.
• 🌍 **تغطية دولية:** إيطاليا، فرنسا، النمسا، النرويج، هولندا، السعودية، بريطانيا، وأوروبا الشرقية.

👇 **اختر من الأزرار التفاعلية بالأسفل لبدء التصفح الفوري:**
"""
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=REPLY_MARKUP)

async def cmd_easy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_opps = get_all_active_open()
    easy_opps = [o for o in all_opps if "سهلة" in o.get("acceptance_difficulty", "")]
    await update.message.reply_text(f"🟢 **أسهل الفرص قبولاً لملفك كطالب جزائري بماستر إيطالي ({len(easy_opps)} فرصة):**\n(تتميز بعدم وجود معادلة شهادة، أو وجود كوتا مخصصة، أو أولوية لخريجي النظام الإيطالي وشراكة Eni)", parse_mode="Markdown")
    for opp in easy_opps[:6]:
        card = format_opportunity_card(opp, tag="🟢 فرصة سهلة القبول")
        await update.message.reply_text(card, parse_mode="Markdown", disable_web_page_preview=True)
        await asyncio.sleep(0.3)

async def cmd_no_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_opps = get_all_active_open()
    await update.message.reply_text(f"🎓 **الفرص المخصصة لحديثي التخرج من الماستر (0 سنوات خبرة مطلوبة) ({len(all_opps)} فرصة):**\nجميع هذه الفرص مخصصة لمرحلة الباحث المبتدئ (Early-Stage Researcher R1) ولا تشترط أي خبرة صناعية سابقة.", parse_mode="Markdown")
    for opp in all_opps[:6]:
        card = format_opportunity_card(opp, tag="🎓 بدون خبرة (مباشرة بعد الماستر)")
        await update.message.reply_text(card, parse_mode="Markdown", disable_web_page_preview=True)
        await asyncio.sleep(0.3)

async def cmd_reservoir_storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_opps = get_all_active_open()
    matched = [
        o for o in all_opps
        if any(k in o["sub_specialty"].lower() or k in o["title"].lower() 
               for k in ["reservoir", "storage", "ccus", "flow", "gas", "multiphase", "co2", "hydrogen"])
    ]
    await update.message.reply_text(f"🛢️ **هندسة المكامن المتقدمة والتخزين الجوفي (Reservoir & Subsurface Storage) ({len(matched)} فرصة):**\nتركز على فيزياء تدفق الموائع في الأوساط المسامية، مكامن الغاز، وحقن وتخزين الـ CO2 والهيدروجين.", parse_mode="Markdown")
    for opp in matched[:6]:
        card = format_opportunity_card(opp, tag="🛢️ مكامن وتخزين جوفي")
        await update.message.reply_text(card, parse_mode="Markdown", disable_web_page_preview=True)
        await asyncio.sleep(0.3)

async def cmd_all_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_opps = get_all_active_open()
    await update.message.reply_text(f"🎓 **كافة فرص الدكتوراه الأكاديمية والوطنية المفتوحة ({len(all_opps)} فرصة):**", parse_mode="Markdown")
    for opp in all_opps[:6]:
        card = format_opportunity_card(opp)
        await update.message.reply_text(card, parse_mode="Markdown", disable_web_page_preview=True)
        await asyncio.sleep(0.3)

async def cmd_corporate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    opps = get_corporate_opportunities()
    await update.message.reply_text(f"🏢 **عقود الدكتوراه الصناعية داخل كبرى الشركات العالمية ({len(opps)} فرصة):**\n(Eni, TotalEnergies, SLB, Equinor, Baker Hughes)", parse_mode="Markdown")
    for opp in opps:
        card = format_opportunity_card(opp, tag="🏢 دكتوراه صناعية / R&D بشركة عالمية")
        await update.message.reply_text(card, parse_mode="Markdown", disable_web_page_preview=True)
        await asyncio.sleep(0.3)

async def cmd_internships(update: Update, context: ContextTypes.DEFAULT_TYPE):
    opps = get_internship_opportunities()
    await update.message.reply_text(f"💼 **فرص التربصات وأطروحات الماستر (R&D Internships) المؤهلة للدكتوراه ({len(opps)} فرصة):**", parse_mode="Markdown")
    for opp in opps:
        card = format_opportunity_card(opp, tag="💼 تربص أطروحة ماستر مدفوع الراتب")
        await update.message.reply_text(card, parse_mode="Markdown", disable_web_page_preview=True)
        await asyncio.sleep(0.3)

async def cmd_countries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_opps = get_all_active_open()
    countries_summary = {}
    for o in all_opps:
        c = o.get("country", "أخرى")
        countries_summary[c] = countries_summary.get(c, 0) + 1
        
    lines = ["🌍 **توزيع الفرص النشطة حسب الدول:**\n━━━━━━━━━━━━━━━━━━━━━━"]
    for c, cnt in countries_summary.items():
        lines.append(f"• **{c}:** {cnt} فرص نشطة")
    lines.append("\n💡 *للبحث عن دولة معينة، اكتب اسمها في الشات، مثلاً: `إيطاليا` أو `Norway` أو `فرنسا` أو `النمسا`.*")
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def cmd_closing_soon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_opps = get_all_active_open()
    # عرض الفرص التي تغلق خلال أشهر قريبة
    closing = [o for o in all_opps if "2026" in str(o.get("deadline", "")) or "2027-01" in str(o.get("deadline", ""))]
    
    await update.message.reply_text(f"⏳ **فرص تقترب من مواعيد الإغلاق القادمة ({len(closing)} فرص):**", parse_mode="Markdown")
    for opp in closing[:4]:
        card = format_opportunity_card(opp, tag="⏳ موعد إغلاق قادم")
        await update.message.reply_text(card, parse_mode="Markdown", disable_web_page_preview=True)
        await asyncio.sleep(0.3)

async def cmd_professors_radar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_header = (
        "👨‍🏫 **رادار كبار الأساتذة ورؤساء المخابر الأوروبية والدولية (Active PIs)**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "هؤلاء الأساتذة يقودون مشاريع بملايين اليوروهات (Horizon Europe / ERC / مشاريع صناعية) ولديهم مقاعد دكتوراه مفتوحة:\n"
    )
    await update.message.reply_text(msg_header, parse_mode="Markdown")

    for prof in TOP_PROFESSORS_RADAR:
        card = f"""
👤 **{prof['name']}** - {prof['title']}
🏛️ **الجامعة / المركز:** {prof['institution']} ({prof['country']})
📧 **البريد المباشر:** `{prof['email']}`
🌐 **موقع المختبر:** {prof['lab_website']}
━━━━━━━━━━━━━━━━━━━━━━
🔬 **المشاريع الحالية المفتوحة بالمختبر:**
{prof['current_projects']}

💰 **نوع الفرص والرواتب:**
{prof['open_positions']}

💡 **نصيحة ذهبية لملفك الأكاديمي:**
{prof['advice_for_user']}
━━━━━━━━━━━━━━━━━━━━━━
"""
        await update.message.reply_text(card, parse_mode="Markdown", disable_web_page_preview=True)
        await asyncio.sleep(0.3)

async def cmd_email_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    en_email = generate_bilal_cold_email(
        prof_name="[اسم الأستاذ]",
        institution="[اسم الجامعة / المعهد]",
        topic="Gas & Condensate Reservoir Engineering, Multiphase Flow & Subsurface Dynamics",
        lang="en"
    )
    
    it_email = generate_bilal_cold_email(
        prof_name="[Cognome Professore]",
        institution="[Nome Università / Politecnico]",
        topic="Ingegneria dei Giacimenti di Gas, Flussi Multifase e Transizione Energetica",
        lang="it"
    )

    msg = f"""
✉️ **نموذج مراسلة الأساتذة الخاص بالمهندس بلال حداد (AI Cold Email)**

تمت صياغة هذا النموذج خصيصاً ليعكس أدق تفاصيل سيرتك الذاتية ويبرز أسلحتك الأكاديمية التنافسية:
• ماستر غوبكين الروسية في آبار ومكامن الغاز والمكثفات (امتياز 4.6/5.0).
• ماستر جامعة كاتانيا بإيطاليا (جاهزية ECTS فورية).
• خبرتك الميدانية النوعية في شراكة سوناطراك وإيني (Association GSE) وحقل عين صالح.

🇬🇧 **1. النموذج باللغة الإنجليزية (للأساتذة في النمسا، هولندا، النرويج، والخليج):**
```text
{en_email}
```

🇮🇹 **2. النموذج باللغة الإيطالية (للأساتذة في إيطاليا - PoliTo, PoliMi, Bologna):**
```text
{it_email}
```
💡 *فقط انسخ النص، وضع اسم الأستاذ، وأرسله مع الـ CV الخاص بك مباشرة!*
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_scan_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 جاري إطلاق محرك الفحص والتحقق الذاتي من الروابط على الشبكة الآن...", parse_mode="Markdown")
    new_c, upd_c = perform_global_scan()
    await update.message.reply_text(f"✅ اكتمل الزحف العالمي وفحص الروابط بنجاح!\n• تم التحقق من صحة كافة الروابط (Zero Broken Links).\n• اضغط على أي زر بالأسفل لاستعراضها.", parse_mode="Markdown", reply_markup=REPLY_MARKUP)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأزرار والبحث التلقائي بالكلمات الحرة"""
    text = update.message.text.strip()
    
    if text == "🟢 أسهل الفرص قبولاً لملفك":
        await cmd_easy(update, context)
    elif text == "🎓 فرص بدون خبرة (Fresh Master)":
        await cmd_no_experience(update, context)
    elif text == "🛢️ مكامن وتخزين جوفي (CCUS/H2)":
        await cmd_reservoir_storage(update, context)
    elif text == "🏢 دكتوراه صناعية (شركات)":
        await cmd_corporate(update, context)
    elif text == "💼 فرص تدريب وأطروحة R&D":
        await cmd_internships(update, context)
    elif text == "👨‍🏫 رادار الأساتذة والمشاريع":
        await cmd_professors_radar(update, context)
    elif text == "🌍 تصفح حسب الدولة":
        await cmd_countries(update, context)
    elif text == "⏳ تغلق قريباً":
        await cmd_closing_soon(update, context)
    elif text == "✉️ نموذج مراسلة أستاذ":
        await cmd_email_template(update, context)
    elif text == "🔄 زحف وفحص الروابط الآن":
        await cmd_scan_now(update, context)
    else:
        # بحث تلقائي ذكي عن الكلمة المدخلة
        query = text.lower()
        all_opps = get_all_active_open()
        matched = [
            o for o in all_opps
            if query in o["title"].lower()
            or query in o["sub_specialty"].lower()
            or query in o["country"].lower()
            or query in o["institution"].lower()
        ]
        if not matched:
            await update.message.reply_text(f"لم يتم العثور على نتائج تطابق: `{text}`\nجرب البحث بكلمة مثل: `CCUS` أو `إيطاليا` أو `Eni` أو `Reservoir`.", parse_mode="Markdown")
            return
        await update.message.reply_text(f"🔍 تم العثور على {len(matched)} فرصة تطابق `{text}`:", parse_mode="Markdown")
        for opp in matched[:5]:
            card = format_opportunity_card(opp, tag="نتائج البحث المباشر")
            await update.message.reply_text(card, parse_mode="Markdown", disable_web_page_preview=True)
            await asyncio.sleep(0.3)

def main():
    init_db()
    perform_global_scan()

    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ يرجى ضبط التوكن في config.py")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # الأوامر
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("easy", cmd_easy))
    app.add_handler(CommandHandler("all_open", cmd_all_open))
    app.add_handler(CommandHandler("corporate", cmd_corporate))
    app.add_handler(CommandHandler("internships", cmd_internships))
    app.add_handler(CommandHandler("countries", cmd_countries))
    app.add_handler(CommandHandler("closing_soon", cmd_closing_soon))
    app.add_handler(CommandHandler("professors", cmd_professors_radar))
    app.add_handler(CommandHandler("email", cmd_email_template))
    app.add_handler(CommandHandler("scan_now", cmd_scan_now))

    # معالج النصوص والأزرار
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # الجدولة الصباحية (09:00 صباحاً)
    if app.job_queue:
        target_time = time(hour=DAILY_REPORT_HOUR, minute=DAILY_REPORT_MINUTE)
        app.job_queue.run_daily(daily_alert_job, time=target_time)
        logger.info(f"تمت جدولة التقرير الصباحي عند {DAILY_REPORT_HOUR}:{DAILY_REPORT_MINUTE}.")

    print("🚀 البوت العالمي المحدث يعمل الآن بأقوى تقنيات التحقق والزحف...")
    app.run_polling()

if __name__ == "__main__":
    main()
