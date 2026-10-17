import os
from PIL import Image, ImageDraw, ImageFont

GIFS_DIR = os.path.join(os.path.dirname(__file__), "static", "gifs")
os.makedirs(GIFS_DIR, exist_ok=True)

# Fonts
try:
    font_bold_lg = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 18)
    font_bold = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 14)
    font_regular = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
    font_sm = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    font_mono = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 13)
    font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 16)
except Exception:
    font_bold_lg = font_bold = font_regular = font_sm = font_mono = font_title = ImageFont.load_default()

W, H = 560, 380

def draw_phone_base(draw, title, plat_color, step_num, step_total=4):
    # Background
    draw.rectangle([0, 0, W, H], fill=(11, 15, 25))
    
    # Outer device bezel
    draw.rounded_rectangle([30, 15, W - 30, H - 20], radius=24, outline=(45, 55, 75), width=3, fill=(15, 23, 42))
    
    # Dynamic island
    draw.rounded_rectangle([W//2 - 45, 22, W//2 + 45, 36], radius=7, fill=(0, 0, 0))
    draw.ellipse([W//2 + 25, 26, W//2 + 31, 32], fill=(16, 185, 129))
    
    # Status bar
    draw.text((50, 22), "9:41", font=font_sm, fill=(200, 210, 225))
    draw.text((W - 110, 22), "5G  100%", font=font_sm, fill=(200, 210, 225))
    
    # App Header
    draw.rectangle([33, 44, W - 33, 82], fill=plat_color)
    draw.text((50, 52), title, font=font_title, fill=(255, 255, 255))
    
    # Step indicator pill
    step_str = f"STEP {step_num}/{step_total}"
    draw.rounded_rectangle([W - 145, 52, W - 50, 74], radius=6, fill=(0, 0, 0, 100), outline=(255, 255, 255), width=1)
    draw.text((W - 138, 55), step_str, font=font_sm, fill=(255, 255, 255))
    
    # Home bar
    draw.rounded_rectangle([W//2 - 40, H - 28, W//2 + 40, H - 24], radius=2, fill=(100, 116, 139))


def create_instagram_gif():
    frames = []
    PLAT_COLOR = (193, 53, 132) # Instagram magenta
    
    # Step 1: Profile & Hamburger Menu
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Instagram", PLAT_COLOR, 1)
        
        # Profile view
        d.ellipse([55, 100, 115, 160], outline=(225, 48, 108), width=3, fill=(30, 41, 59))
        d.text((75, 120), "USER", font=font_bold, fill=(255, 255, 255))
        d.text((135, 105), "@user_account", font=font_bold, fill=(255, 255, 255))
        d.text((135, 125), "Posts: 24  •  Followers: 380  •  Following: 195", font=font_sm, fill=(148, 163, 184))
        
        # Menu Button highlighted
        d.rounded_rectangle([W - 110, 98, W - 55, 135], radius=10, outline=(99, 102, 241), width=2, fill=(49, 46, 129))
        d.text((W - 95, 107), "MENU", font=font_bold, fill=(255, 255, 255))
        
        # Post grid placeholders
        for r in range(2):
            for c in range(3):
                x = 55 + c * 150
                y = 175 + r * 65
                d.rounded_rectangle([x, y, x + 140, y + 55], radius=8, fill=(30, 41, 59), outline=(51, 65, 85))
        
        # Bottom caption banner
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "1. Open Profile -> Tap Menu (three lines in top right)", font=font_bold, fill=(241, 245, 249))
        frames.append(img)
        
    # Step 2: Settings / Your Activity
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Instagram • Settings", PLAT_COLOR, 2)
        
        d.text((55, 95), "Settings and Activity", font=font_bold_lg, fill=(255, 255, 255))
        
        # Options list
        opts = [
            ("⚙️ Settings & Privacy", False),
            ("📊 Your Activity / Accounts Center", True),
            ("📦 Archive", False),
            ("🔒 Security & Permissions", False)
        ]
        for i, (txt, active) in enumerate(opts):
            y = 125 + i * 42
            if active:
                d.rounded_rectangle([55, y, W - 55, y + 36], radius=10, fill=(49, 46, 129), outline=(129, 140, 248), width=2)
                d.text((70, y + 8), txt, font=font_bold, fill=(255, 255, 255))
                d.rounded_rectangle([W - 140, y + 6, W - 68, y + 30], radius=6, fill=(79, 70, 229))
                d.text((W - 130, y + 9), "SELECT", font=font_sm, fill=(255, 255, 255))
            else:
                d.rounded_rectangle([55, y, W - 55, y + 36], radius=10, fill=(30, 41, 59), outline=(51, 65, 85))
                d.text((70, y + 8), txt, font=font_regular, fill=(203, 213, 225))
                
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "2. Choose 'Your Activity' or 'Accounts Center'", font=font_bold, fill=(241, 245, 249))
        frames.append(img)

    # Step 3: Select Subscriptions & Format JSON
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Meta • Download Info", PLAT_COLOR, 3)
        
        d.text((55, 95), "Download Your Information", font=font_bold, fill=(255, 255, 255))
        
        # Checkbox item
        d.rounded_rectangle([55, 120, W - 55, 160], radius=10, fill=(22, 101, 52, 120), outline=(34, 197, 94), width=2)
        d.text((70, 130), "[X] Followers and following", font=font_bold, fill=(240, 253, 244))
        d.text((W - 120, 132), "CHECKED", font=font_sm, fill=(74, 222, 128))
        
        # Format selector
        d.text((55, 175), "Format:", font=font_bold, fill=(255, 255, 255))
        d.rounded_rectangle([55, 195, 180, 230], radius=8, fill=(30, 41, 59), outline=(71, 85, 105))
        d.text((75, 203), "( ) HTML", font=font_regular, fill=(148, 163, 184))
        
        d.rounded_rectangle([200, 195, 360, 230], radius=8, fill=(67, 56, 202), outline=(129, 140, 248), width=2)
        d.text((215, 203), "(*) JSON (Machine)", font=font_bold, fill=(255, 255, 255))
        
        # Submit button
        d.rounded_rectangle([55, 245, W - 55, 282], radius=10, fill=(37, 99, 235), outline=(96, 165, 250))
        d.text((W//2 - 60, 254), "Request Download", font=font_bold, fill=(255, 255, 255))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "3. Check 'Followers and following' and format: JSON", font=font_bold, fill=(241, 245, 249))
        frames.append(img)

    # Step 4: Notification & File Delivery
    for _ in range(4):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Instagram • Ready", PLAT_COLOR, 4)
        
        # Push notification box
        d.rounded_rectangle([55, 95, W - 55, 145], radius=12, fill=(30, 41, 59), outline=(225, 48, 108), width=2)
        d.text((70, 102), "INSTAGRAM  •  Just now", font=font_sm, fill=(244, 114, 182))
        d.text((70, 120), "Your information is ready to download (ZIP / JSON)", font=font_bold, fill=(255, 255, 255))
        
        # File Delivery Card
        d.rounded_rectangle([55, 160, W - 55, 275], radius=14, fill=(15, 23, 42), outline=(34, 197, 94), width=2)
        d.text((70, 175), "FILE EXPORT COMPLETED", font=font_bold, fill=(74, 222, 128))
        
        # File badge
        d.rounded_rectangle([70, 200, W - 70, 235], radius=8, fill=(2, 6, 23), outline=(100, 116, 139))
        d.text((85, 208), "[FILE] following.json", font=font_mono, fill=(56, 189, 248))
        d.text((W - 150, 210), "Ready to scan", font=font_sm, fill=(148, 163, 184))
        
        d.text((70, 245), "Sent to your Email / Available in Instagram Downloads", font=font_sm, fill=(203, 213, 225))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "4. Download following.json -> Send to bot for safety check!", font=font_bold, fill=(74, 222, 128))
        frames.append(img)
        
    frames[0].save(os.path.join(GIFS_DIR, "instagram.gif"), save_all=True, append_images=frames[1:], duration=1400, loop=0, optimize=True)
    print("Saved instagram.gif")


def create_telegram_gif():
    frames = []
    PLAT_COLOR = (34, 158, 217) # Telegram Blue
    
    # Step 1: Open Menu in Telegram Desktop
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Telegram Desktop", PLAT_COLOR, 1)
        
        # Header with Menu
        d.rounded_rectangle([55, 95, 125, 125], radius=6, fill=(30, 58, 138), outline=(96, 165, 250), width=2)
        d.text((68, 102), "MENU", font=font_bold, fill=(255, 255, 255))
        
        # Chat items
        chats = ["InstaSafe UZ Bot [Verified]", "News Channel", "Family Chat", "IT Community"]
        for i, c in enumerate(chats):
            y = 135 + i * 36
            d.rounded_rectangle([55, y, W - 55, y + 30], radius=8, fill=(30, 41, 59), outline=(51, 65, 85))
            d.text((70, y + 6), f"• {c}", font=font_regular, fill=(226, 232, 240))
            
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "1. Open Telegram Desktop -> Click Menu in top left", font=font_bold, fill=(241, 245, 249))
        frames.append(img)
        
    # Step 2: Settings -> Advanced
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Telegram • Settings", PLAT_COLOR, 2)
        
        opts = [
            ("Notifications and Sounds", False),
            ("Privacy and Security", False),
            ("Advanced Settings (Export data)", True),
            ("Language & Chat Settings", False)
        ]
        for i, (txt, active) in enumerate(opts):
            y = 105 + i * 40
            if active:
                d.rounded_rectangle([55, y, W - 55, y + 34], radius=8, fill=(14, 116, 144), outline=(56, 189, 248), width=2)
                d.text((70, y + 7), f"> {txt}", font=font_bold, fill=(255, 255, 255))
            else:
                d.rounded_rectangle([55, y, W - 55, y + 34], radius=8, fill=(30, 41, 59), outline=(51, 65, 85))
                d.text((70, y + 7), f"  {txt}", font=font_regular, fill=(148, 163, 184))
                
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "2. Settings -> Choose 'Advanced' -> 'Export Telegram Data'", font=font_bold, fill=(241, 245, 249))
        frames.append(img)

    # Step 3: Export Modal -> Channel Subscriptions + JSON
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Export Telegram Data", PLAT_COLOR, 3)
        
        # Checkboxes
        d.rounded_rectangle([55, 105, W - 55, 140], radius=8, fill=(30, 41, 59), outline=(71, 85, 105))
        d.text((70, 115), "[ ] Private chats / Media (Uncheck all)", font=font_sm, fill=(148, 163, 184))
        
        d.rounded_rectangle([55, 150, W - 55, 188], radius=8, fill=(12, 74, 110), outline=(14, 165, 233), width=2)
        d.text((70, 160), "[X] Channel subscriptions (Channels list)", font=font_bold, fill=(240, 249, 255))
        d.text((W - 130, 162), "REQUIRED", font=font_sm, fill=(56, 189, 248))
        
        # Format
        d.text((55, 202), "Format:  (*) Machine-readable JSON", font=font_bold, fill=(255, 255, 255))
        
        # Export Button
        d.rounded_rectangle([W - 170, 230, W - 55, 268], radius=8, fill=(2, 132, 199), outline=(56, 189, 248))
        d.text((W - 140, 240), "EXPORT", font=font_bold, fill=(255, 255, 255))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "3. Check ONLY 'Channel subscriptions' & choose JSON format", font=font_bold, fill=(241, 245, 249))
        frames.append(img)

    # Step 4: Export Saved to Downloads -> result.json
    for _ in range(4):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Export Finished", PLAT_COLOR, 4)
        
        d.rounded_rectangle([55, 105, W - 55, 240], radius=14, fill=(15, 23, 42), outline=(34, 197, 94), width=2)
        d.text((70, 120), "TELEGRAM EXPORT COMPLETED", font=font_bold, fill=(74, 222, 128))
        
        d.rounded_rectangle([70, 150, W - 70, 190], radius=8, fill=(2, 6, 23), outline=(56, 189, 248))
        d.text((85, 160), "[FILE] result.json", font=font_mono, fill=(56, 189, 248))
        
        d.text((70, 205), "Location: Downloads / Telegram Desktop / result.json", font=font_sm, fill=(203, 213, 225))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "4. Upload result.json to InstaSafe bot to scan all channels!", font=font_bold, fill=(74, 222, 128))
        frames.append(img)
        
    frames[0].save(os.path.join(GIFS_DIR, "telegram.gif"), save_all=True, append_images=frames[1:], duration=1400, loop=0, optimize=True)
    print("Saved telegram.gif")


def create_youtube_gif():
    frames = []
    PLAT_COLOR = (239, 68, 68) # YouTube Red
    
    # Step 1: takeout.google.com
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Google Takeout", PLAT_COLOR, 1)
        
        d.text((55, 100), "Google Takeout (takeout.google.com)", font=font_bold, fill=(255, 255, 255))
        d.text((55, 125), "Export a copy of your Google content", font=font_sm, fill=(148, 163, 184))
        
        # Deselect all button highlighted
        d.rounded_rectangle([55, 160, 220, 200], radius=8, fill=(185, 28, 28), outline=(252, 165, 165), width=2)
        d.text((70, 172), "Deselect all [CLICK]", font=font_bold, fill=(255, 255, 255))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "1. Go to takeout.google.com -> Click 'Deselect all'", font=font_bold, fill=(241, 245, 249))
        frames.append(img)
        
    # Step 2: Select YouTube only
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Google Takeout • Select", PLAT_COLOR, 2)
        
        d.rounded_rectangle([55, 110, W - 55, 175], radius=10, fill=(69, 10, 10), outline=(239, 68, 68), width=2)
        d.text((70, 125), "[X] YouTube and YouTube Music", font=font_bold_lg, fill=(255, 255, 255))
        d.text((70, 148), "History, playlists, subscriptions, comments", font=font_sm, fill=(252, 165, 165))
        d.text((W - 130, 130), "CHECKED", font=font_bold, fill=(239, 68, 68))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "2. Scroll down and check ONLY 'YouTube and YouTube Music'", font=font_bold, fill=(241, 245, 249))
        frames.append(img)

    # Step 3: Subscriptions CSV only
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "YouTube Data Options", PLAT_COLOR, 3)
        
        d.text((55, 100), "Select data to include:", font=font_bold, fill=(255, 255, 255))
        d.rounded_rectangle([55, 125, W - 55, 165], radius=8, fill=(15, 23, 42), outline=(34, 197, 94), width=2)
        d.text((70, 135), "[X] Subscriptions (CSV format)", font=font_bold, fill=(74, 222, 128))
        
        d.rounded_rectangle([55, 180, 240, 220], radius=8, fill=(37, 99, 235), outline=(96, 165, 250))
        d.text((70, 192), "Create export ->", font=font_bold, fill=(255, 255, 255))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "3. Leave only 'Subscriptions' checked -> Click 'Create export'", font=font_bold, fill=(241, 245, 249))
        frames.append(img)

    # Step 4: Gmail Archive -> subscriptions.csv
    for _ in range(4):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Google Takeout • Ready", PLAT_COLOR, 4)
        
        d.rounded_rectangle([55, 100, W - 55, 145], radius=10, fill=(30, 41, 59), outline=(239, 68, 68), width=2)
        d.text((70, 108), "GMAIL NOTIFICATION", font=font_sm, fill=(248, 113, 113))
        d.text((70, 124), "Your Google data archive is ready to download!", font=font_bold, fill=(255, 255, 255))
        
        d.rounded_rectangle([55, 160, W - 55, 250], radius=12, fill=(15, 23, 42), outline=(34, 197, 94), width=2)
        d.text((70, 175), "YOUTUBE DATA FILE", font=font_bold, fill=(74, 222, 128))
        d.rounded_rectangle([70, 198, W - 70, 230], radius=6, fill=(2, 6, 23), outline=(100, 116, 139))
        d.text((85, 206), "[FILE] subscriptions.csv", font=font_mono, fill=(56, 189, 248))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "4. Download ZIP from email -> Send subscriptions.csv to bot!", font=font_bold, fill=(74, 222, 128))
        frames.append(img)
        
    frames[0].save(os.path.join(GIFS_DIR, "youtube.gif"), save_all=True, append_images=frames[1:], duration=1400, loop=0, optimize=True)
    print("Saved youtube.gif")


