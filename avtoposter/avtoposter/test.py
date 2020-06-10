import asyncio

import api
import utils
from data import vk as vk_conf

vk = utils.VKMethods(vk_conf.token)


async def main():
    posts = await vk.get_posts(vk_conf.group_id)
    target_post = utils.check_posts(posts)
    if not target_post:
        return True
    last_saved = api.Posts.get_last_saved()
    formatted = '\n'.join(utils.format_post(target_post))
    print(formatted)

asyncio.get_event_loop().run_until_complete(main())

