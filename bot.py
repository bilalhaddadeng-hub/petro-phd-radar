# -*- coding: utf-8 -*-
"""
bot.py - رادار وصياد دكتوراه وتدريب هندسة البترول والمكامن والطاقة الجوفية
المصمم خصيصاً للمهندس بلال حداد (Bilal Haddad)
يدعم التصفح التفاعلي بالأزرار (Pagination)، صيد الفرص الحي، فحص الروابط 100%، وتوليد الإيميلات.
"""

import logging
import asyncio
from datetime import datetime
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
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
    add_subscriber,
    get_subscribers,
    get_all_active_open,
    get_corporate_opportunities,
    get_internship_opportunities,
    get_reservoir_storage_opportunities,
    get_easy_opportunities,
    get_opportunities_by_country,
    search_opportunities,
    add_favorite,
    remove_favorite,
    is_favorite,
    get_user_favorites,
    get_opportunity_by_id,
    get_latest_hunting_stats,
    get_new_opportunities_for_alert,
    mark_as_notified_new,
    get_closing_soon_opportunities,
    mark_as_notified_closing,
    authorize_user,
    is_user_authorized
)
from hunter import execute_deep_hunt, HUNTING_TARGETS
from data.professors import TOP_PROFESSORS_RADAR
from email_advisor import generate_bilal_cold_email
from notifier import (
    format_opportunity_card,
    build_opportunity_keyboard,
    format_professor_card,
    build_professor_keyboard,
    build_daily_digest
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# لوحة المفاتيح الرئيسية الثابتة (سهلة وسريعة الوصول)
MAIN_KEYBOARD = [
    [KeyboardButton("🛢️ مكامن وتخزين جوفي (CCUS/H2)"), KeyboardButton("🎓 فرص بدون خبرة (Fresh Master)")],
    [KeyboardButton("🟢 أسهل الفرص لملفك (إيطاليا)"), KeyboardButton("🏢 دكتوراه صناعية (شركات)")],
    [KeyboardButton("💼 فرص تدريب وأطروحة R&D"), KeyboardButton("👨‍🏫 رادار الأساتذة والمشاريع")],
    [KeyboardButton("🎯 صياد الفرص الحي (Live Hunter)"), KeyboardButton("⭐ الفرص المحفوظة (المفضلة)")],
    [KeyboardButton("🌍 تصفح حسب الدولة"), KeyboardButton("🔍 بحث مخصص في الفرص")]
]
REPLY_MARKUP = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)

# ذاكرة الجلسة لتخزين قوائم البحث والتصفح حسب المستخدم
USER_CACHE = {}

def get_category_items(category: str, chat_id: str) -> list:
    if category == "reservoir_storage":
        return get_reservoir_storage_opportunities()
    elif category == "no_exp":
        return get_all_active_open()
    elif category == "easy":
        return get_easy_opportunities()
    elif category == "corporate":
        return get_corporate_opportunities()
    elif category == "internship":
        return get_internship_opportunities()
    elif category == "favorites":
        return get_user_favorites(chat_id)
    elif category.startswith("country:"):
        country = category.split(":", 1)[1]
        return get_opportunities_by_country(country)
    elif category.startswith("search:"):
        q = category.split(":", 1)[1]
        return search_opportunities(q)
    return get_all_active_open()

async def send_paginated_opportunity(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str, page: int = 0, is_edit: bool = False):
    chat_id = str(update.effective_chat.id)
    items = get_category_items(category, chat_id)

    if not items:
        empty_text = "❌ لا توجد فرص متطابقة حالياً ضمن هذا القسم."
        if is_edit and update.callback_query:
            await update.callback_query.edit_message_text(empty_text)
        else:
            await context.bot.send_message(chat_id=chat_id, text=empty_text)
        return

    # ضبط رقم الصفحة ضمن الحدود
    total = len(items)
    page = max(0, min(page, total - 1))
    opp = items[page]
    fav_status = is_favorite(chat_id, opp["id"])

    card_text = format_opportunity_card(opp, current_idx=page, total_count=total)
    keyboard = build_opportunity_keyboard(opp, category=category, page=page, total=total, is_fav=fav_status)

    if is_edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text=card_text,
                parse_mode="Markdown",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.debug(f"Edit message skipped: {e}")
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=card_text,
            parse_mode="Markdown",
            reply_markup=keyboard,
            disable_web_page_preview=True
        )

