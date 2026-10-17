import json
import re
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OCR_FILE = os.path.join(DATA_DIR, "full_court_list_ocr.json")

with open(OCR_FILE, "r", encoding="utf-8") as f:
    pages = json.load(f)

def clean_entry(text: str) -> str:
    t = text.strip().replace("\"", "").replace("“", "").replace("”", "").replace("«", "").replace("»", "")
    t = re.sub(r"\s+", " ", t)
    return t

def extract_handles(text: str):
    username = ""
    # t.me link (supports t.me, t/me, telegram.me, etc.)
    m_tg = re.search(r"(?:t[\./]me|telegram\.(?:me|org|com))/([a-zA-Z0-9_+]+)", text, re.I)
    if m_tg:
        username = m_tg.group(1)
    
    # @username
    if not username:
        m_at = re.search(r"@([a-zA-Z0-9_.]+)", text)
        if m_at:
            username = m_at.group(1)

    # youtube channel / handle
    if not username:
        m_yt = re.search(r"(?:youtube\.com|youtu\.be)/(?:c/|channel/|user/|@)?([a-zA-Z0-9_.-]+)", text, re.I)
        if m_yt:
            username = m_yt.group(1)

    # instagram link
    if not username:
        m_ig = re.search(r"instagram\.com/(?:_u/)?([a-zA-Z0-9_.]+)", text, re.I)
        if m_ig:
            username = m_ig.group(1)

    # tiktok link
    if not username:
        m_tt = re.search(r"tiktok\.com/@?([a-zA-Z0-9_.]+)", text, re.I)
        if m_tt:
            username = m_tt.group(1)

    # facebook link
    if not username:
        m_fb = re.search(r"facebook\.com/([a-zA-Z0-9_.]+)", text, re.I)
        if m_fb:
            username = m_fb.group(1)

    clean_u = username.strip().replace("@", "").lower()
    return clean_u

def parse_lines_to_dict(lines, min_id=1, max_id=9999):
    result = {}
    for i, line in enumerate(lines):
        l_str = line.strip()
        matches = list(re.finditer(r"(\d+)\.\s*", l_str))
        if len(matches) > 1:
            for idx in range(len(matches)):
                num = int(matches[idx].group(1))
                s_idx = matches[idx].end()
                e_idx = matches[idx+1].start() if idx+1 < len(matches) else len(l_str)
                text = l_str[s_idx:e_idx].strip()
                if min_id <= num <= max_id:
                    result[num] = text
            continue

        m = re.match(r"^(\d+)\.\s*(.*)", l_str)
        if m:
            num = int(m.group(1))
            val = m.group(2).strip()
            if not val and i+1 < len(lines):
                next_l = lines[i+1].strip()
                if not re.match(r"^\d+\.", next_l):
                    val = next_l
            if min_id <= num <= max_id:
                result[num] = val
    return result

# 1. FACEBOOK (Pages 1 & 2 before 'Telegram')
fb_p1 = parse_lines_to_dict(pages["page_1"], 1, 136)

p2_lines = pages["page_2"]
p2_fb_lines = []
for l in p2_lines:
    if "telegram" in l.lower() or "mecce" in l.lower():
        break
    p2_fb_lines.append(l)
fb_p2 = parse_lines_to_dict(p2_fb_lines, 137, 249)

fb_raw = {**fb_p1, **fb_p2}
fb_items = []
for nid in range(1, 250):
    val = clean_entry(fb_raw.get(nid, ""))
    handle = extract_handles(val)
    fb_items.append({
        "id": nid,
        "platform": "facebook",
        "title": val,
        "username": handle,
        "original": val
    })

# 2. TELEGRAM (Pages 2-7)
p2_tg_lines = []
tg_found = False
for l in p2_lines:
    if "telegram" in l.lower() or "mecce" in l.lower():
        tg_found = True
        continue
    if tg_found:
        p2_tg_lines.append(l)

tg_raw = {}
tg_raw.update(parse_lines_to_dict(p2_tg_lines, 1, 44))
for p in [3, 4, 5, 6]:
    tg_raw.update(parse_lines_to_dict(pages[f"page_{p}"], 1, 790))

p7_tg_lines = []
for l in pages["page_7"]:
    if "instagram" in l.lower() or "tapmo" in l.lower() and "insta" in l.lower():
        break
    p7_tg_lines.append(l)
tg_raw.update(parse_lines_to_dict(p7_tg_lines, 701, 790))

# Manual corrections
if 372 not in tg_raw or not tg_raw[372]:
    tg_raw[372] = "Sekulyarizm Islom mezonida"
if 700 not in tg_raw or not tg_raw[700]:
    tg_raw[700] = "ЧОЙХОНА №1 ÇOYXONA №1"

tg_items = []
for nid in range(1, 791):
    val = clean_entry(tg_raw.get(nid, ""))
    handle = extract_handles(val)
    tg_items.append({
        "id": nid,
        "platform": "telegram",
        "title": val,
        "username": handle,
        "original": val
    })

