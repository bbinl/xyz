import logging
import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.error import BadRequest

# 🔐 এখানে আপনার BotFather থেকে পাওয়া টোকেন বসান
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# 📋 লগিং সেটআপ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🎯 purge_before কমান্ড হ্যান্ডলার
def purge_before(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("⚠️ তারিখ দিন এভাবে:\n`/purgebefore YYYY-MM-DD`", parse_mode="Markdown")
        return

    try:
        purge_date = datetime.datetime.strptime(context.args[0], "%Y-%m-%d")
    except ValueError:
        update.message.reply_text("❌ ভুল ফরম্যাট! লিখুন:\n`/purgebefore 2025-07-01`", parse_mode="Markdown")
        return

    chat_id = update.effective_chat.id
    update.message.reply_text(f"🧹 `{purge_date.date()}` এর আগের মেসেজগুলো ডিলিট করা হচ্ছে...", parse_mode="Markdown")

    def delete_messages(context: CallbackContext):
        last_message_id = update.message.message_id
        deleted = 0

        while True:
            try:
                messages = context.bot.get_chat_history(chat_id=chat_id, offset_id=last_message_id - 1, limit=100)
                if not messages:
                    break

                for msg in messages:
                    last_message_id = msg.message_id
                    if msg.date < purge_date:
                        try:
                            context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
                            deleted += 1
                        except BadRequest:
                            continue
            except Exception as e:
                logger.error(f"Error: {e}")
                break

        context.bot.send_message(chat_id=chat_id, text=f"✅ মোট {deleted} টি মেসেজ ডিলিট হয়েছে `{purge_date.date()}` এর আগের।", parse_mode="Markdown")

    context.job_queue.run_once(delete_messages, 0)

# 🚀 বট চালানো
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("purgebefore", purge_before))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