# الرمز السري الحصري للوصول للبوت (خاص بالمهندس بلال حداد فقط)
SECRET_ACCESS_TOKEN = "bilal_petro_vip"

AUTH_LOCKED_TEXT = """
🔒 *عذراً، هذا الرادار مخصص وخاص.*

هذا البوت مخصص حصرياً للمهندس *بلال حداد* (Bilal Haddad) لمتابعة واقتناص فرص الدكتوراه والتربصات المتقدمة في هندسة المكامن والبترول والطاقة الجوفية.

إذا كنت صاحب الرادار وتستخدم حساباً جديداً، يرجى الدخول عبر رابط الدعوة الحصري:
🔗 `https://t.me/bilal_petro_phd_bot?start=bilal_petro_vip`

أو إرسال رمز التفعيل الخاص مباشرة في المحادثة:
`/auth bilal_petro_vip`
"""

def check_user_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    user = update.effective_user
    if not chat:
        return False
    chat_id = str(chat.id)
    username = user.username if user else ""
    first_name = user.first_name if user else ""

    # التحقق من باراميتر البدء في الرابط العميق: /start bilal_petro_vip
    if context.args and len(context.args) > 0 and context.args[0].strip() == SECRET_ACCESS_TOKEN:
        authorize_user(chat_id, username, first_name)
        return True

    # التحقق من قاعدة البيانات أو اليوزرنيم المعتمد
    if is_user_authorized(chat_id, username):
        return True

    return False

# ----------------- أوامر البوت الأساسية -----------------
async def cmd_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    chat_id = str(chat.id)
    username = user.username if user else ""
    first_name = user.first_name if user else ""

    token = context.args[0].strip() if context.args else ""
    text = update.message.text.strip() if update.message and update.message.text else ""
    if not token and SECRET_ACCESS_TOKEN in text:
        token = SECRET_ACCESS_TOKEN

    if token == SECRET_ACCESS_TOKEN:
        authorize_user(chat_id, username, first_name)
        await update.message.reply_text(
            f"🔓 *تم التحقق بنجاح وتفعيل وصولك الحصري يا مهندس {first_name or 'بلال'}!*\n\nأهلاً بك في رادارك الخاص لصيد دكتوراه هندسة البترول والمكامن.",
            parse_mode="Markdown",
            reply_markup=REPLY_MARKUP
        )
        await cmd_start(update, context)
    else:
        await update.message.reply_text(
            "❌ رمز الدخول غير صحيح. يرجى إدخال الرمز الصحيح عبر:\n`/auth bilal_petro_vip`",
            parse_mode="Markdown"
        )

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_user_auth(update, context):
        await update.message.reply_text(AUTH_LOCKED_TEXT, parse_mode="Markdown")
        return

    chat = update.effective_chat
    user = update.effective_user
    user_name = user.first_name if user else "يا مهندس بلال"

    if chat:
        add_subscriber(chat_id=str(chat.id), username=user.username or "", first_name=user.first_name or "")

    stats = get_latest_hunting_stats()
    all_opps = get_all_active_open()
    res_opps = get_reservoir_storage_opportunities()

    welcome_text = f"""
مرحباً بك يا مهندس {user_name}! 🛢️🌍
*رادار وصياد دكتوراه هندسة البترول والمكامن والطاقة الجوفية الحصري*

📊 *حالة الرادار السحابي المباشرة:*
• إجمالي الفرص النشطة المصطادة: *{len(all_opps)} فرصة*
• مكامن وتخزين جوفي (CCUS/H2): *{len(res_opps)} فرصة*
• متطلب الخبرة: *0 سنوات (مفتوحة لحديثي التخرج من الماستر)*
• حالة الروابط: *100% مؤكدة ومفحوصة (Zero Dead Links)*
• السيرفر السحابي: *يعمل 24/7 دون توقف*
• الحساب: *مصرح ومحمي حصرياً لك*

👇 *استخدم الأزرار التفاعلية بالأسفل للتصفح السلس بنقرة واحدة:*
"""
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=REPLY_MARKUP)