def create_facebook_gif():
    frames = []
    PLAT_COLOR = (24, 119, 242) # Facebook Blue
    
    # Step 1: Facebook Menu
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Facebook", PLAT_COLOR, 1)
        
        d.text((55, 100), "Menu (three lines icon)", font=font_bold, fill=(255, 255, 255))
        
        d.rounded_rectangle([W - 120, 95, W - 55, 130], radius=8, fill=(30, 64, 175), outline=(96, 165, 250), width=2)
        d.text((W - 105, 105), "MENU", font=font_bold, fill=(255, 255, 255))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "1. Open Facebook app -> Tap Menu tab", font=font_bold, fill=(241, 245, 249))
        frames.append(img)
        
    # Step 2: Accounts Center -> Download Your Information
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Meta Accounts Center", PLAT_COLOR, 2)
        
        d.rounded_rectangle([55, 110, W - 55, 155], radius=10, fill=(30, 58, 138), outline=(96, 165, 250), width=2)
        d.text((70, 125), "Your Information and Permissions", font=font_bold, fill=(255, 255, 255))
        d.text((W - 130, 128), "SELECT", font=font_sm, fill=(147, 197, 253))
        
        d.rounded_rectangle([55, 170, W - 55, 215], radius=10, fill=(23, 37, 84), outline=(59, 130, 246))
        d.text((70, 185), "Download Your Information -> Request a download", font=font_bold, fill=(255, 255, 255))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "2. Choose 'Your Information' -> 'Download Your Information'", font=font_bold, fill=(241, 245, 249))
        frames.append(img)

    # Step 3: Friends and followers + JSON
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Download Options", PLAT_COLOR, 3)
        
        d.rounded_rectangle([55, 105, W - 55, 145], radius=8, fill=(22, 101, 52), outline=(34, 197, 94), width=2)
        d.text((70, 118), "[X] Friends and followers", font=font_bold, fill=(240, 253, 244))
        
        d.text((55, 165), "Format:  (*) JSON format (Required)", font=font_bold, fill=(255, 255, 255))
        
        d.rounded_rectangle([55, 200, 230, 238], radius=8, fill=(37, 99, 235), outline=(96, 165, 250))
        d.text((70, 212), "Submit Request", font=font_bold, fill=(255, 255, 255))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "3. Select 'Friends and followers' and choose JSON format", font=font_bold, fill=(241, 245, 249))
        frames.append(img)

    # Step 4: Notification -> friends_and_followers.json
    for _ in range(4):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "Facebook • Ready", PLAT_COLOR, 4)
        
        d.rounded_rectangle([55, 105, W - 55, 235], radius=12, fill=(15, 23, 42), outline=(34, 197, 94), width=2)
        d.text((70, 120), "FACEBOOK ARCHIVE READY", font=font_bold, fill=(74, 222, 128))
        d.rounded_rectangle([70, 150, W - 70, 185], radius=8, fill=(2, 6, 23), outline=(59, 130, 246))
        d.text((85, 160), "[FILE] friends_and_followers.json", font=font_mono, fill=(56, 189, 248))
        d.text((70, 200), "Sent to your Email / Download link ready", font=font_sm, fill=(203, 213, 225))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "4. Download file -> Send to bot for official safety check!", font=font_bold, fill=(74, 222, 128))
        frames.append(img)
        
    frames[0].save(os.path.join(GIFS_DIR, "facebook.gif"), save_all=True, append_images=frames[1:], duration=1400, loop=0, optimize=True)
    print("Saved facebook.gif")


