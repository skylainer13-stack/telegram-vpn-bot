# bot.py — OpenVPN (Корейские серверы) + Shadowsocks Bot (декабрь 2025)
import asyncio
from datetime import datetime
from io import BytesIO
import base64
from urllib.parse import quote
import qrcode
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from aiogram.exceptions import TelegramBadRequest

TOKEN = "7270293398:AAEJ5XrmsE66BfyC5z3_23J-2bewkVNJmGE"
bot = Bot(token=TOKEN)
dp = Dispatcher()

menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🇰🇷 OpenVPN Корея", callback_data="openvpn")],
    [InlineKeyboardButton(text="🔥 Shadowsocks (с QR)", callback_data="shadowsocks")],
    [InlineKeyboardButton(text="🔄 Обновить меню", callback_data="refresh")],
])

# Корейские OpenVPN серверы (из VPN Gate + VPNBook, актуально декабрь 2025)
KOREA_OPENVPN = [
    {"h": "korea.vpnjantit.com", "p": 1194, "pr": "UDP", "c": "🇰🇷 Сеул"},
    {"h": "kr1.vpnjantit.com", "p": 1194, "pr": "UDP", "c": "🇰🇷 Сеул"},
    {"h": "kr2.vpnjantit.com", "p": 1194, "pr": "UDP", "c": "🇰🇷 Пусан"},
    {"h": "korea.vpnbook.com", "p": 1194, "pr": "UDP", "c": "🇰🇷 Корея (VPNBook)"},
    {"h": "kr.vpnjantit.com", "p": 443, "pr": "TCP", "c": "🇰🇷 Сеул (TCP)"},
]

OP_TEMPLATE = "client\ndev tun\nproto {prl}\nremote {h} {p}\nresolv-retry infinite\nnobind\npersist-key\npersist-tun\nremote-cert-tls server\ncipher AES-256-GCM\nauth SHA512\nauth-nocache\nverb 3"

# Shadowsocks (остаётся)
SHADOWSOCKS_SERVERS = [
    {"h": "ru-ss.ipracevpn.com", "p": 2443, "m": "aes-256-gcm", "pw": "racevpn", "c": "🇷🇺 Россия (Москва)", "n": "racevpn.com"},
    {"h": "sg.freeshadowsock.com", "p": 443, "m": "chacha20-ietf-poly1305", "pw": "freesg", "c": "🇸🇬 Сингапур", "n": "jagoanssh.com"},
    {"h": "fr-ss.vpncreate.com", "p": 8443, "m": "aes-256-gcm", "pw": "freefr", "c": "🇫🇷 Франция", "n": "vpncreate.com"},
    {"h": "uk-ss.vpncreate.com", "p": 8443, "m": "aes-128-gcm", "pw": "freeuk", "c": "🇬🇧 Великобритания", "n": "vpncreate.com"},
    {"h": "us-ss.vpnhack.com", "p": 8388, "m": "chacha20-ietf-poly1305", "pw": "vpnhack", "c": "🇺🇸 США", "n": "vpnhack.com"},
]

SS_JSON = '{{"server": "{h}","server_port": {p},"local_address": "127.0.0.1","local_port": 1080,"password": "{pw}","timeout": 300,"method": "{m}","fast_open": false,"remarks": "{c}"}}'

def ss_link(h, p, m, pw, c):
    enc = base64.urlsafe_b64encode(f"{m}:{pw}".encode()).decode().rstrip("=")
    enc_c = quote(c)
    return f"ss://{enc}@{h}:{p}#{enc_c}"

def generate_qr(ss_link):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(ss_link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

async def safe_edit(cb, t):
    if cb.message.text != t:
        try:
            await cb.message.edit_text(t, reply_markup=menu)
        except TelegramBadRequest:
            pass

@dp.message(CommandStart())
async def start(m: types.Message):
    await m.answer("🇰🇷 *OpenVPN Корея + Shadowsocks Bot*\n\nВыбери:", parse_mode="Markdown", reply_markup=menu)

@dp.callback_query(lambda c: c.data == "refresh")
async def refresh(c: types.CallbackQuery):
    await safe_edit(c, "🔄 Обновляю меню...")

@dp.callback_query(lambda c: c.data == "openvpn")
async def openvpn_h(c: types.CallbackQuery):
    await safe_edit(c, "🇰🇷 Генерирую корейские OpenVPN .ovpn…")
    medals = "🥇🥈🥉🏅🏅"
    for i, s in enumerate(KOREA_OPENVPN):
        medal = medals[i] if i < len(medals) else "⭐"
        cap = f"{medal} *{s['c']}*\n📍 Порт: {s['p']} | Протокол: {s['pr']}\nСоздай аккаунт на vpnjantit.com или vpnbook.com"
        cfg = OP_TEMPLATE.format(prl=s["pr"].lower(), h=s["h"], p=s["p"])
        bio = BytesIO(cfg.encode('utf-8'))
        bio.seek(0)
        await c.message.answer_document(BufferedInputFile(bio.read(), filename=f"ovpn_{s['h']}_{s['p']}.ovpn"), caption=cap, parse_mode="Markdown")
        await asyncio.sleep(0.5)
    await c.message.answer("✅ Готово! Корейские серверы отправлены", reply_markup=menu)

@dp.callback_query(lambda c: c.data == "shadowsocks")
async def shadowsocks_h(c: types.CallbackQuery):
    await safe_edit(c, "🔥 Генерирую Shadowsocks конфиги…")
    medals = "🥇🥈🥉🏅🏅"
    for i, s in enumerate(SHADOWSOCKS_SERVERS):
        medal = medals[i] if i < len(medals) else "⭐"
        link = ss_link(s["h"], s["p"], s["m"], s["pw"], s["c"])

        # .json файл
        cfg = SS_JSON.format(h=s["h"], p=s["p"], pw=s["pw"], m=s["m"], c=s["c"])
        cfg_bio = BytesIO(cfg.encode('utf-8'))
        cfg_bio.seek(0)
        await c.message.answer_document(BufferedInputFile(cfg_bio.read(), filename=f"ss_{s['h']}_{s['p']}.json"),
                                        caption=f"{medal} *{s['c']}*\nПорт: {s['p']} | Метод: {s['m']}\n{s['n']}", parse_mode="Markdown")

        # QR-код
        qr_bio = generate_qr(link)
        await c.message.answer_photo(BufferedInputFile(qr_bio.read(), filename="qr.png"),
                                     caption=f"{medal} *QR-код для {s['c']}*\n📱 Сканируй камерой → импорт!\n\n`{link}`\nНажми → Копировать", parse_mode="Markdown")

        await asyncio.sleep(0.8)

    await c.message.answer("✅ Готово Shadowsocks!", reply_markup=menu)

async def main():
    print("Бот с корейскими OpenVPN запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
