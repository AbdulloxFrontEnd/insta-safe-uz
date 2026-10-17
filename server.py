import os
import json
import re
import logging
import threading
import time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from checker import BannedChecker
from database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")

db = Database()

app = FastAPI(
    title="Uzbekistan Multi-Platform Safety Scanner",
    description="Система автоматической проверки подписок и каналов (Telegram, YouTube, Instagram, Facebook, TikTok) на запрещенные материалы Верховного суда РУз",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def no_cache_middleware(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path == "/" or path.endswith((".html", ".js", ".css")):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

checker = BannedChecker()

# Rate limiting and flood protection
ACTIVE_CHECKS_LOCK = set()
LAST_CHECK_TIME = {}
CHECK_SEMAPHORE = threading.Semaphore(5)

class CheckSingleRequest(BaseModel):
    query: str
    platform: Optional[str] = None  # telegram, youtube, instagram, facebook, tiktok, or None (auto)
    telegram_id: Optional[int] = None

class CheckListRequest(BaseModel):
    items: List[str]
    platform: Optional[str] = None
    telegram_id: Optional[int] = None

class CreateOrderRequest(BaseModel):
    telegram_id: int
    package: str = "single"  # single (10000), pack3 (25000), unlimited (49000)
    provider: Optional[str] = "click"

class ConfirmOrderRequest(BaseModel):
    order_id: str

@app.get("/api/info")
def get_info():
    stats = checker.get_stats()
    return {
        "status": "online",
        "title": "Uzbekistan Multi-Platform Safety Scanner (Telegram, YouTube, Instagram, Facebook)",
        "total_banned_items": stats["total_banned"],
        "by_platform": stats["by_platform"],
        "source": "Ўзбекистон Республикаси Олий судининг расмий рўйхати (2026 йил ҳолатига)"
    }

@app.get("/api/banned-list")
def get_banned_list(platform: Optional[str] = None, search: Optional[str] = None):
    plat = platform.lower().strip() if platform and platform.lower().strip() != "all" else None
    results = checker.search_registry(query=search or "", platform=plat)
    return {
        "total": len(results),
        "platform": plat or "all",
        "items": results
    }

@app.get("/api/user/status")
def get_user_status(telegram_id: int = Query(...), username: Optional[str] = "", first_name: Optional[str] = ""):
    user = db.get_or_create_user(telegram_id, username or "", first_name or "")
    status = db.get_user_status(telegram_id)
    return {"success": True, "user": status}

@app.post("/api/payment/create-order")
def create_payment_order(req: CreateOrderRequest):
    PACKAGES = {
        "single": {"name": "1 разовая проверка", "amount": 10000, "checks": 1},
        "pack3": {"name": "3 проверки (семья / друзья)", "amount": 25000, "checks": 3},
        "unlimited": {"name": "Неограниченно на месяц", "amount": 49000, "checks": 100}
    }
    pkg = PACKAGES.get(req.package, PACKAGES["single"])
    order_id = db.create_order(req.telegram_id, pkg["amount"], pkg["checks"], req.provider or "click")

    # Load merchant configurations from bot_config.json if provided
    cfg = {}
    config_path = os.path.join(os.path.dirname(__file__), "bot_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass

    click_service_id = cfg.get("click_service_id", "32014")
    click_merchant_id = cfg.get("click_merchant_id", "24018")
    payme_merchant_id = cfg.get("payme_merchant_id", "64b182e01fa2")

    return_url = f"{cfg.get('webapp_url', 'http://localhost:8000')}/?payment_success=1&order_id={order_id}"

    # Click URL
    click_url = (
        f"https://my.click.uz/services/pay?service_id={click_service_id}"
        f"&merchant_id={click_merchant_id}"
        f"&amount={pkg['amount']}"
        f"&transaction_param={order_id}"
        f"&return_url={return_url}"
    )

    # Payme URL
    import base64
    payme_params = f"m={payme_merchant_id};ac.order_id={order_id};a={pkg['amount'] * 100}"
    payme_b64 = base64.b64encode(payme_params.encode()).decode()
    payme_url = f"https://checkout.paycom.uz/{payme_b64}"

    return {
        "success": True,
        "order_id": order_id,
        "amount_uzs": pkg["amount"],
        "package_name": pkg["name"],
        "checks_count": pkg["checks"],
        "click_url": click_url,
        "payme_url": payme_url
    }

@app.post("/api/payment/confirm-order")
def confirm_payment_order(req: ConfirmOrderRequest):
    success = db.complete_order(req.order_id)
    return {"success": success}

# Official Click Webhook
@app.post("/api/payment/click/callback")
async def click_webhook(request: Request):
    form_data = await request.form()
    click_trans_id = form_data.get("click_trans_id")
    merchant_trans_id = form_data.get("merchant_trans_id")
    action = form_data.get("action")

    logger.info(f"Click Webhook: action={action}, order_id={merchant_trans_id}")

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (merchant_trans_id,))
        order = cursor.fetchone()

    if not order:
        return {"error": -5, "error_note": "Order does not exist"}

    if action == "0":
        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_prepare_id": merchant_trans_id,
            "error": 0,
            "error_note": "Success"
        }
    elif action == "1":
        db.complete_order(merchant_trans_id)
        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_confirm_id": merchant_trans_id,
            "error": 0,
            "error_note": "Success"
        }

    return {"error": -1, "error_note": "Unknown action"}

