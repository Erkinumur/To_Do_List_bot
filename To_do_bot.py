
import telebot
from telebot import types
import json


token = "1165336826:AAHB5Rd9KT3B4lzepQFhwC7TbRkjyQ-0P68"
bot = telebot.TeleBot(token)


markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
btn1 = types.KeyboardButton("📋 Посмотреть список дел")
btn2 = types.KeyboardButton("➕ Добавить дело")
btn3 = types.KeyboardButton("🗑 Очистить список")
btn4 = types.KeyboardButton("🔚 Выйти")
markup_menu.add(btn1, btn2, btn3, btn4)

#/start
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, text='Приветствую.\nЯ бот помощник "To do list".\nВыберите действие ниже:', reply_markup=markup_menu)
    bot.register_next_step_handler(message, selector)

def selector(message):
    text = message.text
    if text == "📋 Посмотреть список дел":
        show_list(message)
    elif text == "➕ Добавить дело":
        add_assignment(message)
    elif text == '🗑 Очистить список':
        clear_list(message)
    elif text == '🔚 Выйти':
        end(message)
    else:
        bot.send_message(message.chat.id, 'Я не смог распознать команду. Попробуйте еще раз.\nВыберите действие:')
        bot.register_next_step_handler(message, selector)

def show_list(message):
    try:
        chat_id = message.chat.id
        with open('todolist.json', 'r') as f:
            data = json.load(f)
            user_id = str(message.from_user.id)

        markup = types.InlineKeyboardMarkup()
        btn_update = types.InlineKeyboardButton('Редактировать дело', callback_data='update')
        btn_delete = types.InlineKeyboardButton('Удалить дело', callback_data='delete')
        btn_back = types.InlineKeyboardButton('Назад', callback_data='back')
        markup.add(btn_update, btn_delete, btn_back)

        if user_id in data['users']:      
            result = ''
            num = 1
            for i in data['users'][user_id]:
                result += f'{num}. {i}\n'
                num += 1
            bot.send_message(chat_id, result, reply_markup=markup)
            
        else:
            bot.send_message(chat_id, 'Вы еще не добавили ни одного пункта', reply_markup=markup_menu)
            bot.register_next_step_handler(message, selector)
            
            
    except Exception as e:
        print('show list: ', e)
        bot.send_message(message.chat.id, 'Упс. Что то пошло не так. Попробуйте еще раз.', reply_markup=markup_menu)
        bot.register_next_step_handler(message, selector)


def add_assignment(message):
    
    bot.send_message(message.chat.id, 'Введите пункт, который хотите добавить:')
    bot.register_next_step_handler(message, reply)

def reply(message):
    try:  
        with open('todolist.json', "r") as f:
            data = json.load(f)
            user_id = str(message.from_user.id)
            if user_id in data['users']:
                data['users'][user_id].append(message.text)
            else:
                data['users'][user_id] = [message.text]
        with open('todolist.json', 'w') as f:
            json.dump(data, f, indent=4)
        bot.send_message(message.chat.id, 'Пункт добавлен', reply_markup=markup_menu)
        bot.register_next_step_handler(message, selector)
    except Exception as e:
        print('reply: ', e)
        bot.send_message(message.chat.id, 'Упс. Что то пошло не так. Попробуйте еще раз.', reply_markup=markup_menu)
        bot.register_next_step_handler(message, selector)



def clear_list(message):
    try:
        chat_id = message.chat.id
        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton('Да', callback_data='yes')
        btn_no = types.InlineKeyboardButton('Нет', callback_data='no')
        markup.add(btn_yes, btn_no)
        bot.send_message(chat_id, text="Уверены что хотите очистить список?", reply_markup=markup)
    except Exception as e:
        print('clear list: ', e)
        bot.send_message(message.chat.id, 'Упс. Что то пошло не так. Попробуйте еще раз.', reply_markup=markup_menu)
        bot.register_next_step_handler(message, selector)

@bot.callback_query_handler(func=lambda call:True)
def calls(call):
    if call.data == "yes":
        with open('todolist.json', 'r') as f:
            data = json.load(f)
            user_id = str(call.message.chat.id)
            # print(call.message)
        if user_id in data['users']:
            data['users'].pop(user_id)
            with open('todolist.json', 'w') as f:
                json.dump(data, f, indent=4)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Список очищен")
            bot.send_message(call.message.chat.id, 'Выберите действие:', reply_markup=markup_menu)
            bot.register_next_step_handler(call.message, selector)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Вы еще не добавили ни одного пункта')
            bot.send_message(call.message.chat.id, 'Выберите действие:', reply_markup=markup_menu)
            bot.register_next_step_handler(call.message, selector)
    elif call.data == 'no':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Изменений нет')
        bot.send_message(call.message.chat.id, 'Выберите действие:', reply_markup=markup_menu)
        bot.register_next_step_handler(call.message, selector) 
    elif call.data == 'update':
        bot.send_message(chat_id=call.message.chat.id, text='Введите номер пункта, который хотите изменить:')
        bot.register_next_step_handler(call.message, update_list)
    elif call.data == 'delete':
        bot.send_message(chat_id=call.message.chat.id, text='Введите номер пункта, который хотите удалить:')
        bot.register_next_step_handler(call.message, delete_task)
    elif call.data == 'back':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Меню")
        bot.send_message(chat_id=call.message.chat.id, text='Выберите действие:', reply_markup=markup_menu)
        bot.register_next_step_handler(call.message, selector)

      
update = 0
def update_list(message):
    global update
    update = int(message.text)
    bot.send_message(message.chat.id, 'Введите новый пункт:')
    bot.register_next_step_handler(message, update_list2)

def update_list2(message):
    try:
        with open('todolist.json', "r") as f:
            data = json.load(f)
            user_id = str(message.from_user.id)
        data['users'][user_id][update-1] = message.text
        with open('todolist.json', 'w') as f:
            json.dump(data, f, indent=4) 
        bot.send_message(message.chat.id, 'Изменения внесены', reply_markup=markup_menu)
        bot.register_next_step_handler(message, selector)
    except Exception as e:
        print('update list: ', e)
        bot.send_message(message.chat.id, 'Упс. Что то пошло не так. Попробуйте еще раз.', reply_markup=markup_menu)
        bot.register_next_step_handler(message, selector)

delete_num = 0
def delete_task(message):
    try:
        global delete_num
        delete_num = int(message.text)
        with open('todolist.json', "r") as f:
            data = json.load(f)
            user_id = str(message.from_user.id)
        if len(data['users'][user_id]) > 1:
            data['users'][user_id].pop(delete_num-1)
        else:
            data['users'].pop(user_id)
        with open('todolist.json', 'w') as f:
            json.dump(data, f, indent=4) 
        bot.send_message(message.chat.id, 'Изменения внесены', reply_markup=markup_menu)
        bot.register_next_step_handler(message, selector)
    except Exception as e:
        print('delete task: ', e)
        bot.send_message(message.chat.id, 'Упс. Что то пошло не так. Попробуйте еще раз.')


def end(message):
    bot.send_message(message.chat.id, 'До свидания.\nДля возврата наберите "/start"')

# @bot.message_handler(content_types=['text'])
# def unknown_comand(message):
#     bot.send_message(message.chat.id, 'Я не смог распознать команду. Попробуйте еще раз.\nВыберите действие:', reply_markup=markup_menu)
#     bot.register_next_step_handler(message, selector)



bot.polling(none_stop=True)

