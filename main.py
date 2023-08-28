from bot.bot import Bot
from bot.handler import MessageHandler
from bot.handler import BotButtonCommandHandler
from bot.bot import Event
import json
import schedule
from schedule import every
import time
from multiprocessing import Process
import multiprocessing as mp
import datetime
import config
import psycopg2
from psycopg2.extras import DictCursor
from SQL_funcs import get_user, get_not_senders_by_hour, add_user, set_silence, shift_time_diff, add_sender, senders_reset, get_not_senders
from config import  city_callback_to_city, city_to_time, time_callback_to_offset
from registration import register


TOKEN = config.SKBT_SECRETARY_TOKEN #your token here
CHAT_ID = config.SKB_CHAT_ID
#CHAT_ID = '83665@chat.agent' #тестовый




def send_menu(bot : Bot, user_id : str):
    buttons = [[
        {"text":"💻 Выбрать место работы", "callbackData":"call_back_workplace", "style": "primary"}
    ]]
    user = get_user(user_id=user_id)
    print (user)
    silensed_text = ''
    if (user['SILENCED']):
        silensed_text = '✅ Включить'
    else:
        silensed_text = '🚫 Выключить'
    buttons[0].append({"text": silensed_text, "callbackData":"call_back_silenced_switch", "style": "primary"})
    bot.send_text(text='Что хочешь сделать?', 
                  chat_id=user_id, 
                  inline_keyboard_markup='{}'.format(json.dumps(buttons)))




def send_workplace_choice(bot: Bot, chat_id: str):
    bot.send_text(chat_id=chat_id, text="Где сегодня работаешь?", inline_keyboard_markup="{}".format(json.dumps([[
            {"text":"💼 Офис", "callbackData":"call_back_office", "style": "primary"},
            {"text":"🏡 Из дома", "callbackData":"call_back_home", "style": "primary"}
        ]])))

def message_check(bot : Bot, event : Event):
    commands_list = ['/menu', '/help', '/start', '/setWorkTime', '/gimmeChatId'] 
    if (event.text in commands_list):
        if(event.text =='/gimmeChatId'):
            print (event.from_chat)
        if (event.chat_type == 'private'):
            if(event.text == '/menu'):
                send_menu(bot, event.from_chat)
            if(event.text == '/start'):
                print (f"start command")
                register(bot=bot, event=event)
            if(event.text =='/setWorkTime'):
                send_time_shift_choice(bot=bot, event=event)
            
        
        else:
            bot.send_text(text='<b>Взаимодействие с ботом вне приватного чата запрещено!</b>', chat_id=event.from_chat, parse_mode='HTML')

def send_time_shift_choice(bot: Bot, event: Event):
    print ("time shift")
    user = get_user(user_id=event.from_chat)
    if (len(user) == 0):
        bot.send_text(text='Сначала нужно зарегистрироваться! Для запуска регистрации используй команду /start', chat_id=event.from_chat)
    else:
        buttons = [
           [{"text":"08:00", "callbackData":"call_back_time_8", "style": "primary"}],
           [{"text":"09:00", "callbackData":"call_back_time_9", "style": "primary"}],
           [{"text":"10:00", "callbackData":"call_back_time_10", "style": "primary"}]
        ]
        bot.send_text(text='Выбери время начала работы', 
                  chat_id=event.from_chat, 
                  inline_keyboard_markup='{}'.format(json.dumps(buttons)))
    pass

def send_choice_in_chat(bot: Bot, place: str, event: Event):
    date = datetime.datetime.now().strftime("%d.%m.%Y")
    print('Имя\nДата ' + place + ' #работа')
    sender = " ".join([event.data['from']['lastName'], event.data['from']['firstName']])
    bot.send_text(text=f'{sender}\n{date} ' + place + ' #работа', chat_id=CHAT_ID)
    add_sender(user_id=event.from_chat)


