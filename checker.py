import json
import os
import re
from typing import List, Dict, Optional, Any, Tuple

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

class BannedChecker:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.platforms = ["telegram", "instagram", "youtube", "facebook", "tiktok", "odnoklassniki"]
        
        self.platform_items: Dict[str, List[Dict[str, Any]]] = {}
        self.platform_user_map: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.platform_title_map: Dict[str, Dict[str, Dict[str, Any]]] = {}
        
        self.all_items: List[Dict[str, Any]] = []
        self.all_user_map: Dict[str, Dict[str, Any]] = {}
        self.all_title_map: Dict[str, Dict[str, Any]] = {}
        self._ocr_engine = None
        
        self.load_all_registries()

    def load_all_registries(self):
        self.all_items.clear()
        self.all_user_map.clear()
        self.all_title_map.clear()

        for plat in self.platforms:
            fpath = os.path.join(self.data_dir, f"banned_{plat}.json")
            items = []
            if os.path.exists(fpath):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        items = json.load(f)
                except Exception as e:
                    print(f"Error loading {fpath}: {e}")
            
            self.platform_items[plat] = items
            self.platform_user_map[plat] = {}
            self.platform_title_map[plat] = {}

            for it in items:
                it["platform"] = plat
                self.all_items.append(it)

                # Index by username / handle
                raw_u = it.get("username", "")
                if raw_u:
                    norm_u = self.normalize_username(raw_u)
                    if norm_u:
                        self.platform_user_map[plat][norm_u] = it
                        if norm_u not in self.all_user_map:
                            self.all_user_map[norm_u] = it

                # Index by title / channel name
                raw_t = it.get("title", "") or it.get("original", "")
                if raw_t:
                    norm_t = self.normalize_title(raw_t)
                    if norm_t and len(norm_t) >= 3:
                        self.platform_title_map[plat][norm_t] = it
                        if norm_t not in self.all_title_map:
                            self.all_title_map[norm_t] = it

    @staticmethod
    def normalize_username(username: str) -> str:
        if not username:
            return ""
        u = username.lower().strip()
        # Remove URLs and prefixes
        u = re.sub(r"^https?://(?:www\.)?(?:t\.me|telegram\.me|instagram\.com|youtube\.com/@?|facebook\.com|tiktok\.com/@?)/", "", u)
        u = re.sub(r"^[sS]?/+", "", u)
        u = re.sub(r"^@+", "", u)
        u = re.sub(r"[/?#].*$", "", u)
        u = re.sub(r"\s+", "", u)
        return u

    @staticmethod
    def normalize_title(title: str) -> str:
        if not title:
            return ""
        t = title.lower().strip()
        # Strip prefixes and non-alphanumeric chars
        t = re.sub(r"[\s_.\-\'\"`«»“”/\\|()\[\]{}#@!?:;]+", "", t)
        return t

    def extract_channel_handle(self, text: str) -> Tuple[str, str]:
        """
        Extracts (username, title_candidate) from user input (link, @handle, or raw text)
        """
        clean = text.strip()
        
        # Check URLs
        tg_m = re.search(r"(?:t\.me|telegram\.me)/([a-zA-Z0-9_+]+)", clean, re.I)
        if tg_m:
            return tg_m.group(1).lower(), clean

        yt_m = re.search(r"(?:youtube\.com|youtu\.be)/@?([a-zA-Z0-9_.-]+)", clean, re.I)
        if yt_m:
            return yt_m.group(1).lower(), clean

        ig_m = re.search(r"instagram\.com/([a-zA-Z0-9_.]+)", clean, re.I)
        if ig_m:
            return ig_m.group(1).lower(), clean

        fb_m = re.search(r"facebook\.com/([a-zA-Z0-9_.]+)", clean, re.I)
        if fb_m:
            return fb_m.group(1).lower(), clean

        tt_m = re.search(r"tiktok\.com/@?([a-zA-Z0-9_.]+)", clean, re.I)
        if tt_m:
            return tt_m.group(1).lower(), clean

        # Starts with @
        if clean.startswith("@"):
            uname = self.normalize_username(clean)
            return uname, clean

        # Single word without spaces
        if " " not in clean and len(clean) <= 35:
            uname = self.normalize_username(clean)
            return uname, clean

        return "", clean

    def check_single_account(self, identifier: str, title: str = "", platform: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Checks a single username/link/title against the banned registry.
        """
        norm_u, raw_t = self.extract_channel_handle(identifier)
        if not norm_u and identifier:
            norm_u = self.normalize_username(identifier)
        
        norm_title = self.normalize_title(title or raw_t or identifier)

        # 1. Search in target platform if specified
        if platform and platform in self.platform_user_map:
            u_map = self.platform_user_map[platform]
            t_map = self.platform_title_map[platform]

            if norm_u and norm_u in u_map:
                item = u_map[norm_u]
                return {
                    "matched_type": "username",
                    "matched_field": item.get("username", norm_u),
                    "platform": platform,
                    "banned_item": item,
                    "reason": f"Прямое совпадение никнейма в реестре ({platform.upper()} №{item['id']}: @{item.get('username')})"
                }

            if norm_title and norm_title in t_map:
                item = t_map[norm_title]
                return {
                    "matched_type": "title",
                    "matched_field": item.get("title", norm_title),
                    "platform": platform,
                    "banned_item": item,
                    "reason": f"Совпадение названия с решением суда ({platform.upper()} №{item['id']}: {item.get('title')})"
                }

        # 2. Search globally across all platforms
        if norm_u and norm_u in self.all_user_map:
            item = self.all_user_map[norm_u]
            p = item.get("platform", "unknown")
            return {
                "matched_type": "username",
                "matched_field": item.get("username", norm_u),
                "platform": p,
                "banned_item": item,
                "reason": f"Совпадение никнейма в реестре ({p.upper()} №{item['id']}: @{item.get('username')})"
            }

        if norm_title and norm_title in self.all_title_map:
            item = self.all_title_map[norm_title]
            p = item.get("platform", "unknown")
            return {
                "matched_type": "title",
                "matched_field": item.get("title", norm_title),
                "platform": p,
                "banned_item": item,
                "reason": f"Совпадение названия с реестром ({p.upper()} №{item['id']}: {item.get('title')})"
            }

        # Substring title matching for strong titles (length >= 6)
        if norm_title and len(norm_title) >= 6:
            search_title_map = self.platform_title_map.get(platform, {}) if platform else self.all_title_map
            for t_key, item in search_title_map.items():
                if len(t_key) >= 6:
                    if norm_title == t_key or (len(norm_title) >= 8 and (norm_title in t_key or t_key in norm_title)):
                        p = item.get("platform", platform or "unknown")
                        return {
                            "matched_type": "title_contain",
                            "matched_field": item.get("title", t_key),
                            "platform": p,
                            "banned_item": item,
                            "reason": f"Совпадение с запрещенным источником ({p.upper()} №{item['id']}: {item.get('title')})"
                        }

        return None

    def analyze_following_list(self, followings: List[Dict[str, str]], platform: str = "instagram") -> Dict[str, Any]:
        """
        Analyzes a list of accounts/channels (for Instagram following.json or general list).
        followings: [ {"username": "...", "full_name": "..."}, ... ]
        """
        banned_found = []
        clean_count = 0

        for f in followings:
            uname = f.get("username", "")
            fname = f.get("full_name", "") or f.get("name", "")
            match = self.check_single_account(uname, fname, platform=platform)
            if match:
                banned_found.append({
                    "username": uname,
                    "full_name": fname,
                    "platform": match.get("platform", platform),
                    "details": match
                })
            else:
                clean_count += 1

        is_safe = len(banned_found) == 0

        return {
            "is_safe": is_safe,
            "platform": platform,
            "total_checked": len(followings),
            "banned_count": len(banned_found),
            "clean_count": clean_count,
            "banned_found": banned_found
        }

    def analyze_telegram_export(self, content_str: str) -> Dict[str, Any]:
        """
        Parses Telegram Desktop export (result.json) or text list of channels.
        """
        channels_to_check = []

        try:
            data = json.loads(content_str)
            # Telegram Desktop result.json structure:
            # { "chats": { "list": [ { "id": 123, "name": "...", "type": "public_channel", ... } ] } }
            chats_list = []
            if isinstance(data, dict):
                if "chats" in data and isinstance(data["chats"], dict) and "list" in data["chats"]:
                    chats_list = data["chats"]["list"]
                elif "chats" in data and isinstance(data["chats"], list):
                    chats_list = data["chats"]
                elif "list" in data and isinstance(data["list"], list):
                    chats_list = data["list"]

            for chat in chats_list:
                c_type = chat.get("type", "")
                name = chat.get("name", "")
                # We check channels and supergroups
                if "channel" in c_type or "supergroup" in c_type or not c_type:
                    uname = ""
                    # Sometimes username or link is present in export
                    if "username" in chat:
                        uname = chat["username"]
                    elif "link" in chat:
                        uname = chat["link"]
                    channels_to_check.append({
                        "username": uname,
                        "full_name": name
                    })

        except Exception:
            # If not JSON, parse line by line (plain text list of channels or links)
            for line in content_str.splitlines():
                line = line.strip()
                if line:
                    u, t = self.extract_channel_handle(line)
                    channels_to_check.append({
                        "username": u or line,
                        "full_name": t or line
                    })

        if not channels_to_check:
            # Fallback line-by-line
            for line in content_str.splitlines():
                line = line.strip()
                if line:
                    channels_to_check.append({"username": line, "full_name": line})

        return self.analyze_following_list(channels_to_check, platform="telegram")

    def analyze_youtube_export(self, content_str: str) -> Dict[str, Any]:
        """
        Parses YouTube subscriptions CSV (Google Takeout subscriptions.csv) or channel list.
        """
        channels_to_check = []
        lines = content_str.splitlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Google Takeout CSV format: Channel Id,Channel Url,Channel Title
            parts = [p.strip().replace("\"", "") for p in line.split(",")]
            if len(parts) >= 3 and ("Channel Id" in parts[0] or "Channel Url" in parts[1]):
                continue  # skip header
            if len(parts) >= 3:
                c_url = parts[1]
                c_title = parts[2]
                channels_to_check.append({"username": c_url, "full_name": c_title})
            elif len(parts) == 2:
                channels_to_check.append({"username": parts[0], "full_name": parts[1]})
            else:
                channels_to_check.append({"username": line, "full_name": line})

        return self.analyze_following_list(channels_to_check, platform="youtube")

    def get_ocr_engine(self):
        if self._ocr_engine is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                self._ocr_engine = RapidOCR()
                self._ocr_error = None
            except Exception as e:
                import traceback
                self._ocr_error = str(e)
                self._ocr_engine = None
        return self._ocr_engine

    def analyze_screenshot(self, image_bytes: bytes, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs high-speed OCR on a mobile screenshot of Telegram / Instagram / YouTube / Facebook channels.
        Matches extracted lines against the 1,562-entry banned registry.
        """
        import time
        t0 = time.time()
        engine = self.get_ocr_engine()
        if engine is None:
            err_msg = getattr(self, "_ocr_error", "No module")
            return {
                "is_safe": True,
                "total_checked": 0,
                "detected_channels": [],
                "banned_count": 0,
                "clean_count": 0,
                "banned_found": [],
                "ocr_time_seconds": 0,
                "platform": platform or "screenshot",
                "ocr_error": err_msg,
                "message": f"Skrinshot OCR xatosi: {err_msg}"
            }
        ocr_result, _ = engine(image_bytes)
        t1 = time.time()

        if not ocr_result:
            return {
                "is_safe": True,
                "total_checked": 0,
                "detected_channels": [],
                "banned_count": 0,
                "clean_count": 0,
                "banned_found": [],
                "ocr_time_seconds": round(t1 - t0, 2),
                "platform": platform or "screenshot"
            }

        # Filter noise patterns (UI bars, times, network icons, common tabs)
        noise_pattern = re.compile(
            r"^(?:\d{1,2}:\d{2}(?::\d{2})?|\d+[\%kKmMbB]?|[0-9\s.,]+|"
            r"lte|4g|5g|wi-?fi|volte|edit|chats|search|qidiruv|sozlamalar|kanallar|guruhlar|"
            r"поиск|чаты|каналы|группы|настройки|изменить|все|подписки|подписчики|подписаться|"
            r"following|followers|subscribed|subscribe|home|shorts|library|reels|explore|"
            r"kecha|bugun|вчера|сегодня|yesterday|today)$",
            re.IGNORECASE
        )

        detected_lines = []
        banned_found = []
        seen_matched_ids = set()

        for item in ocr_result:
            if len(item) < 2:
                continue
            text = str(item[1]).strip()
            score = float(item[2]) if len(item) > 2 else 1.0

            if len(text) < 2 or score < 0.35:
                continue

            # Strip leading/trailing bullet or count badges
            cleaned_text = re.sub(r"^[\d\s•\-#@/]+", "", text).strip()
            if not cleaned_text or len(cleaned_text) < 2:
                continue

            if noise_pattern.match(cleaned_text.lower()):
                continue

            detected_lines.append(text)

            # Check single account
            match = self.check_single_account(cleaned_text, platform=platform)
            if not match and cleaned_text != text:
                match = self.check_single_account(text, platform=platform)

            if match:
                b_item = match["banned_item"]
                b_id = b_item.get("id")
                if b_id not in seen_matched_ids:
                    seen_matched_ids.add(b_id)
                    banned_found.append({
                        "username": match.get("matched_field") or cleaned_text,
                        "full_name": text,
                        "detected_text": text,
                        "confidence": round(score, 2),
                        "platform": match.get("platform", platform or "unknown"),
                        "details": match
                    })

        # Check pairs of adjacent lines (for wrapped titles)
        if len(detected_lines) >= 2:
            for i in range(len(detected_lines) - 1):
                combined = f"{detected_lines[i]} {detected_lines[i+1]}"
                if len(combined) <= 60:
                    match = self.check_single_account(combined, platform=platform)
                    if match:
                        b_item = match["banned_item"]
                        b_id = b_item.get("id")
                        if b_id not in seen_matched_ids:
                            seen_matched_ids.add(b_id)
                            banned_found.append({
                                "username": match.get("matched_field") or combined,
                                "full_name": combined,
                                "detected_text": combined,
                                "confidence": 0.9,
                                "platform": match.get("platform", platform or "unknown"),
                                "details": match
                            })

        total_detected = len(detected_lines)
        banned_count = len(banned_found)
        clean_count = max(0, total_detected - banned_count)
        is_safe = banned_count == 0

        return {
            "is_safe": is_safe,
            "platform": platform or "screenshot",
            "total_checked": total_detected,
            "detected_channels": detected_lines[:30],
            "banned_count": banned_count,
            "clean_count": clean_count,
            "banned_found": banned_found,
            "ocr_time_seconds": round(t1 - t0, 2)
        }

    def search_registry(self, query: str, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search in the banned registry.
        """
        q = query.lower().strip()
        if not q:
            if platform and platform in self.platform_items:
                return self.platform_items[platform]
            return self.all_items

        items_pool = self.platform_items.get(platform, self.all_items) if platform else self.all_items
        results = []
        for it in items_pool:
            t = (it.get("title") or "").lower()
            u = (it.get("username") or "").lower()
            orig = (it.get("original") or "").lower()
            if q in t or q in u or q in orig:
                results.append(it)
        return results

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_banned": len(self.all_items),
            "by_platform": {
                plat: len(items) for plat, items in self.platform_items.items()
            }
        }
