import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ChatMemberHandler, filters, ContextTypes
from telegram import Update

# Put your token here for now (or let Render handle it if you set the env variable)
TOKEN = os.environ.get("BOT_TOKEN", "9183507924:AAFCC9DegVW3y1Wk58uZ4qjRAnbg9wm2Ulw")

# Add bad words inside the list (lowercase)
BAD_WORDS = ["spam", "scam", "badword"]

# 1. Welcome new members
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    # Check if a new user just joined
    if result.old_chat_member.status in ["left", "kicked"] and result.new_chat_member.status == "member":
        user = result.new_chat_member.user
        welcome_text = f"Welcome to the group, {user.first_name}! 🎉 Please read the rules."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)

# 2. Word filter (deletes bad words)
async def filter_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message or not message.text:
        return

    text_lower = message.text.lower()
    
    # Check if any bad word is in the message
    if any(word in text_lower for word in BAD_WORDS):
        try:
            await message.delete()
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=f"⚠️ {message.from_user.first_name}, watch your language! Message deleted."
            )
        except Exception as e:
            print(f"Could not delete message (make sure bot is admin): {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_bad_words))

    # Render provides the PORT and URL automatically
    PORT = int(os.environ.get("PORT", 8080))
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

    if RENDER_URL:
        # Running on Render (Webhook mode)
        print(f"Starting webhook on {RENDER_URL}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN, # Using token as a secret path
            webhook_url=f"{RENDER_URL}/{TOKEN}"
        )
    else:
        # Running locally on your phone (Polling mode)
        print("Starting polling... Bot is running locally!")
        app.run_polling()