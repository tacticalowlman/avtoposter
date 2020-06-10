import sqlite3
import time
import json
from pathlib import Path
from typing import Optional, List

import models
from data import telegram

def redacted(text):
    array_of_dates = Settings.get_ar()
    text_redacted = text.format(*array_of_dates)
    return text_redacted

class DataConn:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        if exc_val:
            raise


db_title = Path(__file__).parent / 'db.db'

with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT `value` FROM `settings` WHERE `key` = ?'
            c.execute(sql, ('changed_text',))
            changed_text = c.fetchone()[0]

class Posts:
    @staticmethod
    def schedule_post(text: str, post_date: int):
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'INSERT or IGNORE INTO `scheduled_posts` (`text`, `post_time`) VALUES (?, ?)'
            c.execute(sql, (text, post_date))
            conn.commit()

    @staticmethod
    def get_posts_to_send() -> Optional[models.ScheduledPost]:
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT `value` FROM `settings` WHERE `key` = ?'
            c.execute(sql, ('changed_text',))
            changed_text = c.fetchone()[0]
        Posts.edit_last_post_text(redacted(changed_text))
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT * FROM `scheduled_posts` WHERE `post_time` < ? AND `is_posted` = 0 LIMIT 1'
            c.execute(sql, (int(time.time()),))
            r = c.fetchone()
            if r:
                return models.ScheduledPost(**r)
            else:
                return None

    @staticmethod
    def mark_post_sent(post_time: int, message_id: int):
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'UPDATE `scheduled_posts` SET `is_posted` = 1 WHERE `post_time` = ?'
            c.execute(sql, (post_time,))
            conn.commit()
            sql = 'INSERT INTO `posts` (`post_time`, `chat_id`, `post_id`) VALUES (?, ?, ?)'
            c.execute(sql, (post_time, telegram.channel_id, message_id))
            conn.commit()

    @staticmethod
    def get_last_posted() -> Optional[models.ScheduledPost]:
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT * FROM `scheduled_posts` WHERE `is_posted` = 1 ORDER BY `post_time` DESC LIMIT 1'
            c.execute(sql)
            r = c.fetchone()
            if r:
                return models.ScheduledPost(**r)
            else:
                return None

    @staticmethod
    def get_last_saved() -> Optional[models.ScheduledPost]:
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT * FROM `scheduled_posts` WHERE `is_posted` = 0 ORDER BY `post_time` DESC LIMIT 1'
            c.execute(sql)
            r = c.fetchone()
            if r:
                return models.ScheduledPost(**r)
            else:
                return None

    @staticmethod
    def edit_last_post_text(text: str):
        last_post = Posts.get_last_saved()
        print('lol')
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'UPDATE `scheduled_posts` SET `text` = ? WHERE `post_time` = ?'
            c.execute(sql, (text, int(last_post.post_time.timestamp())))
            conn.commit()

    @staticmethod
    def get_posts_to_delete() -> Optional[List[models.python.Post]]:
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT * FROM `posts` ORDER BY `post_time` DESC LIMIT 20'
            c.execute(sql)
            r = c.fetchall()
            if r:
                return [models.python.Post(**i) for i in r]
            else:
                return None


class Settings:
    @staticmethod
    def set_time(value: int):
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'UPDATE `settings` SET `value` = ? WHERE `key` = ?'
            c.execute(sql, (value, 'hours'))
            conn.commit()

    @staticmethod
    def get_time() -> int:
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT `value` FROM `settings` WHERE `key` = ?'
            c.execute(sql, ('hours',))
            r = c.fetchone()
            return int(r[0])

    @staticmethod
    def chngtxt(txt):
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'UPDATE `settings` SET `value` = ? WHERE `key` = ?'
            c.execute(sql, (txt, 'changed_text'))
            conn.commit()

    @staticmethod
    def chngardts(ar):
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'UPDATE `settings` SET `value` = ? WHERE `key` = ?'
            c.execute(sql, (ar, 'array_dates'))
            conn.commit()

    @staticmethod
    def get_ar():
        with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'SELECT `value` FROM `settings` WHERE `key` = ?'
            c.execute(sql, ('array_dates',))
            array_of_dates = c.fetchone()[0]
            array_of_dates = json.loads(array_of_dates)
            return array_of_dates