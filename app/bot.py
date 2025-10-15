import logging, aiosqlite
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from .config import effective_env
from .db import DB_PATH, migrate
from . import nft

log = logging.getLogger("bot")
ENV = effective_env()
ADMIN_ID = int(ENV['ADMIN_ID']) if ENV.get('ADMIN_ID','').isdigit() else None
APPROVED_CHAT_ID = ENV.get('APPROVED_CHAT_ID','')
CONTACT_USERNAME = ENV.get('CONTACT_USERNAME','')

async def ensure_user(update: Update):
    if not update.effective_user: return
    u = update.effective_user
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (tg_id, username, first_name, last_name) VALUES (?,?,?,?)",
                         (u.id, u.username or '', u.first_name or '', u.last_name or ''))
        await db.commit()

def admin_only(fn):
    async def w(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id if update.effective_user else None
        if ADMIN_ID and uid != ADMIN_ID:
            await update.effective_chat.send_message('⛔️ אין לך הרשאות.')
            return
        return await fn(update, ctx)
    return w

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ensure_user(update)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton('📋 תפריט', callback_data='menu')]])
    await update.effective_chat.send_message('ברוך הבא לבוט של SELA ✨', reply_markup=kb)

async def on_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton('💳 תשלום והנפקת NFT', callback_data='mint')],
        [InlineKeyboardButton('📈 סטטיסטיקות', callback_data='stats')],
        [InlineKeyboardButton('🔗 קישורים לקהילה', callback_data='links')],
    ])
    await update.effective_chat.send_message('בחר פעולה:', reply_markup=kb)

async def on_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == 'menu':
        await on_menu(update, ctx)
    elif q.data == 'mint':
        await q.message.reply_text('שלח סכום ב-₪ (מספר).')
        ctx.user_data['await_amount'] = True
    elif q.data == 'stats':
        await q.message.reply_text('סטטיסטיקות: בקרוב.')
    elif q.data == 'links':
        await cmd_link(update, ctx)

async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ctx.user_data.get('await_amount'):
        t = (update.message.text or '').strip()
        try:
            amt = float(t)
        except:
            await update.message.reply_text('יש להזין מספר (₪).')
            return
        ctx.user_data.pop('await_amount', None)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO payments (tg_id, amount_nis, status) VALUES (?,?, 'pending')",
                             (update.effective_user.id, amt))
            await db.commit()
        await update.message.reply_text('💳 תשלום נרשם (ממתין). לאחר אימות ננפיק NFT.')

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message('✅ הבוט פעיל. /menu')

@admin_only
async def cmd_mint(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    args = ctx.args or []
    addr = (args[0] if args else '').strip()
    if not addr:
        await update.effective_chat.send_message('שימוש: /mint <BSC_ADDRESS>')
        return
    if not nft.is_ready():
        await update.effective_chat.send_message('⚠️ NFT/Web3 לא הוגדרו.')
        return
    tid, tx = nft.mint_unique(addr, 'ipfs://metadata.json')
    await update.effective_chat.send_message(f'🎉 הונפק NFT token_id={tid}\\n🔗 tx={tx}')

async def cmd_link(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    links = ['קבוצת תומכים (פרטית)'] if APPROVED_CHAT_ID else []
    txt = '• ' + '\\n• '.join(links) if links else 'אין קישורים כרגע.'
    await update.effective_chat.send_message(f'🔗 קישורים לקהילה:\\n{txt}')

def build_application() -> Application:
    return ApplicationBuilder().token(ENV['BOT_TOKEN']).build()

async def init_app(app: Application):
    app.add_handler(CommandHandler('start', cmd_start))
    app.add_handler(CommandHandler('menu', on_menu))
    app.add_handler(CommandHandler('status', cmd_status))
    app.add_handler(CommandHandler('mint', cmd_mint))
    app.add_handler(CommandHandler('link', cmd_link))
    app.add_handler(CallbackQueryHandler(on_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    await migrate()
