import sys
sys.stdout.reconfigure(encoding='utf-8')
from rapidocr_onnxruntime import RapidOCR
from PIL import Image, ImageDraw
import io, time
from checker import BannedChecker

img = Image.new('RGB', (1080, 1920), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

channels = [
    'Kun.uz - Rasmiy kanal',
    'Daryo - Yangiliklar',
    "A'ashiqul jannah",
    'Gazeta.uz',
    'Abdulloh Zufar',
    'Toshkent shahar IIBB',
    'Sekulyarizm Islom mezonida',
    'UzAuto Motors'
]

y = 150
for ch in channels:
    draw.text((60, y), ch, fill=(0, 0, 0))
    y += 180

buf = io.BytesIO()
img.save(buf, format='PNG')

engine = RapidOCR()
t0 = time.time()
res, _ = engine(buf.getvalue())
t1 = time.time()

print(f"OCR completed in {t1 - t0:.2f}s, detected {len(res) if res else 0} lines")

checker = BannedChecker()
banned_found = []

for box, text, score in (res or []):
    m = checker.check_single_account(text, platform='telegram')
    if m:
        banned = m['banned_item']
        banned_found.append((text, banned))
        print(f"  [🚨 BANNED] '{text}' -> #{banned['id']}: {banned['title']}")
    else:
        print(f"  [✅ SAFE] '{text}'")

print(f"\nResult: Found {len(banned_found)} banned channels out of {len(channels)} on screenshot!")
