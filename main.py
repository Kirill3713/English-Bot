# Импортируем модули
import telebot
from config import api_token
import logging
import random
import time
import json
# Создаем функции
def check_message(message:str, command:str) -> bool:
    """
    Функция проверяющая схожесть сообщения и команды.
    """
    message = message.lower().strip()
    command = command.lower().strip()
    punctuation = [".", ",", "!", "?", "'", '"', ";", "(", ")", ":", "—", "^", "&", "`", "[", "]", "{", "}", "<", ">", "´", "`", "´", "°", "|", "…", "\\"]
    for symb in punctuation:
        message = message.replace(symb, "")
        command = command.replace(symb, "")
    if message == command:
        return True
    message_words = message.split()
    command_words = command.split()
    if set(message_words) == set(command_words):
        return True
    if len(message_words) != len(command_words):
        return False
    message_similarity = 0
    for i in range(len(message_words)):
        message_word = message_words[i]
        command_word = command_words[i]
        words_similarity = 0
        if len(command_word) > len(message_word):
            for j in range(len(message_word)):

                if message_word[j] == command_word[0:len(message_word)][j]:
                    words_similarity += 1
        else:
            for j in range(len(command_word)):
                if len(command_word) > len(message_word):
                    if message_word[j] == command_word[0:len(message_word)][j]:
                        words_similarity += 1
                else:
                    if message_word[0:len(command_word)][j] == command_word[j]:
                        words_similarity += 1
        if words_similarity/len(command_word) >= 0.7:
            message_similarity += 1
    if message_similarity/len(command_words) >= 0.5:
        return True
    else:
        return False
def del_word(message) -> None|str:
    """
    Удаление слова.
    """
    if message.text in user_data[str(message.chat.id)].keys():
        del user_data[str(message.chat.id)][message.text]
    elif message.text in user_data[str(message.chat.id)].values():
        user_data[str(message.chat.id)] = {k: v for k, v in user_data[str(message.chat.id)].items() if v != message.text}
    else:
        bot.reply_to(message, "Такого слова у тебя пока нет. Напиши без опечаток, и тогда, возможно, получится.")
        return
    with open("user_data.json", "w", encoding="utf-8") as json_file:
        json.dump(user_data, json_file, ensure_ascii=False)
        bot.reply_to(message, f"Слово {message.text} и его перевод удалены.")
# Объявляем переменные
TOKEN = api_token
bot = telebot.TeleBot(TOKEN)
user_data = {}
try:
    with open("user_data.json", "r", encoding="utf-8") as json_file:
        user_data = json.load(json_file)
except FileNotFoundError:
    pass
# Декоратор
@bot.message_handler(commands=["start"]) # Такая функция пишется перед функцией, для которой он предназначен, в качестве аргумента указываются команды, при которых должна вызываться функция после декоратора
def handle_start(message):
    logging.info("Начинаем работу бота")
    bot.send_message(message.chat.id, "Привет! Это твой бот для обучения английских слов!")
@bot.message_handler(commands=["learn"])
def handle_learn(message):
    logging.info("Урок")
    if len(message.text.split()) == 2 or len(message.text.split()) == 1:
        if user_data != {}:
            logging.info("learn")
            user_words = user_data.get(message.chat.id, {})
            if len(message.text.split()) == 2:
                try:
                    words_number = int(message.text.strip().split()[1])
                except ValueError:
                    bot.send_message(message.chat.id, "Вторая часть команды должна быть числом.")
                    return
            else:
                words_number = 1
            ask_translation(message.chat.id, user_data[str(message.chat.id)], words_number)
        else:
            bot.send_message(message.chat.id, f"У тебя пока нет слов для изучения. Добавь их через функцию addword.")
    else:
        bot.send_message(message.chat.id, "Неверный ввод. Формат команды: /learn количество слов числом")

def ask_translation(chat_id, user_words:dict, words_left:int):
    """
    Запрашиваем перевод у пользователя.
    """
    if words_left > 0:
        word = random.choice(list(user_words.keys()))
        translation = user_words[word]
        bot.send_message(chat_id, f"Введи перевод слова '{word}'.")
        words_left -= 1
        bot.register_next_step_handler_by_chat_id(chat_id, check_translation, translation, words_left)
    else:
        bot.send_message(chat_id, "Вы повторили свои слова.")