# Official Payme JSON-RPC Webhook
@app.post("/api/payment/payme/callback")
async def payme_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        return {"error": {"code": -32700, "message": "Parse error"}, "id": None}

    method = data.get("method")
    params = data.get("params", {})
    req_id = data.get("id")

    order_id = params.get("account", {}).get("order_id")

    if method == "CheckPerformTransaction":
        if not order_id:
            return {"error": {"code": -31050, "message": {"ru": "Заказ не найден", "uz": "Buyurtma topilmadi"}}, "id": req_id}
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            order = cursor.fetchone()
        if not order:
            return {"error": {"code": -31050, "message": {"ru": "Заказ не найден", "uz": "Buyurtma topilmadi"}}, "id": req_id}

        return {
            "result": {
                "allow": True,
                "detail": {
                    "receipt_type": 0,
                    "items": [{
                        "title": "InstaSafe UZ tekshiruv paketi",
                        "price": order["amount_uzs"] * 100,
                        "count": 1,
                        "code": "10899001001000000",
                        "vat_percent": 0,
                        "package_code": "123456"
                    }]
                }
            },
            "id": req_id
        }

    elif method in ["PerformTransaction", "CreateTransaction"]:
        if order_id:
            db.complete_order(order_id)
        return {
            "result": {
                "transaction": str(params.get("id", order_id)),
                "perform_time": int(time.time() * 1000),
                "state": 2
            },
            "id": req_id
        }

    return {"result": {"state": 2}, "id": req_id}

@app.get("/api/admin/stats")
def get_admin_stats():
    return {"success": True, "stats": db.get_stats(), "registry_stats": checker.get_stats()}

