FROM python:3.13-slim

WORKDIR /app

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends ffmpeg curl unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://deno.land/install.sh | sh


ENV DENO_INSTALL="/root/.deno"
ENV PATH="${DENO_INSTALL}/bin:${PATH}"

RUN curl -Ls https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

# ---- Required env vars (config.py check() inme se koi bhi missing hone par bot start hi nahi hoga) ----
ENV API_ID=""
ENV API_HASH=""
ENV BOT_TOKEN=""
ENV MONGO_URL=""
ENV LOGGER_ID=""
ENV OWNER_ID=""
ENV SESSION=""

# ---- Optional pyrogram sessions (multi-assistant support) ----
ENV SESSION2=""
ENV SESSION3=""

# ---- Optional, config.py already has sane defaults, override only if needed ----
ENV DURATION_LIMIT=""
ENV QUEUE_LIMIT=""
ENV PLAYLIST_LIMIT=""
ENV STICKER_ID=""
ENV SUPPORT_CHANNEL=""
ENV SUPPORT_CHAT=""
ENV AUTO_LEAVE=""
ENV AUTO_END=""
ENV THUMB_GEN=""
ENV VIDEO_PLAY=""
ENV LANG_CODE=""
ENV COOKIES_URL=""
ENV DEFAULT_THUMB=""
ENV PING_IMG=""
ENV START_IMG=""
ENV START_VIDEO=""

# ---- Optional Turso cache DB pairs (song-byte caching, saves download API quota) ----
ENV TURSO_URL_1=""
ENV TURSO_TOKEN_1=""
ENV TURSO_URL_2=""
ENV TURSO_TOKEN_2=""

CMD ["bash", "start"]
