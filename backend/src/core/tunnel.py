"""
Временный https-адрес магазина через cloudflared (Quick Tunnel), пока нет своего сервера с доменом.
Следит за туннелем и поднимает его заново, если адрес перестал открываться.
"""
import asyncio
import logging
import re
import socket
from pathlib import Path

from aiogram import Bot
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from aiohttp.abc import AbstractResolver

from src.config import settings
from src.core.bot import set_shop_button

tunnel_proc = None


async def start_tunnel():
    """Запускает cloudflared и ждёт адрес. Адрес меняется при каждом запуске."""
    proc = await asyncio.create_subprocess_exec(
        settings.CLOUDFLARED, "tunnel", "--url", f"http://127.0.0.1:{settings.WEB_PORT}", "--no-autoupdate",
        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE)
    url, loop = None, asyncio.get_running_loop()
    deadline = loop.time() + 45
    while url is None and loop.time() < deadline:
        try:
            line = await asyncio.wait_for(proc.stderr.readline(), deadline - loop.time())
        except asyncio.TimeoutError:
            break
        if not line:
            break
        # адрес туннеля; служебный api.trycloudflare.com (бывает в тексте ошибок) — не он
        m = re.search(rb"https://(?!api\.)[a-z0-9-]+\.trycloudflare\.com", line)
        if m:
            url = m.group(0).decode()

    async def drain():  # читаем вывод дальше, иначе cloudflared зависнет на переполненном буфере
        while await proc.stderr.readline():
            pass
    asyncio.create_task(drain())
    return proc, url


class EdgeResolver(AbstractResolver):
    """Отправляет запрос на сервер Cloudflare по известному IP, не спрашивая DNS о новом адресе.
    Иначе Windows запоминает «адрес не найден», пока туннель ещё регистрируется."""
    def __init__(self, ip: str):
        self.ip = ip

    async def resolve(self, host, port=0, family=socket.AF_INET):
        return [{"hostname": host, "host": self.ip, "port": port, "family": socket.AF_INET,
                 "proto": 0, "flags": socket.AI_NUMERICHOST}]

    async def close(self):
        pass


async def url_alive(url: str) -> bool:
    """Открывается ли магазин по публичному адресу (полная проверка через Cloudflare)."""
    try:
        infos = await asyncio.get_running_loop().getaddrinfo("api.trycloudflare.com", 443, family=socket.AF_INET)
        conn = TCPConnector(resolver=EdgeResolver(infos[0][4][0]), use_dns_cache=False)
        async with ClientSession(connector=conn, timeout=ClientTimeout(total=15)) as s:
            async with s.get(url + "/api/catalog") as r:
                return r.status == 200
    except Exception:
        return False


async def tunnel_supervisor(bot: Bot):
    """Держит туннель живым: поднимает его, следит за ним и перезапускает,
    если cloudflared упал или адрес перестал открываться (после сна, обрыва интернета)."""
    global tunnel_proc
    if not Path(settings.CLOUDFLARED).exists():
        logging.warning("cloudflared не найден (%s) — мини-приложение недоступно", settings.CLOUDFLARED)
        return
    delay = 30  # пауза между неудачными попытками растёт до 5 мин, чтобы Cloudflare не ограничивал частые запросы
    while True:
        proc, url = await start_tunnel()
        tunnel_proc = proc
        ready = False
        if url:  # ждём, пока новый адрес реально заработает (до 90 сек)
            for _ in range(30):
                if proc.returncode is not None:
                    break
                if await url_alive(url):
                    ready = True
                    break
                await asyncio.sleep(3)
        if not ready:
            logging.warning("Не удалось поднять туннель (%s), повтор через %s сек", url or "нет адреса", delay)
            if proc and proc.returncode is None:
                proc.terminate()
            await asyncio.sleep(delay)
            delay = min(delay * 2, 300)
            continue
        delay = 30
        settings.webapp_url = url
        try:
            await set_shop_button(bot, url)
        except Exception:
            logging.exception("Не удалось обновить кнопку меню")
        failures = 0
        while proc.returncode is None and failures < 2:
            try:
                await asyncio.wait_for(proc.wait(), timeout=60)  # проверка каждую минуту
            except asyncio.TimeoutError:
                failures = 0 if await url_alive(url) else failures + 1
        logging.warning("Туннель не отвечает (%s) — перезапускаю", url)
        if proc.returncode is None:
            proc.terminate()
        await asyncio.sleep(3)


def stop_tunnel() -> None:
    if tunnel_proc and tunnel_proc.returncode is None:
        tunnel_proc.terminate()