def create_tiktok_gif():
    frames = []
    PLAT_COLOR = (254, 44, 85) # TikTok Red/Pink
    
    # Step 1: TikTok Profile Menu
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "TikTok", PLAT_COLOR, 1)
        
        d.text((55, 100), "@user_account", font=font_bold_lg, fill=(255, 255, 255))
        d.text((55, 125), "Following: 120  •  Followers: 1.4K  •  Likes: 18K", font=font_sm, fill=(148, 163, 184))
        
        d.rounded_rectangle([W - 120, 95, W - 55, 130], radius=8, fill=(136, 19, 55), outline=(251, 113, 133), width=2)
        d.text((W - 105, 105), "MENU", font=font_bold, fill=(255, 255, 255))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "1. Open Profile -> Tap Menu (three lines in top right)", font=font_bold, fill=(241, 245, 249))
        frames.append(img)
        
    # Step 2: Settings and Privacy -> Account
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "TikTok Settings", PLAT_COLOR, 2)
        
        d.rounded_rectangle([55, 110, W - 55, 155], radius=10, fill=(76, 5, 25), outline=(254, 44, 85), width=2)
        d.text((70, 125), "Settings and privacy -> Account", font=font_bold, fill=(255, 255, 255))
        
        d.rounded_rectangle([55, 170, W - 55, 215], radius=10, fill=(30, 41, 59), outline=(71, 85, 105))
        d.text((70, 185), "Download your data", font=font_bold, fill=(34, 211, 238))
        d.text((W - 130, 188), "SELECT", font=font_sm, fill=(34, 211, 238))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "2. Choose 'Settings and privacy' -> 'Download your data'", font=font_bold, fill=(241, 245, 249))
        frames.append(img)

    # Step 3: Format JSON
    for _ in range(3):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "TikTok • Download Data", PLAT_COLOR, 3)
        
        d.text((55, 100), "Select file format:", font=font_bold, fill=(255, 255, 255))
        
        d.rounded_rectangle([55, 130, 180, 170], radius=8, fill=(30, 41, 59), outline=(71, 85, 105))
        d.text((75, 142), "( ) TXT", font=font_regular, fill=(148, 163, 184))
        
        d.rounded_rectangle([200, 130, 390, 170], radius=8, fill=(136, 19, 55), outline=(34, 211, 238), width=2)
        d.text((215, 142), "(*) JSON (Machine-readable)", font=font_bold, fill=(255, 255, 255))
        
        d.rounded_rectangle([55, 195, 230, 235], radius=8, fill=(254, 44, 85), outline=(251, 113, 133))
        d.text((75, 207), "Request Data", font=font_bold, fill=(255, 255, 255))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "3. Select 'JSON - Machine-readable' -> Tap Request Data", font=font_bold, fill=(241, 245, 249))
        frames.append(img)

    # Step 4: Download tab -> user_data.json
    for _ in range(4):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        draw_phone_base(d, "TikTok • Ready", PLAT_COLOR, 4)
        
        d.rounded_rectangle([55, 105, W - 55, 235], radius=12, fill=(15, 23, 42), outline=(34, 197, 94), width=2)
        d.text((70, 120), "TIKTOK DATA READY IN 'DOWNLOAD DATA' TAB", font=font_bold, fill=(74, 222, 128))
        d.rounded_rectangle([70, 150, W - 70, 185], radius=8, fill=(2, 6, 23), outline=(254, 44, 85))
        d.text((85, 160), "[FILE] user_data.json", font=font_mono, fill=(34, 211, 238))
        d.text((70, 200), "Available in TikTok app -> Settings -> Download data tab", font=font_sm, fill=(203, 213, 225))
        
        d.rectangle([33, H - 75, W - 33, H - 32], fill=(15, 23, 42))
        d.text((50, H - 65), "4. Download user_data.json -> Send to bot for safety check!", font=font_bold, fill=(74, 222, 128))
        frames.append(img)
        
    frames[0].save(os.path.join(GIFS_DIR, "tiktok.gif"), save_all=True, append_images=frames[1:], duration=1400, loop=0, optimize=True)
    print("Saved tiktok.gif")


if __name__ == "__main__":
    create_instagram_gif()
    create_telegram_gif()
    create_youtube_gif()
    create_facebook_gif()
    create_tiktok_gif()
    print("ALL 5 GIFS GENERATED SUCCESSFULLY!")
