# -*- coding: utf-8 -*-
import os
import openai
import telebot
from telebot import types
from telebot.types import Message, Chat
import conf

openai.api_key = conf.OPENAI_API_KEY
#openai.api_key = os.getenv("OPENAI_API_KEY")
bot = telebot.TeleBot(conf.EDU_BOT_ID)
init_message = None
user_answer = None
user_text = None
waiting = None
replay = None
new = None
chat_history = {}
count = 0

behavior_prompt = "Ты чат-бот для помощи в обучении"

def await_user_massage(message):
    global user_answer
    user_answer = message.text 

@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который сделает твой образовательный процесс интереснее. Давай начнем!\nДля просмотра функционала введите /info")

@bot.message_handler(commands=['init'])
def init(message):
    bot.send_message(message.chat.id, "Задайте тему, по которой хотите пройти обучение")
    bot.register_next_step_handler(message, get_topic)
    # global init_message
    # init_message = None
    # init_message = message.text
    # if init_message is not None:
    #     bot.send_message(message.chat.id, "Тема успешно задана: " + init_message)

def get_topic(message: types.Message):
    global init_message
    global waiting
    global user_answer
    global new 
    if waiting == None:
        init_message = message.text
        bot.send_message(message.chat.id, "Тема успешно задана: " + init_message)
    else:
        new = message.text
        waiting = 'done'


def get_answers(message: types.Message):
    global waiting
    waiting = message.text 
    recommendation = f'Пользователь дал ответ на вопросы {replay} ответы {user_answer}. Дай пользователю обртную связь, рекомендации, укажи на ошибки' 
    if count == 1:
        main(recommendation)
    else:
        count = 0
    


@bot.message_handler(commands=['testing'])
def testing(message):
    # Создание и настройка клавиатуры с двумя кнопками
    keyboard = types.InlineKeyboardMarkup()
    first_button = types.InlineKeyboardButton('В школе', callback_data='school')
    second_button = types.InlineKeyboardButton('В ВУЗе', callback_data='university')
    third_button = types.InlineKeyboardButton('Нигде не учусь', callback_data='nostudy')
    keyboard.row(first_button)
    keyboard.row(second_button)
    keyboard.row(third_button)
    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id, 'Выбери один из вариантов ниже, чтоб начать тестирование', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == 'school':
        if init_message == None:
            bot.send_message(call.message.chat.id, 'Тема не задана, введите /init для задания темы')
        else:
            user_message = f'Сгенерируй 5 вопросов для школьника по теме {init_message}'
            chat_id = call.message.chat.id
            chat = Chat(id = chat_id, type = 'private')
            message_object = Message(message_id=1, from_user=None, date=None, chat=chat, content_type=None, options={}, json_string=None)
            message_object.text = user_message
            #user_message.encoding = 'utf-8-sig'
            #user_text = user_message.text
            main(message_object)
    elif call.data == 'university':
        if init_message == None:
            bot.send_message(call.message.chat.id, 'Тема не задана, введите /init для задания темы')
        else:
            user_message = f'Сгенерируй 5 сложных вопросов для студента по теме {init_message}'
            chat_id = call.message.chat.id
            chat = Chat(id = chat_id, type = 'private')
            message_object = Message(message_id=1, from_user=None, date=None, chat=chat, content_type=None, options={}, json_string=None)
            message_object.text = user_message
            main(message_object)   
    elif call.data == 'nostudy':
        if init_message == None:
            bot.send_message(call.message.chat.id, 'Тема не задана, введите /init для задания темы')
        else:
            user_message = f'Сгенерируй 5 средних по сложности вопросов по теме {init_message}'
            chat_id = call.message.chat.id
            chat = Chat(id = chat_id, type = 'private')
            message_object = Message(message_id=1, from_user=None, date=None, chat=chat, content_type=None, options={}, json_string=None)
            message_object.text = user_message
            main(user_message)

@bot.message_handler(commands=['destroy'])
def destroy_history(message):
    chat_history.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "История чата удалена.")

@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, "/destroy - очистить историю переписки, чтоб начать диалог в другом контексте\n/testing - пройти тестирование для получения рекоменаций")

@bot.message_handler(content_types=['text'])
def main(message):
    replay = ''
    global count
    count=count+1
    user_message = message.text
    
    if message.chat is not None:
        prev_user_message = chat_history.get(message.chat.id, "")
    else:
        prev_user_message = ""

    

    input_messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": prev_user_message},
            {"role": "system", "content": behavior_prompt}
        ]

    chat_history[message.chat.id] = user_message
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=input_messages
        )
        
        if completion and completion.choices:
            replay = completion.choices[0].message['content'].strip()
        else:
            replay = 'Не работает'

        bot.send_message(message.chat.id, replay) 

        if user_message == f'Сгенерируй 5 вопросов для школьника по теме {init_message}' or user_message == f'Сгенерируй 5 сложных вопросов для студента по теме {init_message}' or user_message == f'Сгенерируй 5 средних по сложности вопросов по теме {init_message}':
            global waiting 
            global user_answer
            global new
            waiting = 'test'
            bot.register_next_step_handler(message, get_topic)
            while waiting != 'done':
                pass  
            
            recommendation = f'Были заданы вопросы: {replay}. Пользователь дал ответы: {new}. Дай пользователю обртную связь, рекомендации, укажи на ошибки. Не генирируй новые вопросы!' 
            chat_id = message.chat.id
            chat = Chat(id = chat_id, type = 'private')
            message_object = Message(message_id=1, from_user=None, date=None, chat=chat, content_type=None, options={}, json_string=None)
            message_object.text = recommendation

            if count == 1:
                #bot.send_message(message_object.chat.id, message_object.text)
                main(message_object)
            else:
                count = 0
    except:
        bot.send_message(message.chat.id, "Не удалось обработать запрос")
   # else:
       # bot.send_message(message.chat.id, "Условие не выполнилось")





bot.polling(non_stop=True)

## Нужно протестить с объясни понятнее и прочее. 