# 3. YOUTUBE (Pages 9 & 10)
p9_yt_lines = []
yt_found = False
for l in pages["page_9"]:
    if "youtube" in l.lower() or "видеохост" in l.lower():
        yt_found = True
        continue
    if yt_found:
        p9_yt_lines.append(l)

yt_p9 = parse_lines_to_dict(p9_yt_lines, 1, 119)

p10_yt_lines = pages["page_10"][:57]
yt_p10 = parse_lines_to_dict(p10_yt_lines, 120, 167)

yt_raw = {**yt_p9, **yt_p10}
if 164 not in yt_raw or not yt_raw[164]:
    yt_raw[164] = "ЖОНЛИ СУҲБАТ (Mahmud Abdulmomin)(04. 02. 2021) номли аудио ва видео шаклидаги фикр, маъруза ва фатволар"
if 167 not in yt_raw or not yt_raw[167]:
    yt_raw[167] = "Нега раддия берасизлар/// аҳли илмлар бир бирига раддия бериши яхшими? (устоз маҳмуд абдулмўмин) номли аудио ва видео шаклидаги фикр, маъруза ва фатволари"

yt_items = []
for nid in range(1, 168):
    val = clean_entry(yt_raw.get(nid, ""))
    handle = extract_handles(val)
    yt_items.append({
        "id": nid,
        "platform": "youtube",
        "title": val,
        "username": handle,
        "original": val
    })

# 4. ODNOKLASSNIKI (Page 10, lines 57 to 128)
p10_ok_lines = pages["page_10"][57:129]
ok_raw = parse_lines_to_dict(p10_ok_lines, 1, 36)
ok_items = []
for nid in range(1, 37):
    val = clean_entry(ok_raw.get(nid, ""))
    handle = extract_handles(val)
    ok_items.append({
        "id": nid,
        "platform": "odnoklassniki",
        "title": val,
        "username": handle,
        "original": val
    })

# 5. TIKTOK (Page 10, lines 129 to end)
p10_tt_lines = pages["page_10"][129:]
tt_raw = parse_lines_to_dict(p10_tt_lines, 1, 53)
if 52 not in tt_raw or not tt_raw[52]:
    tt_raw[52] = "ام هريرة (tiktok. com/@_tavhld_)"
if 53 not in tt_raw or not tt_raw[53]:
    tt_raw[53] = "مصطف (tiktok. com/@muttaqiyn)"

tt_items = []
for nid in range(1, 54):
    val = clean_entry(tt_raw.get(nid, ""))
    handle = extract_handles(val)
    tt_items.append({
        "id": nid,
        "platform": "tiktok",
        "title": val,
        "username": handle,
        "original": val
    })

# 6. INSTAGRAM (Loaded from validated banned_instagram.json)
with open(os.path.join(DATA_DIR, "banned_instagram.json"), "r", encoding="utf-8") as f:
    ig_items = json.load(f)
for it in ig_items:
    it["platform"] = "instagram"

# Save individual platform files
with open(os.path.join(DATA_DIR, "banned_telegram.json"), "w", encoding="utf-8") as f:
    json.dump(tg_items, f, ensure_ascii=False, indent=2)

with open(os.path.join(DATA_DIR, "banned_youtube.json"), "w", encoding="utf-8") as f:
    json.dump(yt_items, f, ensure_ascii=False, indent=2)

with open(os.path.join(DATA_DIR, "banned_facebook.json"), "w", encoding="utf-8") as f:
    json.dump(fb_items, f, ensure_ascii=False, indent=2)

with open(os.path.join(DATA_DIR, "banned_tiktok.json"), "w", encoding="utf-8") as f:
    json.dump(tt_items, f, ensure_ascii=False, indent=2)

with open(os.path.join(DATA_DIR, "banned_odnoklassniki.json"), "w", encoding="utf-8") as f:
    json.dump(ok_items, f, ensure_ascii=False, indent=2)

# Save combined all platforms
all_registry = {
    "total_count": len(tg_items) + len(ig_items) + len(yt_items) + len(fb_items) + len(tt_items) + len(ok_items),
    "updated_at": "2026-01-10",
    "source": "Ўзбекистон Республикаси Олий суди (Supreme Court of Uzbekistan)",
    "stats": {
        "telegram": len(tg_items),
        "instagram": len(ig_items),
        "youtube": len(yt_items),
        "facebook": len(fb_items),
        "tiktok": len(tt_items),
        "odnoklassniki": len(ok_items)
    },
    "telegram": tg_items,
    "instagram": ig_items,
    "youtube": yt_items,
    "facebook": fb_items,
    "tiktok": tt_items,
    "odnoklassniki": ok_items
}

with open(os.path.join(DATA_DIR, "banned_all.json"), "w", encoding="utf-8") as f:
    json.dump(all_registry, f, ensure_ascii=False, indent=2)

print("Exact Build Complete!")
print(f"Telegram: {len(tg_items)}")
print(f"Instagram: {len(ig_items)}")
print(f"YouTube: {len(yt_items)}")
print(f"Facebook: {len(fb_items)}")
print(f"TikTok: {len(tt_items)}")
print(f"Odnoklassniki: {len(ok_items)}")
print(f"Total Registry Entries: {all_registry['total_count']}")
