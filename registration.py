from bot.bot import Event
from bot.bot import Bot
from config import  city_callback_to_city, city_to_time
import json
from SQL_funcs import get_user




def register(bot : Bot, event: Event):
    user = get_user(user_id=event.from_chat)
    print (f'In registration: {user}')
    if len(user) == 0:
        buttons = []
        for callback in city_callback_to_city:
            buttons.append([{"text": city_callback_to_city[callback], "callbackData": callback, "style": "primary"}])
        bot.send_text(text='В каком городе работаешь?', 
                      chat_id=event.from_chat, 
                      inline_keyboard_markup='{}'.format(json.dumps(buttons)))
    else:
        bot.send_text(
                text = f'Вы уже зарегистрированы! '
                       f'Если вы начинаете работать в другое время, воспользуйтесь командой /setWorkTime', 
                chat_id = event.from_chat
        )
    
    