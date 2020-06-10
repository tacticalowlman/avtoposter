import asyncio

from aiogram import Bot

import api
from data import telegram as tg_conf

bot = Bot(token=tg_conf.token, parse_mode='HTML')


async def main():
    post = api.Posts.get_posts_to_send()
    if post:
        to_delete = api.Posts.get_posts_to_delete()
        if to_delete:
            for data in to_delete:
                try:
                    await bot.delete_message(data.chat_id, data.post_id)
                except Exception as e:
                    print(e)
        sent = await bot.send_message(tg_conf.channel_id, post.text, disable_web_page_preview=True)
        api.Posts.mark_post_sent(int(post.post_time.timestamp()), sent.message_id)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
