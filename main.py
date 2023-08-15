from bot.bot import Bot
from bot.handler import MessageHandler
import config

TOKEN = config.SKBT_SECRETARY_TOKEN

bot = Bot(token=TOKEN)

def message_cb(bot, event):
    bot.send_text(chat_id=event.from_chat, text=event.text)
    print('h')
print('h')
bot.dispatcher.add_handler(MessageHandler(callback=message_cb))
bot.start_polling()
bot.idle()