import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from .auth import create_access_token, decode_token, hash_password, verify_password
from .database import (
    create_user,
    delete_all_history,
    delete_history,
    delete_user,
    get_history,
    get_user_by_username,
    init_db,
    save_history,
)
from .qr_service import generate_qr_code

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://qr-generator-fullstack.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================= 認証ヘルパー =================
def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="認証が必要です")
    token = authorization.removeprefix("Bearer ")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="トークンが無効です")
    return payload


# ================= スキーマ =================
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class QRRequest(BaseModel):
    qr_type: str = "url"
    content: str
    label_text: str = ""
    label_position: str = "Top"
    expires_at: str | None = None


# ================= ルート =================
@app.get("/")
def read_root():
    return {"status": "ok"}


# ---- ユーザー管理 ----
@app.post("/api/register")
def register(body: RegisterRequest):
    if get_user_by_username(body.username):
        raise HTTPException(
            status_code=400, detail="このユーザー名は既に使われています"
        )
    create_user(body.username, hash_password(body.password))
    return {"ok": True}


@app.post("/api/login")
def login(body: LoginRequest):
    user = get_user_by_username(body.username)
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401, detail="ユーザー名またはパスワードが違います"
        )
    token = create_access_token(user["id"], user["username"])
    return {"access_token": token, "username": user["username"]}


@app.delete("/api/user")
def remove_user(current_user: dict = Depends(get_current_user)):
    delete_user(current_user["user_id"])
    return {"ok": True}


# ---- QRコード生成 ----
@app.post("/api/qr")
async def create_qr(
    body: QRRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        qr_bytes = generate_qr_code(
            body.qr_type,
            body.content,
            body.label_text,
            body.label_position,
        )
        save_history(
            user_id=current_user["user_id"],
            qr_type=body.qr_type,
            content=body.content,
            label_text=body.label_text,
            label_position=body.label_position,
            expires_at=body.expires_at,
        )
        return Response(content=qr_bytes, media_type="image/png")
    except Exception as e:
        logging.error(f"QR生成エラー: {e}")
        raise HTTPException(status_code=500, detail="QRコードの生成に失敗しました")


# ---- 履歴管理 ----
@app.get("/api/history")
def list_history(current_user: dict = Depends(get_current_user)):
    return get_history(current_user["user_id"])


@app.delete("/api/history")
def remove_all_history(current_user: dict = Depends(get_current_user)):
    delete_all_history(current_user["user_id"])
    return {"ok": True}


@app.delete("/api/history/{history_id}")
def remove_history(
    history_id: int,
    current_user: dict = Depends(get_current_user),
):
    delete_history(history_id, current_user["user_id"])
    return {"ok": True}