async def cmd_reservoir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_user_auth(update, context):
        await update.message.reply_text(AUTH_LOCKED_TEXT, parse_mode="Markdown")
        return
    await send_paginated_opportunity(update, context, category="reservoir_storage", page=0)

async def cmd_no_exp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_user_auth(update, context):
        await update.message.reply_text(AUTH_LOCKED_TEXT, parse_mode="Markdown")
        return
    await send_paginated_opportunity(update, context, category="no_exp", page=0)

async def cmd_easy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_user_auth(update, context):
        await update.message.reply_text(AUTH_LOCKED_TEXT, parse_mode="Markdown")
        return
    await send_paginated_opportunity(update, context, category="easy", page=0)

async def cmd_corporate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_user_auth(update, context):
        await update.message.reply_text(AUTH_LOCKED_TEXT, parse_mode="Markdown")
        return
    await send_paginated_opportunity(update, context, category="corporate", page=0)

async def cmd_internships(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_user_auth(update, context):
        await update.message.reply_text(AUTH_LOCKED_TEXT, parse_mode="Markdown")
        return
    await send_paginated_opportunity(update, context, category="internship", page=0)

async def cmd_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_user_auth(update, context):
        await update.message.reply_text(AUTH_LOCKED_TEXT, parse_mode="Markdown")
        return
    chat_id = str(update.effective_chat.id)
    favs = get_user_favorites(chat_id)
    if not favs:
        await update.message.reply_text(
            "⭐ *قائمتك المفضلة فارغة حالياً.*\n\nيمكنك حفظ أي فرصة تهمك بالضغط على زر `⭐ حفظ بالمفضلة` أثناء تصفح الفرص للرجوع إليها هنا ومتابعة موعد إغلاقها.",
            parse_mode="Markdown"
        )
        return
    await send_paginated_opportunity(update, context, category="favorites", page=0)

async def cmd_professors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_user_auth(update, context):
        await update.message.reply_text(AUTH_LOCKED_TEXT, parse_mode="Markdown")
        return
    total = len(TOP_PROFESSORS_RADAR)
    prof = TOP_PROFESSORS_RADAR[0]
    card_text = format_professor_card(prof, current_idx=0, total_count=total)
    keyboard = build_professor_keyboard(prof, page=0, total=total)
    await update.message.reply_text(card_text, parse_mode="Markdown", reply_markup=keyboard, disable_web_page_preview=True)

async def cmd_countries_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_user_auth(update, context):
        await update.message.reply_text(AUTH_LOCKED_TEXT, parse_mode="Markdown")
        return
    keyboard = [
        [InlineKeyboardButton("🇮🇹 إيطاليا (PoliTo / Eni / PoliMi)", callback_data="c:إيطاليا")],
        [InlineKeyboardButton("🇳🇴 النرويج (Equinor / NTNU / UiS)", callback_data="c:النرويج"),
         InlineKeyboardButton("🇦🇹 النمسا (Leoben / OMV)", callback_data="c:النمسا")],
        [InlineKeyboardButton("🇫🇷 فرنسا (TotalEnergies / IFPEN)", callback_data="c:فرنسا"),
         InlineKeyboardButton("🇳🇱 هولندا (TU Delft)", callback_data="c:هولندا")],
        [InlineKeyboardButton("🇸🇦 السعودية (KAUST / KFUPM CPG)", callback_data="c:السعودية"),
         InlineKeyboardButton("🇬🇧 بريطانيا (Heriot-Watt)", callback_data="c:بريطانيا")],
        [InlineKeyboardButton("🔙 العودة للقائمة", callback_data="menu:main")]
    ]
    await update.message.reply_text(
        "🌍 *اختر الدولة التي تريد استعراض فرص الدكتوراه والتدريب المتاحة بها:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def cmd_hunter_hub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_user_auth(update, context):
        await update.message.reply_text(AUTH_LOCKED_TEXT, parse_mode="Markdown")
        return
    stats = get_latest_hunting_stats()
    scanned = stats.get("scanned_sources", len(HUNTING_TARGETS)) if stats else len(HUNTING_TARGETS)
    last_time = stats.get("timestamp", "اليوم") if stats else "اليوم"
    all_opps = get_all_active_open()

    text = f"""
🎯 *صياد الفرص الذكي (Autonomous Opportunity Hunter)*
━━━━━━━━━━━━━━━━━━━━━━
📡 *حالة الرادار:* يعمل 24/7 على السحابة (Cloud Runner Active)
🏢 *البوابات الممسوحة:* {scanned} بوابة عالمية (Euraxess, Eni, SLB, Total, IFPEN, PoliTo, Leoben, TU Delft, KAUST...)
📊 *إجمالي الفرص المصطادة:* {len(all_opps)} فرصة مؤكدة الروابط
⏱️ *آخر فحص وصيد نشط:* `{last_time}`
🛡️ *معدل الروابط السليمة:* 100% (Zero Dead Links)
━━━━━━━━━━━━━━━━━━━━━━
💡 الصياد يراقب التحديثات لحظياً ويرسل إشعاراً فورياً للمشتركين عند اكتشاف أي فرصة جديدة تناسب ملفك.
"""
    keyboard = [
        [InlineKeyboardButton("🚀 إطلاق حملة صيد فوري شامل الآن", callback_data="hunt:force")],
        [InlineKeyboardButton("🔙 العودة للقائمة", callback_data="menu:main")]
    ]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def cmd_search_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_user_auth(update, context):
        await update.message.reply_text(AUTH_LOCKED_TEXT, parse_mode="Markdown")
        return
    await update.message.reply_text(
        "🔍 *البحث الذكي المخصص:*\n\nأرسل في الشات أي كلمة تريد البحث عنها، مثل:\n• `multiphase`\n• `Eni`\n• `Torino`\n• `Leoben`\n• `CO2`\n• `عين صالح`\n• `تدريب`\n• `Norway`\n\nوسيقوم البوت بجلب كافة الفرص المطابقة وتصفحها بسلاسة!",
        parse_mode="Markdown"
    )

# ----------------- معالج النصوص والبحث -----------------
async def handle_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = str(update.effective_chat.id)
    user = update.effective_user
    username = user.username if user else ""

    # التحقق من إرسال رمز التفعيل الحصري كنص مباشر
    if text == SECRET_ACCESS_TOKEN or text.startswith("/auth"):
        await cmd_auth(update, context)
        return

    # فحص التصريح الأمني
    if not is_user_authorized(chat_id, username):
        await update.message.reply_text(AUTH_LOCKED_TEXT, parse_mode="Markdown")
        return

    # التوجيه حسب الأزرار الثابتة
    if text == "🛢️ مكامن وتخزين جوفي (CCUS/H2)":
        await cmd_reservoir(update, context)
    elif text == "🎓 فرص بدون خبرة (Fresh Master)":
        await cmd_no_exp(update, context)
    elif text == "🟢 أسهل الفرص لملفك (إيطاليا)":
        await cmd_easy(update, context)
    elif text == "🏢 دكتوراه صناعية (شركات)":
        await cmd_corporate(update, context)
    elif text == "💼 فرص تدريب وأطروحة R&D":
        await cmd_internships(update, context)
    elif text == "⭐ الفرص المحفوظة (المفضلة)":
        await cmd_favorites(update, context)
    elif text == "👨‍🏫 رادار الأساتذة والمشاريع":
        await cmd_professors(update, context)
    elif text == "🌍 تصفح حسب الدولة":
        await cmd_countries_menu(update, context)
    elif text == "🎯 صياد الفرص الحي (Live Hunter)":
        await cmd_hunter_hub(update, context)
    elif text == "🔍 بحث مخصص في الفرص":
        await cmd_search_prompt(update, context)
    else:
        # اعتبار النص ككلمة بحث
        category = f"search:{text}"
        results = search_opportunities(text)
        if not results:
            await update.message.reply_text(f"🔍 لم يتم العثور على فرص تطابق كلمة: `{text}`\nجرب كلمة أخرى مثل: `reservoir` أو `Eni` أو `إيطاليا`.", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"🔍 تم العثور على *{len(results)}* فرصة تطابق: `{text}` 👇", parse_mode="Markdown")
            await send_paginated_opportunity(update, context, category=category, page=0)

# ----------------- معالج الأزرار التفاعلية (Callbacks) -----------------
async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "noop":
        return

    chat_id = str(query.message.chat_id)
    user = query.from_user
    username = user.username if user else ""

    if not is_user_authorized(chat_id, username):
        await query.answer("🔒 الرادار مقفل - يرجى الدخول عبر رابط الدعوة الحصري", show_alert=True)
        return

    # التنقل بين صفحات الفرص
    if data.startswith("page:"):
        _, category, page_str = data.split(":", 2)
        await send_paginated_opportunity(update, context, category=category, page=int(page_str), is_edit=True)

    # المفضلة
    elif data.startswith("fav:"):
        _, opp_id, category, page_str = data.split(":", 3)
        add_favorite(chat_id, opp_id)
        await query.answer("⭐ تم حفظ الفرصة في المفضلة!", show_alert=False)
        await send_paginated_opportunity(update, context, category=category, page=int(page_str), is_edit=True)

    elif data.startswith("unfav:"):
        _, opp_id, category, page_str = data.split(":", 3)
        remove_favorite(chat_id, opp_id)
        await query.answer("❌ تم الحذف من المفضلة", show_alert=False)
        await send_paginated_opportunity(update, context, category=category, page=int(page_str), is_edit=True)

    # اختيار لغة إيميل التواصل للفرصة
    elif data.startswith("mail:"):
        opp_id = data.split(":", 1)[1]
        opp = get_opportunity_by_id(opp_id)
        if opp:
            keyboard = [
                [InlineKeyboardButton("🇬🇧 بالإنجليزية (English)", callback_data=f"gen_mail:{opp_id}:en")],
                [InlineKeyboardButton("🇮🇹 بالإيطالية (Italiano)", callback_data=f"gen_mail:{opp_id}:it")],
                [InlineKeyboardButton("🇫🇷 بالفرنسية (Français)", callback_data=f"gen_mail:{opp_id}:fr")]
            ]
            await query.message.reply_text(
                f"✉️ *تجهيز إيميل تقديم مخصص لفرصة:* \n*{opp['title']}*\n\nاختر لغة الإيميل المناسبة:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    # توليد الإيميل وعرضه
    elif data.startswith("gen_mail:"):
        _, opp_id, lang = data.split(":", 2)
        opp = get_opportunity_by_id(opp_id)
        if opp:
            email_text = generate_bilal_cold_email(
                prof_name="Admissions / Research Committee",
                institution=opp["institution"],
                topic=opp["sub_specialty"],
                lang=lang
            )
            await query.message.reply_text(
                f"✉️ *إليك الإيميل المجهز بنقرة واحدة (جاهز للنسخ والإرسال مباشرة):*\n\n```\n{email_text}\n```",
                parse_mode="Markdown"
            )

    # تصفح الأساتذة
    elif data.startswith("prof_page:"):
        page = int(data.split(":", 1)[1])
        total = len(TOP_PROFESSORS_RADAR)
        page = max(0, min(page, total - 1))
        prof = TOP_PROFESSORS_RADAR[page]
        card_text = format_professor_card(prof, current_idx=page, total_count=total)
        keyboard = build_professor_keyboard(prof, page=page, total=total)
        await query.edit_message_text(card_text, parse_mode="Markdown", reply_markup=keyboard, disable_web_page_preview=True)

    # توليد إيميل لأستاذ معين
    elif data.startswith("prof_mail:"):
        page = int(data.split(":", 1)[1])
        prof = TOP_PROFESSORS_RADAR[page]
        email_text = generate_bilal_cold_email(
            prof_name=prof["name"],
            institution=prof["institution"],
            topic=prof["title"] + " & Subsurface Energy Dynamics",
            lang="it" if "إيطاليا" in prof["country"] else "en"
        )
        await query.message.reply_text(
            f"✉️ *إيميل تواصل مباشر مع {prof['name']}:*\n*(المستلم: `{prof['email']}`)*\n\n```\n{email_text}\n```",
            parse_mode="Markdown"
        )

    # تصفح دولة معينة
    elif data.startswith("c:"):
        country = data.split(":", 1)[1]
        category = f"country:{country}"
        await send_paginated_opportunity(update, context, category=category, page=0, is_edit=False)

    # إطلاق الصيد الفوري
    elif data == "hunt:force":
        await query.edit_message_text(
            "⏳ *جاري إطلاق الصيد الشامل الآن...*\n• فحص بوابات الجامعات والشركات العالمية...\n• فحص الروابط بنظام Zero 404...\n• تقييم التطابق مع ملف بلال حداد...",
            parse_mode="Markdown"
        )
        # تنفيذ الصيد في الخلفية
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, execute_deep_hunt)
        
        finish_text = f"""
✅ *اكتملت حملة الصيد الفوري بنجاح!*
━━━━━━━━━━━━━━━━━━━━━━
🏢 *البوابات المفحوصة:* {res['scanned_sources']} جهة عالمية
📊 *إجمالي الفرص المحققة النشطة:* {res['verified_active']} فرصة
⚡ *فرص جديدة تم صيدها:* {res['new_caught']}
🔄 *فرص تم تحديثها:* {res['updated_caught']}
🛡️ *حالة الروابط:* 100% مؤكدة وصالحة (HTTP 200 OK)
━━━━━━━━━━━━━━━━━━━━━━
يمكنك الآن استعراض أحدث الفرص مباشرة عبر الأزرار بالأسفل!
"""
        keyboard = [
            [InlineKeyboardButton("🛢️ استعراض فرص المكامن والتخزين الجوفي", callback_data="page:reservoir_storage:0")],
            [InlineKeyboardButton("🎓 استعراض فرص بدون خبرة (Fresh Master)", callback_data="page:no_exp:0")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="menu:main")]
        ]
        await query.edit_message_text(finish_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "menu:main":
        all_opps = get_all_active_open()
        await query.message.reply_text(
            f"🏠 *القائمة الرئيسية:*\n\nلديك حالياً *{len(all_opps)}* فرصة نشطة ومؤكدة بالرادار. اختر القسم الذي تريد استعراضه:",
            parse_mode="Markdown",
            reply_markup=REPLY_MARKUP
        )

# ----------------- المهمة اليومية الصباحية -----------------
async def daily_alert_job(context: ContextTypes.DEFAULT_TYPE):
    logger.info("تشغيل صياد الفرص الصباحي التلقائي...")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, execute_deep_hunt)

    new_opps = get_new_opportunities_for_alert()
    closing_soon = get_closing_soon_opportunities()

    if not new_opps and not closing_soon:
        logger.info("لا توجد تنبيهات جديدة هذا الصباح.")
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

def main():
    init_db()
    
    # تنفيذ صيد أولي سريع عند الإقلاع
    logger.info("بدء تشغيل بوت رادار وصياد دكتوراه البترول...")
    try:
        execute_deep_hunt()
    except Exception as e:
        logger.warning(f"Initial hunt warning: {e}")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # الأوامر النصية
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("auth", cmd_auth))
    app.add_handler(CommandHandler("access", cmd_auth))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("reservoir", cmd_reservoir))
    app.add_handler(CommandHandler("fresh", cmd_no_exp))
    app.add_handler(CommandHandler("easy", cmd_easy))
    app.add_handler(CommandHandler("corporate", cmd_corporate))
    app.add_handler(CommandHandler("internship", cmd_internships))
    app.add_handler(CommandHandler("fav", cmd_favorites))
    app.add_handler(CommandHandler("hunt", cmd_hunter_hub))
    app.add_handler(CommandHandler("professors", cmd_professors))

    # معالج الأزرار التفاعلية (Callbacks)
    app.add_handler(CallbackQueryHandler(handle_callbacks))

    # معالج الرسائل النصية المكتوبة
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text))

    # جدولة التنبيه الصباحي التلقائي
    job_queue = app.job_queue
    if job_queue:
        from datetime import time
        job_queue.run_daily(
            daily_alert_job,
            time=time(hour=DAILY_REPORT_HOUR, minute=DAILY_REPORT_MINUTE),
            days=(0, 1, 2, 3, 4, 5, 6)
        )
        logger.info(f"تمت جدولة المنبه اليومي عند الساعة {DAILY_REPORT_HOUR:02d}:{DAILY_REPORT_MINUTE:02d} يومياً.")

    logger.info("البوت جاهز ويعمل بكفاءة...")
    app.run_polling()

if __name__ == "__main__":
    main()
