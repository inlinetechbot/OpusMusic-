# ╔══════════════════════════════════════════════╗
# ║             OpusMusic Bot                  ║
# ║      Advanced Telegram Music System         ║
# ╚══════════════════════════════════════════════╝
#
#  Feature: Join Request Welcome
#  Jab kisi user ka group/channel join request accept hota hai
#  (aur woh member ban jaata hai), bot use DM mein welcome bhejta hai.
#
#  Powered by OpusMusic
#

from pyrogram import enums, filters, types

from opus import app, config

OWNER_ID = 7185778863


def _joinrequest_buttons() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton(text="ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT),
            types.InlineKeyboardButton(text="ᴜᴘᴅᴀᴛᴇ", url=config.SUPPORT_CHANNEL),
        ],
        [
            types.InlineKeyboardButton(text="ᴏᴡɴᴇʀ", url=f"tg://user?id={OWNER_ID}"),
        ],
    ])


# ── Join request approved → DM welcome ────────────────────────────────────────
# Telegram sirf `ChatJoinRequest` event deta hai jab request *dali*
# jaati hai, uske approve/accept hone ka alag se koi seedha event
# nahi milta. Isliye yahan hum khud request ko approve karte hain
# (agar bot ke paas rights hain) aur turant DM bhej dete hain — yeh
# effectively "request accept hote hi member ko DM" wala flow hai.
# Agar approve karne ka permission na ho (bot admin nahi / invite
# users right missing), tab bhi silently skip — koi crash nahi.

@app.on_chat_join_request()
async def joinrequest_welcome(_, request: types.ChatJoinRequest):
    try:
        user = request.from_user
        if not user or user.is_bot:
            return

        chat = request.chat
        chat_name = chat.title or "ɢʀᴏᴜᴘ"
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

        try:
            await app.approve_chat_join_request(chat.id, user.id)
        except Exception:
            # Bot ke paas approve karne ka right nahi ho sakta
            # (normal member / missing invite-users permission) —
            # is case mein DM bhejna bhi skip kar dete hain kyunki
            # request abhi accept hi nahi hui.
            return

        text = (
            f"💐 ʜᴇʏ {full_name} 👋\n"
            f"💮 ᴛʜᴀɴᴋs ꜰᴏʀ ʀᴇǫᴜᴇsᴛɪɴɢ ᴛᴏ ᴊᴏɪɴ {chat_name}\n\n"
            f"ɪ'ᴍ {app.name} - ᴀ ʜɪɢʜ ǫᴜᴀʟɪᴛʏ ᴍᴜsɪᴄ sᴛʀᴇᴀᴍɪɴɢ ʙᴏᴛ ꜰᴏʀ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘs & ᴄʜᴀɴɴᴇʟs 🚀\n\n"
            f"📋 ᴊᴜsᴛ sᴇɴᴅ /start ᴛᴏ sᴇᴇ ʙᴏᴛ ᴍᴇɴᴜ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs 📋"
        )

        try:
            await app.send_message(
                chat_id=user.id,
                text=text,
                reply_markup=_joinrequest_buttons(),
            )
        except Exception:
            # User ne bot ko pehle /start nahi kiya hoga — Telegram
            # ka rule hai, bot khud DM initiate nahi kar sakta.
            # Silently skip, request already approve ho chuki hai.
            pass

    except Exception:
        pass