# FAST SINGLE CHECK (Telegram channel, YouTube channel, Instagram account, Facebook page)
@app.post("/api/check-single")
def check_single(req: CheckSingleRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query is empty")

    user_key = f"tg_{req.telegram_id}" if req.telegram_id else f"ip_{query}"
    now = time.time()
    last_time = LAST_CHECK_TIME.get(user_key, 0)
    if now - last_time < 2.0:
        return {
            "success": False,
            "error_type": "RATE_LIMIT_COOLDOWN",
            "message": "Iltimos, keyingi tekshiruvdan oldin 2 soniya kuting. / Подождите 2 секунды перед следующим запросом."
        }
    LAST_CHECK_TIME[user_key] = now

    # Check trial / paid balance if telegram_id is provided
    if req.telegram_id:
        can_check, left, ctype = db.can_perform_check(req.telegram_id)
        if not can_check:
            return {
                "success": False,
                "error_type": "PAYMENT_REQUIRED",
                "message": "Вы использовали бесплатную попытку проверки. Пожалуйста, приобретите доступ для продолжения."
            }

    match = checker.check_single_account(query, platform=req.platform)
    
    # Deduct check if matched or user completed a valid query
    user_status = None
    if req.telegram_id:
        db.deduct_check(req.telegram_id)
        user_status = db.get_user_status(req.telegram_id)

    is_safe = match is None
    result = {
        "is_safe": is_safe,
        "query": query,
        "platform": req.platform or (match.get("platform") if match else "unknown"),
        "total_checked": 1,
        "banned_count": 0 if is_safe else 1,
        "clean_count": 1 if is_safe else 0,
        "banned_found": [{
            "username": query,
            "full_name": match.get("matched_field", "") if match else "",
            "details": match
        }] if match else []
    }

    return {
        "success": True,
        "query": query,
        "result": result,
        "user_status": user_status
    }

# BATCH / LIST CHECK
@app.post("/api/check-list")
def check_list(req: CheckListRequest):
    if not req.items:
        raise HTTPException(status_code=400, detail="Список пуст")

    if req.telegram_id:
        can_check, left, ctype = db.can_perform_check(req.telegram_id)
        if not can_check:
            return {
                "success": False,
                "error_type": "PAYMENT_REQUIRED",
                "message": "Вы использовали бесплатную попытку проверки. Пожалуйста, приобретите доступ для продолжения."
            }

    followings = [{"username": u.strip(), "full_name": ""} for u in req.items if u.strip()]
    analysis = checker.analyze_following_list(followings, platform=req.platform or "telegram")

    user_status = None
    if req.telegram_id:
        db.deduct_check(req.telegram_id)
        user_status = db.get_user_status(req.telegram_id)

    return {
        "success": True,
        "result": analysis,
        "user_status": user_status
    }

# UNIVERSAL FILE CHECK: supports Instagram following.json, Telegram Desktop result.json, YouTube CSV, and TXT lists!
@app.post("/api/check-file")
async def check_file(file: UploadFile = File(...), telegram_id: Optional[int] = Form(None)):
    if telegram_id:
        can_check, left, ctype = db.can_perform_check(telegram_id)
        if not can_check:
            return {
                "success": False,
                "error_type": "PAYMENT_REQUIRED",
                "message": "Вы использовали бесплатную попытку проверки. Пожалуйста, приобретите доступ для продолжения."
            }

    content_bytes = await file.read()
    content_str = content_bytes.decode("utf-8", errors="ignore")
    fname = (file.filename or "").lower()

    # 1. Check if Telegram Desktop export (result.json or has 'chats')
    if "chats" in content_str or "public_channel" in content_str or "result" in fname:
        analysis = checker.analyze_telegram_export(content_str)
        analysis["platform"] = "telegram"

    # 2. Check if YouTube subscriptions CSV (has 'Channel Id' or ends with .csv)
    elif fname.endswith(".csv") or "Channel Id" in content_str or "channel/UC" in content_str:
        analysis = checker.analyze_youtube_export(content_str)
        analysis["platform"] = "youtube"

    # 3. Check if Instagram following.json
    elif "relationships_following" in content_str or fname.startswith("following"):
        followings = []
        try:
            data = json.loads(content_str)
            rel_list = []
            if isinstance(data, dict):
                rel_list = data.get("relationships_following") or []
                if not rel_list:
                    for k, v in data.items():
                        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict) and ("string_list_data" in v[0] or "title" in v[0]):
                            rel_list = v
                            break

                for item in rel_list:
                    uname = ""
                    if isinstance(item, dict):
                        if item.get("title"):
                            uname = item["title"]
                        if not uname:
                            for s in item.get("string_list_data", []):
                                if s.get("value"):
                                    uname = s["value"]
                                    break
                                elif s.get("href"):
                                    m = re.search(r"instagram\.com/(?:_u/)?([^/?#]+)", s["href"])
                                    if m:
                                        uname = m.group(1)
                                        break
                    elif isinstance(item, str):
                        uname = item

                    if uname:
                        clean_u = uname.strip().replace("@", "")
                        if clean_u:
                            followings.append({"username": clean_u, "full_name": ""})
        except Exception:
            pass

        analysis = checker.analyze_following_list(followings, platform="instagram")
        analysis["platform"] = "instagram"

    # 4. Fallback: plain text list of lines / usernames
    else:
        items = [line.strip() for line in content_str.splitlines() if line.strip()]
        followings = [{"username": u, "full_name": ""} for u in items]
        analysis = checker.analyze_following_list(followings, platform="all")

    user_status = None
    if telegram_id:
        db.deduct_check(telegram_id)
        user_status = db.get_user_status(telegram_id)

    return {
        "success": True,
        "file_name": file.filename,
        "platform": analysis.get("platform", "general"),
        "total_parsed": analysis.get("total_checked", 0),
        "result": analysis,
        "user_status": user_status
    }