def check_translation(message, answer:str, words_left:int):
    """
    Проверяем ответ пользователя.
    """
    user_answer = message.text.strip().lower()
    if user_answer == answer.lower().strip():
        bot.send_message(message.chat.id, "Правильно!")
    else:
        bot.send_message(message.chat.id, f"Неверно. Правильный перевод - {answer}.")
    ask_translation(message.chat.id, user_data[str(message.chat.id)], words_left)

@bot.message_handler(commands=["help"])
def handle_help(message):
    logging.info("Справка")
    bot.send_message(message.chat.id, "Привет\nЯ бот, могу помочь тебе с запоминанием английских слов. Уменя есть несколько полезных команд:\n\n/start - Команда для запуска бота\n/learn - Выбери чтобы начать урок. Если после /learn напишешь какое-то число, то я спрошу именно такое количество слов. По умолчанию стоит 1.\n/help - справка о боте (то, что ты сейчас читаешь).\n/addword - Команда для добавления нового слова. Обязательно нужно после команды написать два слова разделенных пробелами, поэтому придется название команды печатать вручную.\n/delword - Для удаления какого-нибубудь слова выбери эту команду. После этого напиши само слово или его перевод для удаления. Если что, ты потом сможешь добавить его обратно через addword\n/mywords - С помощью этой функции ты сможешь просмотреть все свои слова.\n\nТакже бот может отвечать на простые сообщения пользователя, здороваться и порщаться.")
@bot.message_handler(commands=["addword"])
def handle_addword(message):
    logging.info("Добавление слова")
    global user_data
    user_dict = user_data.get(str(message.chat.id), {})

    words = [word.strip().lower() for word in message.text.split()[1:]]

    if len(words) == 2:
        word, translation = words[0], words[1]
        user_dict[word] = translation
        user_data[str(message.chat.id)] = user_dict
        with open("user_data.json", "w", encoding="utf-8") as json_file:
            json.dump(user_data, json_file, ensure_ascii=False)
            bot.send_message(message.chat.id, f"Слово {word} добавлено в словарь.")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка. Неверный формат. Попробуйте ввести еще раз.")
@bot.message_handler(commands=["mywords"])
def handle_mywords(message):
    logging.info("Просмотр всего словаря")
    bot.send_message(message.chat.id, "Ваш словарь:")
    global user_data
    for word, translation in user_data[str(message.chat.id)].items():
        bot.send_message(message.chat.id, f"{word}: {translation}")
@bot.message_handler(commands=["delword"])
def handle_delword(message):
    logging.info("Удаление слова")
    bot.send_message(message.chat.id, "Напишите слово, которое хотите удалить:")
    bot.register_next_step_handler_by_chat_id(message.chat.id, del_word)
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    logging.info(message.text)
    if check_message(message.text, "Как дела?"):
        bot.send_message(message.chat.id, random.choice(["Нормально.", "Хорошо.", "Нормально", "Отлично"]))
    elif check_message(message.text, "Привет"):
        bot.send_message(message.chat.id, random.choice(["Привет", "Привет!", "Здравствуйте."]))
    elif check_message(message.text, "Добрый день"):
        bot.send_message(message.chat.id, random.choice(["Добрый день", "Здравствуйте."]))
    elif check_message(message.text, "Добрый вечер"):
        bot.send_message(message.chat.id, random.choice(["Добрый вечер.", "Здравствуйте."]))
    elif check_message(message.text, "Доброе утро"):
        bot.send_message(message.chat.id, random.choice(["Доброе утро!", "Здравствуйте."]))
    elif check_message(message.text, "Здравствуйте"):
        bot.send_message(message.chat.id, random.choice(["Здравствуйте", "Здравствуйте."]))
    elif check_message(message.text, "До свидания"):
        bot.send_message(message.chat.id, random.choice(["До свидания!", "Хорошего дня."]))
    elif check_message(message.text, "Пока"):
        bot.send_message(message.chat.id, "Пока")
    elif check_message(message.text, "Который час?"):
        bot.send_message(message.chat.id, f"В Софиевской Борщаговке {time.strftime("%H:%M:%S")}.")
    elif check_message(message.text, "Как тебя зовут?"):
        bot.send_message(message.chat.id, random.choice(["У меня нет имени, я бот для запоминания английских слов."]))
    elif check_message(message.text, "Что ты?"):
        bot.send_message(message.chat.id, random.choice(["Я телеграм бот. Я могу помочь тебе запомнить английские слова."]))
    else:
        bot.send_message(message.chat.id, "Извините, я не понимаю такое сообщение.")
# Точка входа
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Запуск бота . . . .")
    bot.polling(non_stop=True)