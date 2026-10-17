import os
import json
import time
import logging
from typing import List, Dict, Optional, Tuple, Any
from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired,
    UserNotFound,
    PrivateAccount,
    BadPassword,
    TwoFactorRequired,
    ChallengeRequired,
    ClientJSONDecodeError,
    ClientError
)

logger = logging.getLogger(__name__)

SESSION_FILE = os.path.join(os.path.dirname(__file__), "session.json")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "bot_config.json")

class InstagramService:
    def __init__(self):
        self.cl = Client()
        self.cl.delay_range = [2, 4]
        self.is_authenticated = False
        self.current_bot_username = ""
        self.last_error = ""
        self._load_saved_session()

    def _load_saved_session(self):
        """Attempts to load a saved session from session.json"""
        if os.path.exists(SESSION_FILE):
            try:
                self.cl.load_settings(SESSION_FILE)
                if os.path.exists(CONFIG_FILE):
                    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                        self.current_bot_username = cfg.get("bot_username", "")
                self.is_authenticated = True
                logger.info(f"Loaded existing Instagram session for {self.current_bot_username}")
            except Exception as e:
                logger.warning(f"Failed to load session settings: {e}")
                self.is_authenticated = False

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_authenticated": self.is_authenticated,
            "bot_username": self.current_bot_username,
            "has_session_file": os.path.exists(SESSION_FILE),
            "last_error": self.last_error
        }

    def login_bot(self, username: str, password: str, verification_code: Optional[str] = None) -> Tuple[bool, str]:
        """
        Logs into the technical/fake Instagram account.
        Saves session to disk on success.
        """
        try:
            self.last_error = ""
            self.cl = Client()
            self.cl.delay_range = [2, 4]

            if verification_code:
                self.cl.login(username, password, verification_code=verification_code)
            else:
                self.cl.login(username, password)

            self.cl.dump_settings(SESSION_FILE)
            self.current_bot_username = username
            self.is_authenticated = True

            cfg = {}
            if os.path.exists(CONFIG_FILE):
                try:
                    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                except Exception:
                    pass
            cfg["bot_username"] = username
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)

            return True, f"Успешный вход под ботом @{username}"
        except TwoFactorRequired:
            self.last_error = "Требуется код двухфакторной аутентификации (2FA)."
            return False, "2FA_REQUIRED"
        except ChallengeRequired:
            self.last_error = "Instagram запросил подтверждение (Challenge). Проверьте аккаунт в приложении Instagram."
            return False, "CHALLENGE_REQUIRED"
        except BadPassword:
            self.last_error = "Неверный логин или пароль Instagram."
            return False, "Неверный логин или пароль."
        except Exception as e:
            err_msg = str(e)
            if "suspended" in err_msg.lower():
                err_msg = "Аккаунт заблокирован или ограничен Instagram (Suspended). Войдите в него через обычный браузер для разблокировки."
            self.last_error = err_msg
            return False, f"Ошибка авторизации: {err_msg}"

    def get_user_followings(
        self,
        target_username: str,
        max_amount: Optional[int] = None,
        progress_callback: Optional[Any] = None
    ) -> Tuple[Optional[List[Dict[str, str]]], str, int]:
        """
        Fetches the following list for a given target username.
        Checks total following count and paginates until all are fetched.
        Calls progress_callback(current_count, total_count) if provided.
        Returns: (results_list, status_message, total_expected_count)
        """
        if not self.is_authenticated:
            return None, "Технический бот не авторизован. Настройте бота во вкладке 'Настройка бота'.", 0

        clean_user = target_username.strip().replace("@", "")

        try:
            user_id = self.cl.user_id_from_username(clean_user)
        except UserNotFound:
            return None, f"Пользователь @{clean_user} не найден в Instagram.", 0
        except (LoginRequired, ClientJSONDecodeError) as e:
            self.is_authenticated = False
            self.last_error = "Сессия бота устарела или аккаунт бота временно заморожен Instagram."
            return None, "Сессия бота недействительна. Instagram временно заблокировал или запросил подтверждение бота (Suspended). Войдите в бот-аккаунт через браузер или используйте отправку файла.", 0
        except Exception as e:
            err_str = str(e)
            if "suspended" in err_str.lower() or "jsondecodeerror" in err_str.lower():
                self.is_authenticated = False
                return None, "Аккаунт бота временно заблокирован Instagram из-за частых запросов (Suspended). Войдите в бот-аккаунт через браузер или приложение для подтверждения.", 0
            return None, f"Ошибка поиска профиля: {e}", 0

        # Check total followings and privacy
        total_following = 0
        try:
            info = self.cl.user_info_v1(user_id)
            if getattr(info, "is_private", False):
                return None, "PRIVATE_ACCOUNT: Профиль закрыт. Пожалуйста, откройте профиль в настройках Instagram на 1 минуту и повторите проверку.", 0
            total_following = getattr(info, "following_count", 0) or 0
        except PrivateAccount:
            return None, "PRIVATE_ACCOUNT: Профиль закрыт. Пожалуйста, откройте профиль на 1 минуту.", 0
        except Exception as e:
            logger.warning(f"Could not verify info via v1: {e}")

        # If max_amount is None or 0, target the whole following count (or default safety upper bound of 10,000)
        target_limit = max_amount if (max_amount and max_amount > 0) else (total_following if total_following > 0 else 10000)

        # Notify initial discovery
        if progress_callback:
            try:
                progress_callback(0, total_following)
            except Exception:
                pass

        # Safe pagination loop
        results = []
        unique_ids = set()
        max_id = ""
        rank_token = getattr(self.cl, "rank_token", "") or f"{user_id}_{int(time.time())}"

        while True:
            try:
                params = {
                    "count": 40,
                    "rank_token": rank_token,
                    "search_surface": "follow_list_page",
                    "query": "",
                    "enable_groups": "true",
                }
                if max_id:
                    params["max_id"] = max_id

                response = self.cl.private_request(f"friendships/{user_id}/following/", params=params)
                users = response.get("users", [])

                for u in users:
                    pk = str(u.get("pk") or u.get("id"))
                    if pk not in unique_ids:
                        unique_ids.add(pk)
                        results.append({
                            "username": u.get("username", ""),
                            "full_name": u.get("full_name", "")
                        })

                max_id = response.get("next_max_id")

                if progress_callback:
                    try:
                        progress_callback(len(results), total_following or target_limit)
                    except Exception:
                        pass

                if not max_id or len(results) >= target_limit:
                    break

                # Safe polite delay to avoid Instagram anti-spam bans
                time.sleep(2.5)

            except Exception as e:
                logger.warning(f"Fetching stopped at {len(results)} accounts: {e}")
                # If we already have some results, DO NOT FAIL! Return what was fetched!
                if len(results) > 0:
                    break

                err_str = str(e)
                if "suspended" in err_str.lower() or "jsondecodeerror" in err_str.lower():
                    self.is_authenticated = False
                    return None, "Аккаунт бота временно приостановлен Instagram (Suspended). Войдите в него через браузер/приложение для разблокировки, либо используйте проверку файлом JSON.", total_following
                return None, f"Ошибка при получении списка подписок: {e}", total_following

        if not results:
            return None, "Не удалось загрузить подписки профиля (список пуст или ограничен Instagram).", total_following

        return results, "OK", total_following
