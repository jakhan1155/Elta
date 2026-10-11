"""
Разрешает магазину, открытому с другого адреса (Vercel), обращаться к API бота.
Каталог публичный, а заказ всё равно проверяется по подписи Telegram.
"""
from aiohttp import web

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
}


@web.middleware
async def cors_middleware(request: web.Request, handler):
    if not request.path.startswith("/api/"):
        return await handler(request)
    if request.method == "OPTIONS":  # предварительный запрос браузера перед POST
        return web.Response(status=204, headers=CORS_HEADERS)
    resp = await handler(request)
    resp.headers.update(CORS_HEADERS)
    return resp
