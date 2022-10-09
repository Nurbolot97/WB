import telebot
import time
import csv
import pandas as pd
from telebot import types
from selenium import webdriver
from decouple import config
from selenium.webdriver.common.by import By


driver = webdriver.Chrome(executable_path='/Users/mac/Downloads/chromedriver')
bot = telebot.TeleBot(token=config("TOKEN"), parse_mode=None)

tip_board = types.InlineKeyboardMarkup(row_width=2)
btn1 = types.InlineKeyboardButton('Поисковый запрос', callback_data = 'search')
btn2 = types.InlineKeyboardButton('По бренду', callback_data = 'brand')
btn3 = types.InlineKeyboardButton('По категории', callback_data = 'category')
tip_board.add(btn1, btn2, btn3)


@bot.message_handler(commands=['start', 'help', 'info'])
def start(message):
    chat_id = message.chat.id
    if message.text == "/start":
        bot.send_message(chat_id, "Приветствую! \nВыберите тип запроса:", reply_markup=tip_board)
    elif message.text == "/help":
        bot.send_message(chat_id, "Для связи с создателем бота пишите\nна этот аккаунт: @nurbadai")
    elif message.text == "/info":
        bot.send_message(chat_id, "Данный бот предназначен для парсинга данных\nиз интернет-магазина Вайлдберриз.\nСбор информации осуществляется по\n3-типам запроса.")
    else:
        bot.send_message(chat_id, "Нажмите /start для начала")
        
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, "Нажмите /start для начала, \nа если Вы нажали выберите тип запросa")

@bot.callback_query_handler(func=lambda c: True)
def call_inline(c):
    chat_id = c.message.chat.id
    
    if c.data == "search":
        msg = bot.send_message(chat_id, "Напишите чего хотите поискать:")
        bot.register_next_step_handler(msg, get_info_brand)
    elif c.data == "brand":
        msg = bot.send_message(chat_id, "Напишите название бренда:")
        bot.register_next_step_handler(msg, get_info_brand)
    elif c.data == "category":
        msg = bot.send_message(chat_id, "Вставьте URL-адрес категории:")
        bot.register_next_step_handler(msg, get_category)
    else:
        bot.send_message(chat_id, "Вы ввели неправильные данные! \nВведите правильные:", reply_markup=tip_board)

def get_info_brand(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Пожалуйста ожидайте...")
    from_telegram = message.text
    url = "https://www.wildberries.ru/catalog/0/search.aspx?sort=popular&search=" + f"{from_telegram}"
    driver.get(url)
    time.sleep(2)
    
    try:
        selen_data = driver.find_element(By.CLASS_NAME, "catalog-page__text")
        if selen_data:
            bot.send_message(chat_id, selen_data.text)
            bot.send_message(chat_id, "Повторите попытку", reply_markup=tip_board)
    except:
        brands_name = driver.find_elements(By.CLASS_NAME, "brand-name")  
        goods_name = driver.find_elements(By.CLASS_NAME, "goods-name")
        price = driver.find_elements(By.CLASS_NAME, "lower-price")
        marks = driver.find_elements(By.CLASS_NAME, "product-card__count")
                        
        df = pd.DataFrame.from_dict({"brands_name": [i.text for i in brands_name], 
                                    "goods_name": [j.text for j in goods_name], 
                                    "price": [n.text for n in price],
                                    "marks": [k.text for k in marks]})
        df.to_csv('./wb.csv') 
                    
        bot.send_message(chat_id, "Ваш готовый файл:")
        document = open("wb.csv", "rb")
        bot.send_document(chat_id, document)
        bot.send_message(chat_id, "Возвращаю Вас на главное", reply_markup=tip_board)

def get_category(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Пожалуйста ожидайте...")
    url = f"{message.text}"
    
    if url.startswith("https://www.wildberries.ru/"):
        driver.get(url)
        time.sleep(2)
        try:
            selen_data = driver.find_element(By.CLASS_NAME, "content404__title")
            if selen_data:
                bot.send_message(chat_id, selen_data.text)
                bot.send_message(chat_id, "Повторите попытку", reply_markup=tip_board)
        except:
            brands_name = driver.find_elements(By.CLASS_NAME, "brand-name")  
            goods_name = driver.find_elements(By.CLASS_NAME, "goods-name")
            price = driver.find_elements(By.CLASS_NAME, "lower-price")
            marks = driver.find_elements(By.CLASS_NAME, "product-card__count")
                            
            df = pd.DataFrame.from_dict({"brands_name": [i.text for i in brands_name], 
                                        "goods_name": [j.text for j in goods_name], 
                                        "price": [n.text for n in price],
                                        "marks": [k.text for k in marks]})
            df.to_csv('./wb.csv') 
                        
            bot.send_message(chat_id, "Ваш готовый файл:")
            document = open("wb.csv", "rb")
            bot.send_document(chat_id, document)
            bot.send_message(chat_id, "Возвращаю Вас на главное", reply_markup=tip_board)
    else:
        bot.send_message(chat_id, "Введите данные правильно и повторите попытку!", reply_markup=tip_board)

def main():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()





