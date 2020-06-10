# -*- coding: utf-8 -*-
import json
import sqlite3
import telebot
from telebot import types
import re
import text
import logging

bot = telebot.TeleBot(text.token, threaded=False)

class DB:
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()

def change_text(target_post):
    text = (DB.cursor.execute('select `text` from `info`').fetchone())[0]
    array_dates = re.findall(r'\d{2}\s\S+\s\d{4}\s.\.', target_post)
    sp_date = re.findall(r'\d{2}\,\s\d{2}\,\s\d{2}\s\S+', target_post)
    array_dates.insert(1, sp_date[0])
    text_red = text.format(*array_dates)
    return text_red

@bot.channel_post_handler(content_types=['text'])
def reciever(msg: types.Message):
    if msg.text.find(text.post_text) != -1:
        channel_id = (DB.cursor.execute('select `channel_id` from `info`').fetchone())[0]
        channel_id2 = (DB.cursor.execute('select `channel_id2` from `info`').fetchone())[0]
        delmes = (DB.cursor.execute('select `delmes` from `info`').fetchone())[0]
        print('ok')
        bot.delete_message(channel_id, msg.message_id)
        print('ok')
        bot.delete_message(channel_id2, delmes)
        print('ok')
        delmes = bot.send_message(channel_id2, change_text(msg.text), parse_mode = 'Markdown', disable_web_page_preview = 'True')
        DB.cursor.execute('update `info` set `delmes` = ?', (delmes.id, ))
        DB.conn.commit()

@bot.message_handler(commands=['start'])
def usermenu(msg: types.Message):
    text_ch = (DB.cursor.execute('select `text` from `info`').fetchone())[0]
    bot.send_message(msg.chat.id, text.helper + text_ch + text.helper2)

@bot.message_handler(commands=['cansel'])
def usermenu(msg: types.Message):
    DB.cursor.execute('update `info` set `state` = ?, `state2` = ?', (0, 0))
    DB.conn.commit()
    bot.send_message(msg.chat.id, 'Действие успешно отменено.')

@bot.message_handler(commands=['change_text'])
def usermenu(msg: types.Message):
    bot.send_message(msg.chat.id, 'Отправьте нужный текст.\nЧтобы отменить изменение текста, отправьте команду /cansel.')
    DB.cursor.execute('update `info` set `state` = ?', (1,))

@bot.message_handler(commands=['change_channel_geter'])
def usermenu(msg: types.Message):
    bot.send_message(msg.chat.id, text.changing_id_text)
    DB.cursor.execute('update `info` set `state2` = ?', (1,))

@bot.message_handler(commands=['change_channel_sender'])
def usermenu(msg: types.Message):
    bot.send_message(msg.chat.id, text.changing_id_text2)
    DB.cursor.execute('update `info` set `state3` = ?', (1,))

@bot.message_handler(content_types=['text'], func=lambda msg:
(DB.cursor.execute('select `state` from `info`').fetchone())[
    0] == 1)
def readreport(msg: types.Message):
    DB.cursor.execute('update `info` set `text` = ?', (msg.text, ))
    DB.cursor.execute('update `info` set `state` = ?', (0,))
    DB.conn.commit()
    bot.send_message(msg.chat.id, 'Текст успешно изменен.')

@bot.message_handler(content_types=['text'], func=lambda msg:
(DB.cursor.execute('select `state2` from `info`').fetchone())[
    0] == 1)
def chng(msg: types.Message):
    DB.cursor.execute('update `info` set `channel_id` = ?', (msg.text, ))
    DB.cursor.execute('update `info` set `state2` = ?', (0,))
    DB.conn.commit()
    bot.send_message(msg.chat.id, 'Id канала успешно изменен.')

@bot.message_handler(content_types=['text'], func=lambda msg:
(DB.cursor.execute('select `state3` from `info`').fetchone())[
    0] == 1)
def chng(msg: types.Message):
    DB.cursor.execute('update `info` set `channel_id2` = ?', (msg.text, ))
    DB.cursor.execute('update `info` set `state3` = ?', (0,))
    DB.conn.commit()
    bot.send_message(msg.chat.id, 'Id канала успешно изменен.')
    

while True:
    try:
            bot.polling(none_stop=True)
    except Exception as err:
            logging.error(err)