# HIGH-SPEED SCREENSHOT CHECK (Telegram / Instagram / YouTube / Facebook channels screenshot)
@app.post("/api/check-screenshot")
async def check_screenshot(
    file: UploadFile = File(...),
    platform: Optional[str] = Form(None),
    telegram_id: Optional[int] = Form(None)
):
    if telegram_id:
        can_check, left, ctype = db.can_perform_check(telegram_id)
        if not can_check:
            return {
                "success": False,
                "error_type": "PAYMENT_REQUIRED",
                "message": "Вы использовали бесплатную попытку проверки. Пожалуйста, приобретите доступ для продолжения."
            }

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image file")

    analysis = checker.analyze_screenshot(image_bytes, platform=platform)

    user_status = None
    if telegram_id:
        db.deduct_check(telegram_id)
        user_status = db.get_user_status(telegram_id)

    return {
        "success": True,
        "file_name": file.filename,
        "platform": analysis.get("platform", platform or "screenshot"),
        "total_parsed": analysis.get("total_checked", 0),
        "result": analysis,
        "user_status": user_status
    }

# Serve static directory with resilient search across public, static, and root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEARCH_DIRS = [
    BASE_DIR,
    os.path.join(BASE_DIR, "public"),
    os.path.join(BASE_DIR, "static"),
    os.getcwd(),
    os.path.join(os.getcwd(), "public"),
    os.path.join(os.getcwd(), "static"),
    "/var/task",
    "/var/task/public",
    "/var/task/static",
]

def find_file(relative_name: str) -> Optional[str]:
    for d in SEARCH_DIRS:
        target = os.path.join(d, relative_name)
        if os.path.exists(target):
            return target
    return None

STATIC_DIR = next((d for d in SEARCH_DIRS if os.path.exists(os.path.join(d, "index.html"))), BASE_DIR)

async def serve_index():
    index_file = find_file("index.html")
    if index_file and os.path.exists(index_file):
        response = FileResponse(index_file)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return {
        "status": "ok",
        "message": "InstaSafe Scanner API is running, but index.html was not found",
        "searched_dirs": SEARCH_DIRS,
        "files_in_base_dir": os.listdir(BASE_DIR) if os.path.exists(BASE_DIR) else []
    }

@app.get("/")
@app.get("/api/index.py")
@app.get("/api")
@app.get("/api/")
@app.get("/index.html")
async def get_index():
    return await serve_index()

@app.get("/app.js")
@app.get("/static/app.js")
@app.get("/public/app.js")
async def get_app_js():
    js_file = find_file("app.js")
    if js_file and os.path.exists(js_file):
        response = FileResponse(js_file, media_type="application/javascript")
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        return response
    raise HTTPException(status_code=404, detail="app.js not found")

@app.get("/gifs/{gif_name}")
@app.get("/static/gifs/{gif_name}")
@app.get("/public/gifs/{gif_name}")
async def get_gif(gif_name: str):
    gif_file = find_file(os.path.join("gifs", gif_name)) or find_file(gif_name)
    if gif_file and os.path.exists(gif_file):
        return FileResponse(gif_file, media_type="image/gif")
    raise HTTPException(status_code=404, detail=f"GIF {gif_name} not found")

if os.path.exists(STATIC_DIR):
    try:
        app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    except Exception:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
