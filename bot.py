# Balishious AI Bot - Buttons + Image
import os 
from flask import Flask
import threading
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Balishious Bot Live!"
def run_flask(): flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
PRICE = "Basic Setup: $15\nHosting: $5/month\nDelivery 1-2 days"
LOCATION = "Kahna Lahore, Pakistan - Worldwide"
CONTACT = "Telegram: @balishious_ai_bot\nFiverr: Inbox me\nInsta: @relax_peter"
PRODUCTS = "24/7 AI Bot\nEnglish & Roman Urdu\nGroq AI + Image Gen"
GROQ_KEY = os.getenv("GROQ_API_KEY")
user_state = {}

def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Price", callback_data="price"), InlineKeyboardButton("📍 Location", callback_data="loc")],
        [InlineKeyboardButton("📞 Contact", callback_data="cont"), InlineKeyboardButton("🛍️ Products", callback_data="prod")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello {update.effective_user.first_name}! 🤖 Balishious Bot\nTry /image cat", reply_markup=keyboard())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - Start\n/image cat - Generate image\n/help - Help", reply_markup=keyboard())

async def image_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args) if context.args else "cute cat"
    await update.message.reply_text(f"Generating: {prompt}... 🎨")
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    await update.message.reply_photo(photo=url, caption=f"{prompt}", reply_markup=keyboard())

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data=="price": await q.message.reply_text(PRICE, reply_markup=keyboard())
    if q.data=="loc": await q.message.reply_text(LOCATION, reply_markup=keyboard())
    if q.data=="cont": await q.message.reply_text(CONTACT, reply_markup=keyboard())
    if q.data=="prod": await q.message.reply_text(PRODUCTS, reply_markup=keyboard())
def groq_reply(text):
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": "You are Balishious AI assistant. Reply in English + Roman Urdu mix, friendly, short."}, {"role": "user", "content": text}]}, timeout=20)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Sorry, thoda masla hua - dobara likhein!"
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
  
    reply = groq_reply(update.message.text)
    await update.message.reply_text(reply, reply_markup=keyboard())
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("image", image_cmd))
app.add_handler(CallbackQueryHandler(btn))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
