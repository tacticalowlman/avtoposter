import typing

import aiohttp
import models


class VKMethods:
    def __init__(self, token: str):
        self.__session = aiohttp.ClientSession()
        self._BASE_URL = 'https://api.vk.com/method/'
        self.__token = token
        self._default_params = {
            'v':            '5.101',
            'access_token': token
        }

    async def _make_request(self, method: str, params: dict) -> dict:
        async with self.__session.get(self._BASE_URL + method, params=params) as resp:
            r = await resp.json()
            return r

    async def get_posts(self, group_id: int) -> typing.List[models.Post]:
        method = 'wall.get'
        raw_params = {'owner_id': group_id}
        params = self._default_params.copy()
        params.update(raw_params)
        r = await self._make_request(method, params)
        raw_data = [r['response']['items'][i] for i in range(len(r['response']['items']))]
        data = list()
        for i in raw_data:
            try:
                data.append(models.Post(**i))
            except Exception as e:
                print(e)
                print(i)
        return data


def check_posts(posts: typing.List[models.Post]) -> typing.Optional[models.Post]:
    for i in posts:
        if 'предварительная запись на ПОДАЧУ документов и КОНСУЛЬТАЦИИ осуществляется на следующие даты' in i.text:
            return i


def format_post(post: models.Post) -> typing.List[str]:
    txt = list()
    lines = post.text.splitlines()
    header_date = lines[0]
    header_text = 'предварительная запись на ПОДАЧУ документов осуществляется на следующие даты:'
    start_index = lines.index('На подачу: ')
    end_index = lines.index('На платную КОНСУЛЬТАЦИЮ ')
    txt.append(f'<b>{header_date}</b> {header_text}\n')
    tmp = lines[start_index + 1:end_index]
    tmp_new = list()
    for i in tmp:
        if 'отдельные категории' in i:
            i = i.replace('отдельные категории', 'по Указу 187')
        if ' - ' in i:
            parts = i.split(' - ')
            parts[0] = f'<b>{parts[0]}</b>'
            if 'оформление документов НРЯ' in parts[1]:
                parts[1] = 'прием по вопросам НРЯ (в том числе на уведомление о возможности приема в гражданство).'
            ready = ' - '.join(parts)
            if '(' in i:
                parts = ready.split('(')
                right_parts = parts[1].split(')')
                parts[1] = f'<i>{right_parts[0]}</i>){right_parts[1]}'
                ready = '('.join(parts)
                ready = ready.strip()
            if not ready.endswith('.'):
                ready = ready + '.'
        else:
            ready = i
        tmp_new.append(ready)
    txt.extend(tmp_new)
    txt.append('')
    txt.append('Внимание! Даты записи актуальны на 08:00, в течение дня даты могут меняться.')
    txt.append('')
    txt.append(f'Подробнее о том, <a href="https://t.me/mgrntrunews/662">как взять талон</a>')
    return txt
