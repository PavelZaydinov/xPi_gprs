#!/usr/bin/python3

from aiohttp import web, ClientSession
from psycopg2 import connect
from contextlib import closing
from os import getenv

HTTP_API = 'https://api.telegram.org/bot%s/sendMessage'


def get_contact_name(phone: str) -> str:
    try:
        p_number = int(phone.replace('+', ''))
    except ValueError:
        return ''
    find = f"~ '{p_number}'" if p_number/100000 >= 1 else f"= '{p_number}'"
    query = f'''select string_agg(value, '; ')
    from oc_cards_properties 
    where 
        cardid in (select cardid 
        from oc_cards_properties 
        where name ='TEL'
        and replace(replace(value,' ',''), '-','') {find})
    and name in ('FN' , 'ORG', 'TITLE') group by cardid;'''
    with closing(connect(**DB)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            name = n[0][0] if len(n := cursor.fetchall()) == 1 else '; '.join([s[0] for s in n])
    return name


def phone_normalize(phone: str) -> str:
    phone = phone.strip(' ')
    if len(phone) > 10 and phone[0] != '+':
        return '+' + phone
    return phone


def data_processing(data: dict) -> dict:

    base_data = {
        'chat_id': TG_CHAT_ID,
        'parse_mode': 'HTML',
        'text': f"<b>{data['incoming']} in {data['dev']}</b>\n"
                f"Name: <i>{get_contact_name(data['phone'])}</i>\n"
                f"Phone: <i>{phone_normalize(data['phone'])}</i>"
    }
    if body := data.get('text'):
        base_data['text'] += f'\n\n{body}'
    print(base_data)
    return base_data


async def send_data_tg(url_api: str, data: dict) -> dict:
    async with ClientSession() as session:
        async with session.post(url_api, json=data) as resp:
            return await resp.json()


async def root_post(request):
    datajs = await request.json()
    return web.json_response(await send_data_tg(url, data_processing(datajs)))


if __name__ == '__main__':
    app = web.Application()
    app.router.add_post('/', root_post)
    DB = {
        "host": getenv('PG_HOST'),
        "user": getenv('PG_USER'),
        "password": getenv('PG_PASSWORD'),
        "database": getenv('PG_DB')
    }
    TG_TOKEN = getenv('TG_TOKEN')
    TG_CHAT_ID = getenv('TG_CHAT_ID')
    url = HTTP_API % TG_TOKEN
    web.run_app(app, host='0.0.0.0', port=80)
