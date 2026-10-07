# ╔══════════════════════════════════════════════╗
# ║             OpusMusic Bot                  ║
# ║      Advanced Telegram Music System         ║
# ╚══════════════════════════════════════════════╝

import html

from pyrogram import enums, filters, types

from opus import app, config
#&&

# ── Request / confirm message ki image (yahan apna URL daalo) ─────────────────
RQS_IMG_URL = "https://files.catbox.moe/beec33.png"

_pending: dict[str, dict] = {}


def _key(chat_id: int, user_id: int) -> str:
    return f"{chat_id}:{user_id}"


def _esc(text: str) -> str:
    return html.escape(text or "")


def _request_buttons(chat_id: int, user_id: int) -> types.InlineKeyboardMarkup:
    # Owner ke DM wale Accept / Reject buttons
    return types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton(
                text="✅ ᴀᴄᴄᴇᴘᴛ",
                callback_data=f"jreq accept {chat_id} {user_id}",
                style=enums.ButtonStyle.SUCCESS,
            ),
            types.InlineKeyboardButton(
                text="❌ ʀᴇᴊᴇᴄᴛ",
                callback_data=f"jreq reject {chat_id} {user_id}",
                style=enums.ButtonStyle.DANGER,
            ),
        ],
    ])


def _user_buttons() -> types.InlineKeyboardMarkup:
    # Request karne wale user ko jane wale dono messages ke buttons
    #   Row 1: Add me
    #   Row 2: Support | Update
    return types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ",
                url=f"https://t.me/{app.username}?startgroup=true",
                style=enums.ButtonStyle.SUCCESS,
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="ꜱᴜᴘᴘᴏʀᴛ",
                url=config.SUPPORT_CHAT,
                style=enums.ButtonStyle.PRIMARY,
            ),
            types.InlineKeyboardButton(
                text="ᴜᴘᴅᴀᴛᴇ",
                url=config.SUPPORT_CHANNEL,
                style=enums.ButtonStyle.PRIMARY,
            ),
        ],
    ])


def _request_text(full_name: str, chat_title: str) -> str:
    # Request daalte hi user ko jane wala message
    return (
        f"💐 ʜᴇʏ {_esc(full_name)} 👋\n\n"
        f"💮 ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ʀᴇǫᴜᴇsᴛɪɴɢ <b>{_esc(chat_title)}</b>\n\n"
        f"ɪ'ᴍ {_esc(app.name)} - ᴧ ʜɪɢʜ ǫᴜᴧʟɪᴛʏ ᴍᴜsɪᴄ sᴛʀєᴧᴍɪηɢ ʙσᴛ "
        f"ғσʀ ᴛєʟєɢʀᴧᴍ ɢʀσᴜᴘs & ᴄʜᴧηηєʟs 🚀\n\n"
        f"ᴊᴜsᴛ sєηᴅ /start ᴛσ sєє ʙσᴛ ᴍєηᴜ ᴧηᴅ ᴄσᴍᴍᴧηᴅs 📋"
    )


def _confirm_text(full_name: str, chat_title: str) -> str:
    # Request accept hone ke baad user ko jane wala message
    return (
        f"💐 ʜᴇʏ {_esc(full_name)} 👋\n\n"
        f"🎉 ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ <b>{_esc(chat_title)}</b> ʜᴀs ʙᴇᴇɴ ᴀᴄᴄᴇᴘᴛᴇᴅ\n\n"
        f"ɪ'ᴍ {_esc(app.name)} - ᴧ ʜɪɢʜ ǫᴜᴧʟɪᴛʏ ᴍᴜsɪᴄ sᴛʀєᴧᴍɪηɢ ʙσᴛ "
        f"ғσʀ ᴛєʟєɢʀᴧᴍ ɢʀσᴜᴘs & ᴄʜᴧηηєʟs 🚀\n\n"
        f"ᴊᴜsᴛ sєηᴅ /start ᴛσ sєє ʙσᴛ ᴍєηᴜ ᴧηᴅ ᴄσᴍᴍᴧηᴅs 📋"
    )


async def _send_user_msg(target_id: int, text: str) -> None:
    """Image + caption + buttons bhejta hai. Image fail ho to sirf text bhejta hai."""
    markup = _user_buttons()
    try:
        if RQS_IMG_URL:
            await app.send_photo(
                chat_id=target_id,
                photo=RQS_IMG_URL,
                caption=text,
                reply_markup=markup,
            )
            return
    except Exception:
        pass  # image URL kharab / photo fail - neeche text bhej denge
    try:
        await app.send_message(chat_id=target_id, text=text, reply_markup=markup)
    except Exception:
        # User ko DM nahi ja saka (window expire / DM band) - skip.
        pass


# -- Naya join request aane par -> user ko msg + sabhi owners ko DM -----------

