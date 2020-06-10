# -*- coding: utf-8 -*-
import json
import sqlite3
import telebot
from telebot import types
import re
import text
import logging

bot = telebot.TeleBot(text.token, threaded=False)

class DB:       #Подключение к бд
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()

def change_text(target_post):       #Подстановка дат в текст
    text = (DB.cursor.execute('select `text` from `info`').fetchone())[0]
    sp_date = re.findall(r'^.*\n', target_post)        #Вытаскиваем своевременные даты
    sp_date[0] = sp_date[0][0:-2]
    array_dates = re.findall(r'.* -', target_post)
    arlen = len(array_dates)
    for i in range(4):
        array_dates[i] = array_dates[i][0:-2]
    for i in range(arlen-1, 3, -1):
        array_dates.pop(i)
    array_dates.insert(0, sp_date[0])       #Вставляем даты
    text_red = text.format(*array_dates)
    return text_red

@bot.channel_post_handler(content_types=['text'])       #Ожидание подходящего поста
def reciever(msg: types.Message):
    print('okok')
    if msg.text.find(text.post_text) != -1:
        channel_id = (DB.cursor.execute('select `channel_id` from `info`').fetchone())[0]
        channel_id2 = (DB.cursor.execute('select `channel_id2` from `info`').fetchone())[0]
        delmes = (DB.cursor.execute('select `delmes` from `info`').fetchone())[0]
        if delmes != 0:
            try:
                bot.delete_message(channel_id2, delmes)     #Удаление предыдущего поста в постящем канале
            except Exception as e:
                print(e)
        delmes = bot.send_message(channel_id2, change_text(msg.text), parse_mode = 'Markdown', disable_web_page_preview = 'True')       #Отправка отредактированного поста
        DB.cursor.execute('update `info` set `delmes` = ?', (delmes.message_id,))
        DB.conn.commit()

@bot.message_handler(commands=['start'], func=lambda msg: msg.from_user.id == 138526122 or msg.from_user.id == 396706690)        #Меню
def usermenu(msg: types.Message):
    text_ch = (DB.cursor.execute('select `text` from `info`').fetchone())[0]
    bot.send_message(msg.chat.id, text.helper + text_ch + text.helper2)

@bot.message_handler(commands=['cansel'])       #Отказ то записи
def usermenu(msg: types.Message):
    DB.cursor.execute('update `info` set `state` = ?, `state2` = ?', (0, 0))
    DB.conn.commit()
    bot.send_message(msg.chat.id, 'Действие успешно отменено.')

@bot.message_handler(commands=['change_text'])      #Смена основное части текста
def usermenu(msg: types.Message):
    bot.send_message(msg.chat.id, 'Отправьте нужный текст.\nЧтобы отменить изменение текста, отправьте команду /cansel.')
    DB.cursor.execute('update `info` set `state` = ?', (1,))

@bot.message_handler(commands=['change_channel_geter'])     #Смена канала родителя
def usermenu(msg: types.Message):
    bot.send_message(msg.chat.id, text.changing_id_text)
    DB.cursor.execute('update `info` set `state2` = ?', (1,))

@bot.message_handler(commands=['change_channel_sender'])        #Смена канала постера
def usermenu(msg: types.Message):
    bot.send_message(msg.chat.id, text.changing_id_text2)
    DB.cursor.execute('update `info` set `state3` = ?', (1,))

@bot.message_handler(content_types=['text'], func=lambda msg:       #Запись основной части текста
(DB.cursor.execute('select `state` from `info`').fetchone())[
    0] == 1)
def readreport(msg: types.Message):
    DB.cursor.execute('update `info` set `text` = ?', (msg.text, ))
    DB.cursor.execute('update `info` set `state` = ?', (0,))
    DB.conn.commit()
    bot.send_message(msg.chat.id, 'Текст успешно изменен.')

@bot.message_handler(content_types=['text'], func=lambda msg:       #Запись id канала родителя
(DB.cursor.execute('select `state2` from `info`').fetchone())[
    0] == 1)
def chng(msg: types.Message):
    DB.cursor.execute('update `info` set `channel_id` = ?', (msg.text, ))
    DB.cursor.execute('update `info` set `state2` = ?', (0,))
    DB.cursor.execute('update `info` set `delmes` = ?', (0,))
    DB.conn.commit()
    bot.send_message(msg.chat.id, 'Id канала успешно изменен.')

@bot.message_handler(content_types=['text'], func=lambda msg:       #Запись id канала постера
(DB.cursor.execute('select `state3` from `info`').fetchone())[
    0] == 1)
def chng(msg: types.Message):
    DB.cursor.execute('update `info` set `channel_id2` = ?', (msg.text, ))
    DB.cursor.execute('update `info` set `state3` = ?', (0,))
    DB.cursor.execute('update `info` set `delmes` = ?', (0,))
    DB.conn.commit()
    bot.send_message(msg.chat.id, 'Id канала успешно изменен.')
    

while True:
    try:
            bot.polling(none_stop=True)
    except Exception as err:
            logging.error(err)