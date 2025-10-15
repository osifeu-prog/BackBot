import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from telegram import Update
from app.config import require_env, effective_env
from app.bot import build_application, init_app

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("server")

ENV = effective_env()
REQ = require_env()

WEBHOOK_ROUTE = REQ.get("WEBHOOK_ROUTE", "/webhook")
PUBLIC_URL = REQ["PUBLIC_URL"]

app = FastAPI(title="SELA Bot Webhook")

tg_application = build_application()
_initialized = False

@app.on_event("startup")
async def on_startup():
    global _initialized
    if not _initialized:
        await init_app(tg_application)
        _initialized = True
        log.info("Bot application initialized.")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/set-webhook")
async def set_webhook():
    url = PUBLIC_URL.rstrip("/") + WEBHOOK_ROUTE
    if not (url.startswith("https://") or url.startswith("http://localhost")):
        return JSONResponse({"detail": "PUBLIC_URL env var is missing or not https"}, status_code=400)
    bot = tg_application.bot
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        ok = await bot.set_webhook(url)
        return {"ok": ok, "url": url}
    except Exception as e:
        log.exception("set_webhook failed")
        return JSONResponse({"detail": str(e)}, status_code=500)

@app.post(WEBHOOK_ROUTE)
async def webhook(request: Request):
    data = await request.json()
    try:
        update = Update.de_json(data, tg_application.bot)
        await tg_application.process_update(update)
    except Exception as e:
        log.exception("Failed to process update: %s", e)
        return JSONResponse({"detail": "failed"}, status_code=500)
    return Response(status_code=200)