@app.on_chat_join_request()
async def joinrequest_notify_owner(_, request: types.ChatJoinRequest):
    try:
        user = request.from_user
        if not user or user.is_bot:
            return

        chat = request.chat
        chat_title = chat.title or "ɢʀᴏᴜᴘ"
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else "ɴᴏɴᴇ"

        # Telegram request ke baad kuch der ke liye user_chat_id se DM allow karta hai
        # (user ne bot start na kiya ho tab bhi).
        user_chat_id = getattr(request, "user_chat_id", None) or user.id

        # 1) Request karne wale user ko message
        await _send_user_msg(user_chat_id, _request_text(full_name, chat_title))

        # 2) Owners ko DM (Accept / Reject)
        text = (
            f"📥 <b>ɴᴇᴡ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ</b>\n\n"
            f"👤 ɴᴀᴍᴇ: {_esc(full_name)}\n"
            f"🆔 ᴜsᴇʀ ɪᴅ: <code>{user.id}</code>\n"
            f"🔗 ᴜsᴇʀɴᴀᴍᴇ: {username}\n"
            f"💬 ᴄʜᴀᴛ: {_esc(chat_title)} (<code>{chat.id}</code>)\n\n"
            f"ᴀᴄᴄᴇᴘᴛ ᴏʀ ʀᴇᴊᴇᴄᴛ ᴛʜɪs ʀᴇǫᴜᴇsᴛ?"
        )

        key = _key(chat.id, user.id)
        _pending[key] = {
            "messages": {},  # owner_id -> message_id
            "chat_title": chat_title,
            "full_name": full_name,
            "user_chat_id": user_chat_id,
            "handled": False,
        }

        for owner_id in config.OWNER_ID:
            try:
                sent = await app.send_message(
                    chat_id=owner_id,
                    text=text,
                    reply_markup=_request_buttons(chat.id, user.id),
                )
                _pending[key]["messages"][owner_id] = sent.id
            except Exception:
                # Owner ne bot ko start nahi kiya ya DM band hai - skip.
                continue

    except Exception:
        pass


# -- Owner ke Approve/Reject dabane par ---------------------------------------

@app.on_callback_query(filters.regex("^jreq ") & ~app.bl_users)
async def joinrequest_decision(_, query: types.CallbackQuery):
    try:
        _, action, chat_id, user_id = query.data.split()
        chat_id, user_id = int(chat_id), int(user_id)
    except Exception:
        return await query.answer()

    if query.from_user.id not in config.OWNER_ID:
        return await query.answer("ʏᴇ ʙᴜᴛᴛᴏɴ ꜱɪʀꜰ ᴏᴡɴᴇʀ ᴋᴇ ʟɪʏᴇ ʜᴀɪ.", show_alert=True)

    key = _key(chat_id, user_id)
    entry = _pending.get(key)

    if not entry or entry["handled"]:
        try:
            await query.edit_message_text("⚠️ ʏᴇ ʀᴇǫᴜᴇsᴛ ᴘᴀʜᴀʟᴇ ʜɪ ᴋɪꜱɪ ᴀᴜʀ ᴏᴡɴᴇʀ ɴᴇ ʜᴀɴᴅʟᴇ ᴋᴀʀ ᴅɪ ʜᴀɪ.")
        except Exception:
            pass
        return await query.answer()

    entry["handled"] = True
    decided_by = query.from_user.mention

    if action == "accept":
        try:
            await app.approve_chat_join_request(chat_id, user_id)
        except Exception:
            for owner_id, msg_id in entry["messages"].items():
                try:
                    await app.edit_message_text(
                        owner_id, msg_id,
                        "❌ ʀᴇǫᴜᴇsᴛ ᴀᴄᴄᴇᴘᴛ ɴᴀʜɪ ʜᴏ ᴘᴀᴀʏɪ (ʙᴏᴛ ᴋᴇ ᴘᴀᴀꜱ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ɴᴀʜɪ ʜᴀɪ)."
                    )
                except Exception:
                    pass
            _pending.pop(key, None)
            return await query.answer()

        result_text = f"✅ ʀᴇǫᴜᴇsᴛ ᴀᴄᴄᴇᴘᴛ ᴋᴀʀ ᴅɪ ɢᴀʏɪ ʙʏ {decided_by}"

        # Request confirm hone par user ko confirm message
        await _send_user_msg(
            entry.get("user_chat_id") or user_id,
            _confirm_text(entry["full_name"], entry["chat_title"]),
        )

    else:
        try:
            await app.decline_chat_join_request(chat_id, user_id)
        except Exception:
            pass
        result_text = f"❌ ʀᴇǫᴜᴇsᴛ ʀᴇᴊᴇᴄᴛ ᴋᴀʀ ᴅɪ ɢᴀʏɪ ʙʏ {decided_by}"

    for owner_id, msg_id in entry["messages"].items():
        try:
            await app.edit_message_text(owner_id, msg_id, result_text)
        except Exception:
            pass

    _pending.pop(key, None)
    await query.answer()
    
