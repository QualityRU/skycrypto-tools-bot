from asyncio import create_task, gather, run
from random import choice

from aiohttp import ClientSession, TCPConnector

# import config

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/114.0.0.0 Safari/537.36'
)
proxies_list = list()


async def free_proxy_list():
    headers = {'User-Agent': USER_AGENT}
    async with ClientSession(headers=headers, conn_timeout=5.0) as session:
        url = 'https://free-proxy-list.net/'
        async with session.get(url) as resp:
            result = await resp.text()
            result = result.split('UTC.\n\n')[1]
            result = result.split(
                '</textarea></div><div class="modal-footer">'
            )[0]
            result = result.split('\n')
            result = list(filter(None, result))
            return result


async def fetch_check_proxies(session, url, proxy):
    try:
        async with session.get(
            url=url, proxy=proxy, verify_ssl=False
        ) as response:
            print(proxy, '- есть контакт!')
            proxies_list.append(proxy)
    except Exception as e:
        print(proxy, '- нет контакта:', e)
    # return proxies_list


async def check_proxies():
    url = 'https://skycrypto.me'
    headers = {'User-Agent': USER_AGENT}
    proxies = await free_proxy_list()
    connector = TCPConnector()
    async with ClientSession(
        headers=headers, conn_timeout=5.0, connector=connector
    ) as session:
        tasks = [
            create_task(
                fetch_check_proxies(
                    session=session, url=url, proxy=f'http://{proxy}'
                )
            )
            for proxy in proxies
        ]
        return await gather(*tasks)


run(check_proxies())
print()
print('Список прокси работающих для skycrypto.me', len(proxies_list))
print(proxies_list)
# choice(run(check_proxies()))
