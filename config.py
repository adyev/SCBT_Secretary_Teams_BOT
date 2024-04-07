SKB_CHAT_ID = '638@chat.agent' #рабочий 
#тестовый
#SKB_CHAT_ID = '83665@chat.agent'
SKBT_SECRETARY_TOKEN = "001.0309258019.1441521491:1000000101"
BOSS_ID = 'kapustinao@sovcombank.ru'
#BOSS_ID = 'adyevdv@sovcombank.ru'

DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = '183492'
DB_HOST = 'localhost'

city_callback_to_city = {
    "call_back_city_NSK":"Новосибирск",
    "call_back_city_HBR":"Хабаровск",
    "call_back_city_SRT":"Саратов",
    "call_back_city_MSK":"Москва"
}

city_to_time = {
    "Новосибирск" : 7,
    "Хабаровск" : 10,
    "Саратов" : 4,
    "Москва" : 3
}
time_callback_to_offset = {
    'call_back_time_8' : -1,
    'call_back_time_9' : 0,
    'call_back_time_10': 1
}