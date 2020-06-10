import asyncio
import datetime
import json
from aiogram import Bot

import api
import utils
from data import telegram as tg_conf
from data import vk as vk_conf

vk = utils.VKMethods(vk_conf.token)
bot = Bot(token=tg_conf.token, parse_mode='HTML')


def get_today() -> datetime.datetime:
    r = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    return r


async def main():
    posts = await vk.get_posts(vk_conf.group_id)
    target_post = utils.check_posts(posts)
    if not target_post:
        return True
    last_saved = api.Posts.get_last_saved()
    get_array_dates = re.findall(r'\d{2}\s\S+\s\d{4}\s.\.', target_post)
    sp_date = re.findall(r'\d{2}\,\s\d{2}\,\s\d{2}\s\S+', target_post)
    get_array_dates.insert(1, sp_date[0])
    get_array_dates = json.dumps(get_array_dates)
    with DataConn(db_title) as conn:
            c = conn.cursor()
            sql = 'UPDATE `settings` SET `value` = ? WHERE `key` = ?'
            c.execute(sql, (get_array_dates, 'array_dates'))
            conn.commit()
    formatted = '\n'.join(utils.format_post(target_post))
    if last_saved:
        if last_saved.text == formatted:
            return True
    hours_count = api.Settings.get_time()
    if target_post.date.hour > 7:
        if target_post.date.hour < 19:
            previous_post = api.Posts.get_last_posted()
            target_post.date.replace(tzinfo=None)
            if (not previous_post) or (target_post.date - previous_post.post_time).days > 2:
                await bot.send_message(tg_conf.debugging, 'now')
                api.Posts.schedule_post(
                    formatted,
                    int(datetime.datetime.now().timestamp())
                )
            else:
                await bot.send_message(tg_conf.debugging, 'Tomorrow1')
                api.Posts.schedule_post(
                    formatted,
                    int((get_today() + datetime.timedelta(days=1, hours=hours_count)).timestamp())
                )
        else:
            await bot.send_message(tg_conf.debugging, 'Tomorrow2')
            api.Posts.schedule_post(
                formatted,
                int((get_today() + datetime.timedelta(days=1, hours=hours_count)).timestamp())
            )
    else:
        await bot.send_message(tg_conf.debugging, 'Today7')
        api.Posts.schedule_post(
            formatted,
            int((get_today() + datetime.timedelta(hours=hours_count)).timestamp())
        )


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
