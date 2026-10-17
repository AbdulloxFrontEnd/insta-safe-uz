@echo off
title InstaSafe UZ - Public HTTPS Tunnel
cd /d "%~dp0"
echo ==================================================
echo    InstaSafe UZ - Public HTTPS Tunnel
echo ==================================================
echo Generating free HTTPS link for Telegram Mini App...
echo.
echo Look for the link ending in: .trycloudflare.com
echo Copy that HTTPS link and set it in @BotFather!
echo.
cloudflared tunnel --url http://127.0.0.1:8000
pause