def buttons_func(bot : Bot, event : Event):
    #Запросить выбор места работы
    if (event.data['callbackData'] == 'call_back_workplace'):
       send_workplace_choice(bot=bot, chat_id=event.from_chat) 

    #Выбрал в офисе
    if (event.data['callbackData'] == 'call_back_office'):       
        send_choice_in_chat(bot=bot, place='💼 Офис', event=event)
    
    #Выбрал из дома
    if (event.data['callbackData'] == 'call_back_home'):       
        send_choice_in_chat(bot=bot, place='🏡 Из дома', event=event)

    #Кнопка on/off
    if (event.data['callbackData'] == 'call_back_silenced_switch'):
        user = get_user(user_id=event.from_chat)
        print (f'chat ID: {event.from_chat}\n')

        if (user['SILENCED']):
            set_silence(user_id=event.from_chat, value=False)
            bot.send_text('Рассылка включена!', event.from_chat)
        else:
            set_silence(user_id=event.from_chat, value=True)
            bot.send_text('Рассылка отключена!', event.from_chat)
     
    #Выбор города во время регистрации
    if (event.data['callbackData'] in ['call_back_city_NSK', 'call_back_city_HBR', 'call_back_city_SRT', 'call_back_city_MSK']): 
        print ("City selected")
        user = get_user(user_id=event.from_chat)
        if (len(user) != 0):
            bot.send_text(
                text = f'Вы уже зарегистрированы! '
                       f'Если вы начинаете работать в другое время, воспользуйтесь командой /setWorkTime', 
                chat_id = event.from_chat
            )
        else:
            city = city_callback_to_city[event.data['callbackData']]
            add_user(
                name=" ".join([event.data['from']['lastName'], event.data['from']['firstName']]), 
                chat_id=event.from_chat, 
                diff=city_to_time[city],
                city=city
            )
            bot.send_text(
                    text = f'Вы успешно зарегистрированы! Сообщение о сегодняшнем месте работы теперь будут отправляться в 09:00 города {city}! '
                           f'Если вы начинаете работать в другое время, воспользуйтесь командой /setWorkTime', 
                    chat_id = event.from_chat
            )
    
    #Выбор времени начала работы
    if (event.data['callbackData'] in ['call_back_time_8', 'call_back_time_9', 'call_back_time_10']): 
        user = get_user(event.from_chat)
        if (len(user) == 0):
            bot.send_text(text='Сначала нужно зарегистрироваться! Для запуска регистрации используй команду /start', chat_id=event.from_chat)
        else:
            city = user['CITY']
            city_time = city_to_time[city]
            new_time_diff = city_time - time_callback_to_offset[event.data['callbackData']]
            shift_time_diff(new_time_diff=new_time_diff, user_id=event.from_chat)
            bot.send_text(text='Время успешно изменено!', chat_id=event.from_chat)
        pass


def send_report():
    week_day = datetime.datetime.now().weekday()
    if (week_day < 5):
        bot = Bot(token=TOKEN)
        users = get_not_senders()
        msg_text = 'Пользователи, не сообщившие о месте работы сегодня:\n'
        for user in users:
            msg_text += user['NAME'] + '\n'
        bot.send_text(text=msg_text, chat_id=config.BOSS_ID)

def start_schedule():
    print ("Schedule started")
    every().hour.at(":00").do(daily_question)
    every().day.at("00:00").do(senders_reset)
    every().day.at("13:00").do(senders_reset)
    while (True):
        schedule.run_pending()
        time.sleep(1)
   

def daily_question():
    bot = Bot(token=TOKEN)
    hour = datetime.datetime.now().hour
    week_day = datetime.datetime.now().weekday()
    print (f'weekday: {week_day}')
    if (week_day < 5):
        users = get_not_senders_by_hour(16 - hour)
        print(users)
        for user in users:
            send_workplace_choice(bot=bot, chat_id=user['TEAMS_ID'])
    

#------------------------------------------------------------------------------------------------



def main():
    bot = Bot(token=TOKEN)
    bot.dispatcher.add_handler(MessageHandler(callback=message_check))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=buttons_func))
    p = Process(target = start_schedule)
    p.start()
    bot.start_polling()
    bot.idle()



if __name__ == '__main__':
    main()