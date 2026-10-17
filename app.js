// Global App State
let currentLang = 'uz'; // 'uz' or 'ru'
let currentTab = 'check'; // 'check' or 'registry'
let currentMode = 'screenshot'; // 'screenshot', 'single', or 'file'
let selectedPlatform = 'telegram'; // 'telegram', 'youtube', 'instagram', 'facebook'
let selectedRegistryFilter = 'all';

let currentTelegramUser = null;
let currentTelegramId = null;
let userChecksLeft = 1;
let allBannedItems = [];
let loadingInterval = null;

// Multi-language text dictionary
const I18N = {
  uz: {
    heroTitle: `Kanallaringizni <span class="hero-text-gradient">taqiqlangan ro'yxatga</span> tekshiring`,
    heroSubtitle: "O'zbekiston Respublikasi Oliy sudi tomonidan taqiqlangan 1 560+ ta rasmiy ekstremistik manbalar (Telegram, YouTube, Instagram, Facebook).",
    tabCheck: "Tekshirish",
    tabRegistry: "Reyestr (1560+)",
    modeScreenshot: "Skrinshot (AI)",
    modeSingle: "Kanal / Havola",
    modeFile: "Fayl eksport",
    screenshotCardTitle: "Skrinshot orqali tekshirish",
    screenshotCardDesc: "Obunalaringizni skrinshot qilib tashlang, AI 2 soniyada tekshiradi.",
    screenshotDropText: "Skrinshotni tanlang yoki shu yerga tashlang",
    screenshotTipText: "<b>Eng qulay usul:</b> Telegram yoki Instagram'da kanallaringiz ro'yxatini ochib bitta skrinshot qiling. Bizning AI barcha nomlarni 2 soniyada o'qib, sud qarorlari bilan tekshirib beradi!",
    singleCardTitle: "Kanal yoki sahifani tekshirish",
    singleCheckBtn: "Oliy sud bazasidan tekshirish",
    singleTip: "<b>Maslahat:</b> Telegram botimizda shubhali kanaldan xabarni to'g'ridan-to'g'ri forward qilib ham tekshirishingiz mumkin!",
    placeholderTg: "@kanal_nomi, t.me/havola yoki kanal nomi",
    placeholderYt: "youtube.com/@kanal, kanal nomi yoki havola",
    placeholderIg: "@username, instagram.com/profil yoki nik",
    placeholderFb: "facebook.com/sahifa yoki profil nomi",
    fileCardTitle: "Fayl orqali barcha obunalarni tekshirish",
    fileCardDesc: "Telegram (<code>result.json</code>), YouTube (<code>subscriptions.csv</code>) yoki Instagram (<code>following.json</code>).",
    dropMainText: "Faylni shu yerga tashlang yoki tanlang",
    guideTitle: "Eksport faylini olish bo'yicha qo'llanma:",
    safeTitle: "Barcha obunalar toza va xavfsiz!",
    safeDesc: "Tekshirildi: <b>{count}</b> ta manba. Oliy sudning ekstremistik materiallar reyestrida topilmadi.",
    bannedTitle: "Diqqat! Taqiqlangan manbalar topildi: {count} ta",
    bannedAlertNote: "<b>Qonuniy ogohlantirish:</b> O'zbekiston Respublikasi Jinoyat kodeksining 244-1-moddasiga muvofiq, ekstremistik materiallarni saqlash va tarqatish taqiqlanadi. Ko'rsatilgan kanallardan darhol chiqish (unfollow) tavsiya etiladi.",
    unsubscribeBtn: "Chiqib ketish",
    btnCheckAgain: "Yana tekshirish",
    hideBtn: "Yopish",
    legalCardTitle: "Qonuniy xavfsizlik va JK 244-1-moddasi haqida",
    legalTxt1: "Ekstremistik, terroristik yoki qonun bilan taqiqlangan materiallarni tayyorlash, saqlash yoki tarqatish qonun bo'yicha javobgarlikka sabab bo'ladi.",
    legalTxt2: "Chet elga chiqish yoki qaytishda bojxona va aeroport nazoratida telefoningizdagi shubhali kanallar tekshirilishi mumkin. Oldindan tozalab qo'yish xotirjamlik beradi.",
    legalTxt3: "InstaSafe hech qanday shaxsiy yozishmalaringizni, rasmlaringizni yoki parollaringizni saqlamaydi. Faqat kanal nomlari sud bazasi bilan solishtiriladi.",
    legalTxt4: "Eski egasidan qolgan kanallarni 1 daqiqada aniqlab, nomingizga tushishi mumkin bo'lgan har qanday xavfning oldini oling.",
    shareCardTitle: "Yaqinlaringizni ham xavfdan ogohlantiring",
    shareCardDesc: "Do'stlaringiz va oilangizga bepul tekshiruv havolasini yuboring",
    shareTgBtnText: "Telegram'da do'stlarga ulashish",
    copyLinkBtnText: "Nusxalash"
  },
  ru: {
    heroTitle: `Проверьте каналы и подписки на <span class="hero-text-gradient">запрещенные материалы</span>`,
    heroSubtitle: "Официальный реестр экстремистских материалов Верховного суда РУз (1 560+ источников: Telegram, YouTube, Instagram, Facebook).",
    tabCheck: "Проверка",
    tabRegistry: "Реестр суда (1560+)",
    modeScreenshot: "Скриншот (ИИ)",
    modeSingle: "Канал / Ссылка",
    modeFile: "Файл данных",
    screenshotCardTitle: "Проверка по скриншоту",
    screenshotCardDesc: "Сделайте снимок экрана подписок, ИИ проверит за 2 секунды.",
    screenshotDropText: "Выберите скриншот или перетащите сюда",
    screenshotTipText: "<b>Самый быстрый способ:</b> Откройте список подписок и сделайте скриншот. Наш ИИ за 2 секунды распознает все названия и сверит с судебной базой!",
    singleCardTitle: "Проверка канала или страницы",
    singleCheckBtn: "Проверить по судебной базе",
    singleTip: "<b>Подсказка:</b> В нашем Telegram-боте вы можете просто переслать (forward) сообщение из канала для мгновенной проверки!",
    placeholderTg: "@channel_name, t.me/link или название канала",
    placeholderYt: "youtube.com/@channel, название или ссылка",
    placeholderIg: "@username, ссылка или никнейм",
    placeholderFb: "facebook.com/page или название профиля",
    fileCardTitle: "Массовая проверка всех подписок файлом",
    fileCardDesc: "Telegram (<code>result.json</code>), YouTube (<code>subscriptions.csv</code>) или Instagram (<code>following.json</code>).",
    dropMainText: "Перетащите файл сюда или нажмите для выбора",
    guideTitle: "Инструкция по выгрузке файла:",
    safeTitle: "Все каналы и подписки в безопасности!",
    safeDesc: "Проверено: <b>{count}</b> источников. Ни один не числится в списке экстремистских материалов Верховного суда РУз.",
    bannedTitle: "Внимание! Найдены запрещенные ресурсы: {count}",
    bannedAlertNote: "<b>Юридическая справка:</b> Согласно статье 244-1 УК РУз, хранение и распространение экстремистских материалов запрещено законом. Рекомендуется немедленно отписаться от указанных ресурсов.",
    unsubscribeBtn: "Отписаться",
    btnCheckAgain: "Проверить еще",
    hideBtn: "Закрыть",
    legalCardTitle: "Правовая безопасность и статья 244-1 УК РУз",
    legalTxt1: "Изготовление, хранение или распространение материалов, содержащих угрозу общественной безопасности, влечет уголовную ответственность (ст. 244-1 УК РУз).",
    legalTxt2: "При вылете или въезде в страну на таможенном контроле могут проверить список подписок на экстремистские ресурсы. Заблаговременная проверка исключает любые риски.",
    legalTxt3: "InstaSafe не сохраняет переписки, фото или пароли. Мы сверяем исключительно публичные названия и ссылки с решениями суда.",
    legalTxt4: "Купив телефон с рук, проверьте каналы прежнего владельца за 1 минуту, чтобы обезопасить себя от чужой ответственности.",
    shareCardTitle: "Предупредите своих близких об опасности",
    shareCardDesc: "Отправьте ссылку на бесплатную проверку друзьям и семье",
    shareTgBtnText: "Поделиться в Telegram",
    copyLinkBtnText: "Скопировать ссылку"
  }
};

function toggleLanguage() {
  currentLang = currentLang === 'uz' ? 'ru' : 'uz';
  document.getElementById('langToggleText').textContent = currentLang === 'uz' ? "O'Z" : "RU";
  applyLanguage();
  if (currentTelegramId) {
    fetch(`/api/user/status?telegram_id=${currentTelegramId}&lang=${currentLang}`).catch(() => {});
  }
}

function applyLanguage() {
  const t = I18N[currentLang];
  document.getElementById('heroTitle').innerHTML = t.heroTitle;
  document.getElementById('heroSubtitle').textContent = t.heroSubtitle;
  document.getElementById('tabCheckText').textContent = t.tabCheck;
  document.getElementById('tabRegistryText').textContent = t.tabRegistry;
  document.getElementById('modeBtnScreenshotText').textContent = t.modeScreenshot;
  document.getElementById('modeBtnSingleText').textContent = t.modeSingle;
  document.getElementById('modeBtnFileText').textContent = t.modeFile;
  document.getElementById('screenshotCardTitle').textContent = t.screenshotCardTitle;
  document.getElementById('screenshotCardDesc').textContent = t.screenshotCardDesc;
  document.getElementById('screenshotDropText').textContent = t.screenshotDropText;
  document.getElementById('screenshotTipText').innerHTML = t.screenshotTipText;
  document.getElementById('singleCardTitle').textContent = t.singleCardTitle;
  document.getElementById('singleCheckBtnText').textContent = t.singleCheckBtn;
  document.getElementById('singleTipText').innerHTML = t.singleTip;
  document.getElementById('fileCardTitle').textContent = t.fileCardTitle;
  document.getElementById('fileCardDesc').innerHTML = t.fileCardDesc;
  document.getElementById('dropMainText').textContent = t.dropMainText;
  document.getElementById('guideTitle').textContent = t.guideTitle;

  const lTitle = document.getElementById('legalCardTitle'); if (lTitle) lTitle.textContent = t.legalCardTitle;
  const l1 = document.getElementById('legalTxt1'); if (l1) l1.textContent = t.legalTxt1;
  const l2 = document.getElementById('legalTxt2'); if (l2) l2.textContent = t.legalTxt2;
  const l3 = document.getElementById('legalTxt3'); if (l3) l3.textContent = t.legalTxt3;
  const l4 = document.getElementById('legalTxt4'); if (l4) l4.textContent = t.legalTxt4;
  const sTitle = document.getElementById('shareCardTitle'); if (sTitle) sTitle.textContent = t.shareCardTitle;
  const sDesc = document.getElementById('shareCardDesc'); if (sDesc) sDesc.textContent = t.shareCardDesc;
  const sTg = document.getElementById('shareTgBtnText'); if (sTg) sTg.textContent = t.shareTgBtnText;
  const sCopy = document.getElementById('copyLinkBtnText'); if (sCopy) sCopy.textContent = t.copyLinkBtnText;

  // Drawer menu localization
  const isUz = currentLang === 'uz';
  const setEl = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
  setEl('drawerNavCheckText', isUz ? "Kanallarni tekshirish" : "Проверка каналов");
  setEl('drawerNavCheckDesc', isUz ? "Skrinshot, havola yoki fayl orqali" : "По скриншоту, ссылке или файлу");
  setEl('drawerNavRegistryText', isUz ? "Sud reyestri (1560+)" : "Реестр суда (1560+)");
  setEl('drawerNavRegistryDesc', isUz ? "Taqiqlangan manbalar to'liq ro'yxati" : "Полный список экстремистских ресурсов");
  setEl('drawerNavGuideText', isUz ? "Qanday ishlatiladi? (GIF)" : "Инструкция (GIF)");
  setEl('drawerNavGuideDesc', isUz ? "Ko'rgazmali video-qo'llanma" : "Наглядное видео-руководство");
  setEl('drawerNavLegalText', isUz ? "JK 244-1-moddasi haqida" : "Статья 244-1 УК РУз");
  setEl('drawerNavLegalDesc', isUz ? "Yuridik javobgarlik va ma'lumot" : "Юридическая справка и ответственность");
  setEl('drawerNavPayText', isUz ? "Tekshiruv paketlari" : "Пакеты проверок");
  setEl('drawerNavPayDesc', isUz ? "Click va Payme orqali to'ldirish" : "Пополнение через Click и Payme");
  setEl('drawerThemeTitle', isUz ? "Mavzu va Ko'rinish" : "Тема оформления");
  setEl('themeModeAutoText', isUz ? "Avto" : "Авто");
  setEl('themeModeLightText', isUz ? "Yorug'" : "Светлая");
  setEl('themeModeDarkText', isUz ? "Tungi" : "Темная");
  setEl('drawerShareText', isUz ? "Telegram'da ulashish" : "Поделиться в Telegram");

  updateThemeUI();
  updatePlatformUI();
}

const PLATFORM_ACTION_GUIDES = {
  uz: {
    telegram: {
      name: "Telegram",
      title: "Tanlandi: Telegram",
      subtitle: "Tekshirish uchun qulay usulni tanlang:",
      btnGuide: "📖 Telegram (GIF)",
      badgeClass: "bg-gradient-to-r from-sky-400 to-blue-600 shadow-sky-500/40",
      icon: "send",
      steps: [
        { title: "📸 1. Skrinshot (AI)", desc: "Telegram kanallari ro'yxatini rasmga olib tashlang (2 soniyada tekshiradi)." },
        { title: "🔍 2. Bitta kanal", desc: "@kanal_nomi yoki havola orqali tezkor tekshirish." },
        { title: "📁 3. result.json", desc: "Telegram Desktop'dan eksport qilingan faylni yuklang." }
      ]
    },
    youtube: {
      name: "YouTube",
      title: "Tanlandi: YouTube",
      subtitle: "Tekshirish uchun qulay usulni tanlang:",
      btnGuide: "📖 YouTube (GIF)",
      badgeClass: "bg-gradient-to-r from-red-500 to-rose-600 shadow-red-500/40",
      icon: "play",
      steps: [
        { title: "📸 1. Skrinshot (AI)", desc: "YouTube 'Obunalar' sahifasini rasmga olib yuboring." },
        { title: "🔍 2. Havola orqali", desc: "youtube.com/@kanal havolasini kiriting." },
        { title: "📁 3. CSV fayl", desc: "Google Takeout'dan subscriptions.csv yuklang." }
      ]
    },
    instagram: {
      name: "Instagram",
      title: "Tanlandi: Instagram",
      subtitle: "Tekshirish uchun qulay usulni tanlang:",
      btnGuide: "📖 Instagram (GIF)",
      badgeClass: "bg-gradient-to-r from-amber-500 via-rose-500 to-purple-600 shadow-pink-500/40",
      icon: "instagram",
      steps: [
        { title: "📸 1. Skrinshot (AI)", desc: "'Obunalar' (Following) ro'yxatini rasmga oling." },
        { title: "🔍 2. Profil / Nik", desc: "@username yoki havola orqali tekshirish." },
        { title: "📁 3. following.json", desc: "Meta ma'lumotlaridan yuklangan JSON fayli." }
      ]
    },
    facebook: {
      name: "Facebook",
      title: "Tanlandi: Facebook",
      subtitle: "Tekshirish uchun qulay usulni tanlang:",
      btnGuide: "📖 Facebook (GIF)",
      badgeClass: "bg-gradient-to-r from-blue-600 to-indigo-600 shadow-blue-500/40",
      icon: "facebook",
      steps: [
        { title: "📸 1. Skrinshot (AI)", desc: "Obunalar yoki guruhlar ro'yxatini rasmga oling." },
        { title: "🔍 2. Sahifa / Link", desc: "facebook.com/sahifa havolasini kiriting." },
        { title: "📁 3. Meta eksport", desc: "friends_and_followers.json faylini yuklang." }
      ]
    },
    tiktok: {
      name: "TikTok",
      title: "Tanlandi: TikTok",
      subtitle: "Tekshirish uchun qulay usulni tanlang:",
      btnGuide: "📖 TikTok (GIF)",
      badgeClass: "bg-gradient-to-r from-slate-900 to-slate-950 border border-cyan-400 shadow-cyan-500/40",
      icon: "music",
      steps: [
        { title: "📸 1. Skrinshot (AI)", desc: "TikTok'da 'Obunalar' ro'yxatini skrinshot qiling." },
        { title: "🔍 2. Foydalanuvchi", desc: "@username yoki profil havolasini kiriting." },
        { title: "📁 3. user_data.json", desc: "TikTok sozlamalaridan yuklangan JSON fayl." }
      ]
    }
  },
  ru: {
    telegram: {
      name: "Telegram",
      title: "Выбрано: Telegram",
      subtitle: "Выберите удобный способ проверки:",
      btnGuide: "📖 Telegram (GIF)",
      badgeClass: "bg-gradient-to-r from-sky-400 to-blue-600 shadow-sky-500/40",
      icon: "send",
      steps: [
        { title: "📸 1. Скриншот (ИИ)", desc: "Снимок списка каналов — ИИ распознает и проверит за 2 сек." },
        { title: "🔍 2. Поиск канала", desc: "Введите @юзернейм или ссылку на канал." },
        { title: "📁 3. Выгрузка JSON", desc: "Загрузите result.json из Telegram Desktop." }
      ]
    },
    youtube: {
      name: "YouTube",
      title: "Выбрано: YouTube",
      subtitle: "Выберите удобный способ проверки:",
      btnGuide: "📖 YouTube (GIF)",
      badgeClass: "bg-gradient-to-r from-red-500 to-rose-600 shadow-red-500/40",
      icon: "play",
      steps: [
        { title: "📸 1. Скриншот (ИИ)", desc: "Скриншот вкладки «Подписки» в приложении YouTube." },
        { title: "🔍 2. Ссылка на канал", desc: "Вставьте ссылку вида youtube.com/@..." },
        { title: "📁 3. Google Takeout", desc: "Загрузите файл subscriptions.csv." }
      ]
    },
    instagram: {
      name: "Instagram",
      title: "Выбрано: Instagram",
      subtitle: "Выберите удобный способ проверки:",
      btnGuide: "📖 Instagram (GIF)",
      badgeClass: "bg-gradient-to-r from-amber-500 via-rose-500 to-purple-600 shadow-pink-500/40",
      icon: "instagram",
      steps: [
        { title: "📸 1. Скриншот (ИИ)", desc: "Сделайте снимок списка «Подписки» в вашем профиле." },
        { title: "🔍 2. Поиск профиля", desc: "Введите @username или ссылку на страницу." },
        { title: "📁 3. Meta архив", desc: "Загрузите following.json из архива данных." }
      ]
    },
    facebook: {
      name: "Facebook",
      title: "Выбрано: Facebook",
      subtitle: "Выберите удобный способ проверки:",
      btnGuide: "📖 Facebook (GIF)",
      badgeClass: "bg-gradient-to-r from-blue-600 to-indigo-600 shadow-blue-500/40",
      icon: "facebook",
      steps: [
        { title: "📸 1. Скриншот (ИИ)", desc: "Снимок экрана групп или подписок Facebook." },
        { title: "🔍 2. Ссылка / Страница", desc: "Вставьте ссылку на страницу facebook.com/..." },
        { title: "📁 3. Meta выгрузка", desc: "Загрузите файл friends_and_followers.json." }
      ]
    },
    tiktok: {
      name: "TikTok",
      title: "Выбрано: TikTok",
      subtitle: "Выберите удобный способ проверки:",
      btnGuide: "📖 TikTok (GIF)",
      badgeClass: "bg-gradient-to-r from-slate-900 to-slate-950 border border-cyan-400 shadow-cyan-500/40",
      icon: "music",
      steps: [
        { title: "📸 1. Скриншот (ИИ)", desc: "Сделайте скриншот списка «Подписки» в TikTok." },
        { title: "🔍 2. Поиск аккаунта", desc: "Введите @tiktok_username или ссылку." },
        { title: "📁 3. Данные TikTok", desc: "Загрузите файл user_data.json." }
      ]
    }
  }
};

function handleActionStepClick(stepIndex) {
  try { window.Telegram?.WebApp?.HapticFeedback?.impactOccurred('light'); } catch(e) {}
  if (stepIndex === 0) setCheckMode('screenshot');
  else if (stepIndex === 1) setCheckMode('single');
  else if (stepIndex === 2) setCheckMode('file');
}

function selectPlatform(plat) {
  selectedPlatform = plat;
  try {
    window.Telegram?.WebApp?.HapticFeedback?.selectionChanged();
  } catch(e) {}

  ['telegram', 'youtube', 'instagram', 'facebook', 'tiktok'].forEach(p => {
    const btn = document.getElementById(`platBtn${p.charAt(0).toUpperCase() + p.slice(1)}`);
    if (!btn) return;
    if (p === plat) {
      btn.className = `plat-active-${p} touch-ripple shrink-0 py-2 sm:py-2.5 px-3.5 sm:px-4 rounded-xl font-black text-xs sm:text-sm transition-all duration-200 flex items-center space-x-2 whitespace-nowrap shadow-md`;
      try {
        btn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      } catch (e) {}
    } else {
      btn.className = "plat-inactive touch-ripple shrink-0 py-2 sm:py-2.5 px-3.5 sm:px-4 rounded-xl font-bold text-xs sm:text-sm transition-all duration-200 flex items-center space-x-2 whitespace-nowrap";
    }
  });
  updatePlatformUI();
}

function updatePlatformUI() {
  const t = I18N[currentLang];

  const platNames = {
    telegram: "Telegram",
    youtube: "YouTube",
    instagram: "Instagram",
    facebook: "Facebook",
    tiktok: "TikTok"
  };

  const BRAND_SVGS = {
    telegram: `<svg class="w-4 h-4 shrink-0 fill-current" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.75-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/></svg>`,
    youtube: `<svg class="w-4 h-4 shrink-0 fill-current" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>`,
    instagram: `<svg class="w-4 h-4 shrink-0 fill-current" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>`,
    facebook: `<svg class="w-4 h-4 shrink-0 fill-current" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>`,
    tiktok: `<svg class="w-4 h-4 shrink-0 fill-current" viewBox="0 0 24 24"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.24 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>`
  };

  // Configure badges across panels with authentic brand color & icon
  const BADGE_CONFIG = {
    telegram: {
      classes: "bg-sky-50 text-sky-700 border border-sky-200/80 dark:bg-sky-950/60 dark:text-sky-300 dark:border-sky-800/80 shadow-sky-500/10",
      iconClass: "text-sky-600 dark:text-sky-400"
    },
    youtube: {
      classes: "bg-rose-50 text-rose-700 border border-rose-200/80 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-800/80 shadow-rose-500/10",
      iconClass: "text-red-600 dark:text-rose-400"
    },
    instagram: {
      classes: "bg-pink-50 text-pink-700 border border-pink-200/80 dark:bg-pink-950/60 dark:text-pink-300 dark:border-pink-800/80 shadow-pink-500/10",
      iconClass: "text-pink-600 dark:text-pink-400"
    },
    facebook: {
      classes: "bg-blue-50 text-blue-700 border border-blue-200/80 dark:bg-blue-950/60 dark:text-blue-300 dark:border-blue-800/80 shadow-blue-500/10",
      iconClass: "text-blue-600 dark:text-blue-400"
    },
    tiktok: {
      classes: "bg-slate-100 text-slate-800 border border-slate-300 dark:bg-slate-800 dark:text-cyan-300 dark:border-slate-700 shadow-slate-500/10",
      iconClass: "text-slate-800 dark:text-cyan-400"
    }
  };

  const bCfg = BADGE_CONFIG[selectedPlatform] || BADGE_CONFIG.telegram;
  const prefix = currentLang === 'ru' ? 'Выбрано:' : 'Tanlandi:';
  const platName = platNames[selectedPlatform] || 'Telegram';

  function applyBadge(badgeId, iconId, textId) {
    const b = document.getElementById(badgeId);
    const bi = document.getElementById(iconId);
    const bt = document.getElementById(textId);
    if (b) {
      b.className = `text-[10px] font-extrabold px-2.5 py-1 rounded-full flex items-center space-x-1.5 transition-all duration-200 shadow-sm ${bCfg.classes}`;
    }
    if (bi) {
      bi.className = `w-3.5 h-3.5 flex items-center justify-center shrink-0 ${bCfg.iconClass}`;
      bi.innerHTML = BRAND_SVGS[selectedPlatform] || '';
    }
    if (bt) {
      bt.textContent = `${prefix} ${platName}`;
    } else if (b && !bt) {
      b.textContent = `${prefix} ${platName}`;
    }
  }

  applyBadge('selectedPlatformBadge', 'selectedPlatformBadgeIcon', 'selectedPlatformBadgeText');
  applyBadge('screenshotPlatformBadge', 'screenshotPlatformBadgeIcon', 'screenshotPlatformBadgeText');
  applyBadge('filePlatformBadge', 'filePlatformBadgeIcon', 'filePlatformBadgeText');

  // Input Placeholder per platform
  const input = document.getElementById('singleQueryInput');
  if (input) {
    if (selectedPlatform === 'telegram') input.placeholder = t.placeholderTg;
    else if (selectedPlatform === 'youtube') input.placeholder = t.placeholderYt;
    else if (selectedPlatform === 'instagram') input.placeholder = t.placeholderIg;
    else if (selectedPlatform === 'facebook') input.placeholder = t.placeholderFb;
    else if (selectedPlatform === 'tiktok') input.placeholder = currentLang === 'uz' ? "@tiktok_username yoki tiktok.com/@user" : "@tiktok_username или tiktok.com/@user";
  }

  // Update Dynamic Platform Action Card
  const guide = PLATFORM_ACTION_GUIDES[currentLang]?.[selectedPlatform] || PLATFORM_ACTION_GUIDES.ru.telegram;
  const pBadge = document.getElementById('platActionIconBadge');
  const pTitle = document.getElementById('platActionTitle');
  const pSubtitle = document.getElementById('platActionSubtitle');
  const pBtnGuide = document.getElementById('platActionGuideBtn');

  if (pTitle) pTitle.textContent = guide.title;
  if (pSubtitle) pSubtitle.textContent = guide.subtitle;
  if (pBtnGuide) pBtnGuide.innerHTML = `<span>${guide.btnGuide}</span>`;
  if (pBadge) {
    pBadge.className = `w-8 h-8 rounded-xl flex items-center justify-center text-white shadow-md text-xs font-black ${guide.badgeClass} shrink-0 transition-transform duration-200`;
    pBadge.innerHTML = BRAND_SVGS[selectedPlatform] || `<i data-lucide="${guide.icon}" class="w-4 h-4"></i>`;
  }
  const pStepsBox = document.getElementById('platActionSteps');
  if (pStepsBox) {
    pStepsBox.classList.remove('panel-animate');
    void pStepsBox.offsetWidth;
    pStepsBox.classList.add('panel-animate');
    pStepsBox.innerHTML = guide.steps.map((st, i) => `
      <div onclick="handleActionStepClick(${i})" class="cursor-pointer p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200/90 dark:border-slate-700/80 hover:border-indigo-400 dark:hover:border-indigo-500 hover:shadow-sm transition-all duration-150 touch-ripple flex flex-col justify-between space-y-1">
        <div class="flex items-center space-x-1.5 font-extrabold text-slate-800 dark:text-slate-100 text-[11px] sm:text-xs">
          <span>${st.title}</span>
        </div>
        <p class="text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400 leading-snug">${st.desc}</p>
      </div>
    `).join('');
  }

  // Dynamic Quick Samples in Single Check
  const samplesBox = document.getElementById('singleQuickSamples');
  if (samplesBox) {
    const isUz = currentLang === 'uz';
    const SAMPLES = {
      telegram: [
        { q: "Abdulloh Zufar", label: "🚨 Abdulloh Zufar (taqiqlangan)" },
        { q: "Kun.uz", label: "✅ Kun.uz (xavfsiz)" },
        { q: "A'ashiqul jannah", label: "🚨 A'ashiqul jannah" }
      ],
      youtube: [
        { q: "Abdulloh Zufar", label: "🚨 Abdulloh Zufar (YouTube)" },
        { q: "Azon TV", label: "✅ Azon TV (xavfsiz / официальный)" },
        { q: "Tavhid va Jihod", label: "🚨 Tavhid va Jihod" }
      ],
      instagram: [
        { q: "abdullohzufar", label: "🚨 @abdullohzufar" },
        { q: "islomuz", label: "✅ @islomuz (xavfsiz)" },
        { q: "sodiqsamarqandiy", label: "🚨 Sodiq Samarqandiy" }
      ],
      facebook: [
        { q: "Abdulloh Zufar", label: "🚨 Abdulloh Zufar" },
        { q: "Musulmonlar idorasi", label: "✅ Musulmonlar idorasi" },
        { q: "Hizb ut-Tahrir", label: "🚨 Hizb ut-Tahrir" }
      ],
      tiktok: [
        { q: "abdullohzufar", label: "🚨 @abdullohzufar" },
        { q: "ibratli_videolar", label: "✅ @ibratli_videolar" },
        { q: "tavhid_darsi", label: "🚨 @tavhid_darsi" }
      ]
    };
    const sList = SAMPLES[selectedPlatform] || SAMPLES.telegram;
    const label = isUz ? "Tezkor sinov:" : "Быстрый тест:";
    samplesBox.innerHTML = `
      <span class="text-slate-500 font-medium shrink-0">${label}</span>
      ${sList.map(s => `
        <button type="button" onclick="runQuickSample('${s.q.replace(/'/g, "\\'")}', '${selectedPlatform}')" class="shrink-0 whitespace-nowrap px-2.5 py-1 rounded-xl ${s.label.includes('✅') ? 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800' : 'bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-800'} font-semibold transition flex items-center space-x-1 touch-ripple">
          <span>${s.label}</span>
        </button>
      `).join('')}
    `;
  }

  // Dynamic Screenshot Description
  const scDesc = document.getElementById('screenshotCardDesc');
  if (scDesc) {
    const isUz = currentLang === 'uz';
    const SC_DESCS = {
      telegram: isUz ? "Telegram kanallari ro'yxatini skrinshot qiling, AI 2 soniyada tekshiradi." : "Сделайте скриншот списка каналов Telegram, ИИ проверит за 2 секунды.",
      youtube: isUz ? "YouTube 'Obunalar' ro'yxatini skrinshot qiling, AI 2 soniyada tekshiradi." : "Сделайте скриншот списка подписок YouTube, ИИ проверит за 2 секунды.",
      instagram: isUz ? "Instagram 'Obunalar' (Following) ro'yxatini skrinshot qiling, AI 2 soniyada tekshiradi." : "Сделайте скриншот списка подписок в Instagram, ИИ проверит за 2 секунды.",
      facebook: isUz ? "Facebook do'stlar/guruhlar ro'yxatini skrinshot qiling, AI 2 soniyada tekshiradi." : "Сделайте скриншот групп или подписок Facebook, ИИ проверит за 2 секунды.",
      tiktok: isUz ? "TikTok 'Obunalar' ro'yxatini skrinshot qiling, AI 2 soniyada tekshiradi." : "Сделайте скриншот подписок в TikTok, ИИ проверит за 2 секунды."
    };
    scDesc.textContent = SC_DESCS[selectedPlatform] || t.screenshotCardDesc;
  }

  // Platform specific file card texts and quick guide bullets
  const fTitle = document.getElementById('fileCardTitle');
  const fDesc = document.getElementById('fileCardDesc');
  const gList = document.getElementById('guideList');

  if (selectedPlatform === 'telegram') {
    if (fTitle) fTitle.textContent = currentLang === 'uz' ? "Telegram kanallar ro'yxati (result.json)" : "Список каналов Telegram (result.json)";
    if (fDesc) fDesc.innerHTML = currentLang === 'uz' ? "Telegram Desktop'dan olingan <code>result.json</code> fayli." : "Файл <code>result.json</code> из Telegram Desktop.";
    if (gList) gList.innerHTML = currentLang === 'uz'
      ? `<p>• <b>Telegram Desktop (Kompyuter):</b> Sozlamalar ➔ Qo'shimcha ➔ Export Telegram data (faqat «Channels list», JSON).</p><p>• <b>💡 Telefon uchun eng osoni:</b> Kanallar ro'yxatini skrinshot qilib rasm yuboring!</p>`
      : `<p>• <b>Telegram Desktop (ПК):</b> Настройки ➔ Продвинутые настройки ➔ Экспорт данных Telegram (только «Список каналов», JSON).</p><p>• <b>💡 На телефоне проще всего:</b> Сделайте скриншот списка каналов и отправьте фото!</p>`;
  } else if (selectedPlatform === 'instagram') {
    if (fTitle) fTitle.textContent = currentLang === 'uz' ? "Instagram obunalari (following.json)" : "Подписки Instagram (following.json)";
    if (fDesc) fDesc.innerHTML = currentLang === 'uz' ? "Hisoblar markazidan (Meta) yuklangan <code>following.json</code> fayli." : "Файл <code>following.json</code> из Центра аккаунтов Instagram.";
    if (gList) gList.innerHTML = currentLang === 'uz'
      ? `<p>• <b>Instagram ilovasi (Telefon):</b> Profil ➔ ☰ Menyu ➔ Hisoblar markazi ➔ Ma'lumotlarni yuklab olish (JSON).</p><p>• <b>💡 Yana ham oson:</b> Obunalar sahifasini skrinshot qilib rasm yuboring!</p>`
      : `<p>• <b>Instagram (на телефоне):</b> Профиль ➔ ☰ Меню ➔ Центр аккаунтов ➔ Скачать информацию (JSON).</p><p>• <b>💡 Еще проще:</b> Сделайте скриншот списка подписок и пришлите фото!</p>`;
  } else if (selectedPlatform === 'youtube') {
    if (fTitle) fTitle.textContent = currentLang === 'uz' ? "YouTube obunalari (subscriptions.csv)" : "Подписки YouTube (subscriptions.csv)";
    if (fDesc) fDesc.innerHTML = currentLang === 'uz' ? "Google Takeout orqali olingan <code>subscriptions.csv</code> fayli." : "Файл <code>subscriptions.csv</code> из Google Takeout.";
    if (gList) gList.innerHTML = currentLang === 'uz'
      ? `<p>• <b>takeout.google.com:</b> Faqat «YouTube» ➔ Faqat «Obunalar» (CSV) ni tanlang.</p><p>• <b>💡 Yana ham oson:</b> YouTube «Obunalar» sahifasini skrinshot qilib botga tashlang!</p>`
      : `<p>• <b>takeout.google.com:</b> Только «YouTube» ➔ Только «Подписки» (CSV).</p><p>• <b>💡 Еще быстрее:</b> Отправьте скриншот страницы подписок YouTube в бот!</p>`;
  } else if (selectedPlatform === 'facebook') {
    if (fTitle) fTitle.textContent = currentLang === 'uz' ? "Facebook do'stlar va obunalar (JSON)" : "Подписки Facebook (JSON)";
    if (fDesc) fDesc.innerHTML = currentLang === 'uz' ? "Facebook Sozlamalaridan yuklangan JSON fayli." : "Файл JSON из настроек конфиденциальности Facebook.";
    if (gList) gList.innerHTML = currentLang === 'uz'
      ? `<p>• <b>Facebook ilovasi:</b> Sozlamalar ➔ Ma'lumotlarni yuklab olish ➔ «Do'stlar va obunalar» (JSON).</p>`
      : `<p>• <b>Facebook на телефоне:</b> Настройки ➔ Скачать информацию ➔ «Друзья и подписки» (JSON).</p>`;
  } else if (selectedPlatform === 'tiktok') {
    if (fTitle) fTitle.textContent = currentLang === 'uz' ? "TikTok ma'lumotlari (user_data.json)" : "Данные TikTok (user_data.json)";
    if (fDesc) fDesc.innerHTML = currentLang === 'uz' ? "TikTok Sozlamalaridan yuklangan <code>user_data.json</code> fayli." : "Файл <code>user_data.json</code> из настроек TikTok.";
    if (gList) gList.innerHTML = currentLang === 'uz'
      ? `<p>• <b>TikTok ilovasi:</b> Profil ➔ ☰ Menyu ➔ Sozlamalar ➔ Hisob ➔ Ma'lumotlarni yuklab olish (JSON).</p><p>• <b>💡 Eng tezkor:</b> Obunalaringizni skrinshot qilib rasm yuboring!</p>`
      : `<p>• <b>TikTok на телефоне:</b> Профиль ➔ ☰ Меню ➔ Настройки ➔ Скачать данные (JSON).</p><p>• <b>💡 Быстрее всего:</b> Сделайте скриншот списка подписок и отправьте фото!</p>`;
  }

  lucide.createIcons();
}

function setCheckMode(mode) {
  currentMode = mode;
  try {
    window.Telegram?.WebApp?.HapticFeedback?.impactOccurred('light');
  } catch(e) {}

  const pScreenshot = document.getElementById('panelScreenshot');
  const pSingle = document.getElementById('panelSingle');
  const pFile = document.getElementById('panelFile');
  
  const bScreenshot = document.getElementById('modeBtnScreenshot');
  const bSingle = document.getElementById('modeBtnSingle');
  const bFile = document.getElementById('modeBtnFile');

  [pScreenshot, pSingle, pFile].forEach(p => {
    if (p) {
      p.classList.add('hidden');
      p.classList.remove('panel-animate');
    }
  });

  const inactiveModeClass = "flex-1 py-2 sm:py-2.5 rounded-xl font-bold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center justify-center space-x-1.5 transition-all duration-200 touch-ripple border border-transparent";
  const activeModeClass = "flex-1 py-2 sm:py-2.5 rounded-xl font-black bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-md shadow-indigo-500/10 flex items-center justify-center space-x-1.5 transition-all duration-200 touch-ripple border border-indigo-200/80 dark:border-indigo-500/40 ring-1 ring-indigo-500/20";

  bScreenshot.className = inactiveModeClass;
  bSingle.className = inactiveModeClass;
  bFile.className = inactiveModeClass;

  let activePanel = null;
  if (mode === 'screenshot') {
    activePanel = pScreenshot;
    bScreenshot.className = activeModeClass;
  } else if (mode === 'single') {
    activePanel = pSingle;
    bSingle.className = activeModeClass;
  } else {
    activePanel = pFile;
    bFile.className = activeModeClass;
  }

  if (activePanel) {
    activePanel.classList.remove('hidden');
    void activePanel.offsetWidth;
    activePanel.classList.add('panel-animate');
  }
  lucide.createIcons();
}

function handleSplashScreen() {
  const splash = document.getElementById('appSplashScreen');
  const bar = document.getElementById('splashProgressBar');
  if (!splash) return;

  let progress = 10;
  if (bar) bar.style.width = '10%';

  const interval = setInterval(() => {
    progress += Math.floor(Math.random() * 14) + 12;
    if (progress >= 95) {
      progress = 98;
      clearInterval(interval);
    }
    if (bar) bar.style.width = `${progress}%`;
  }, 180);

  setTimeout(() => {
    clearInterval(interval);
    if (bar) bar.style.width = '100%';

    setTimeout(() => {
      splash.style.opacity = '0';
      splash.style.transform = 'scale(1.04)';
      splash.style.pointerEvents = 'none';
      setTimeout(() => {
        splash.classList.add('hidden');
      }, 600);
    }, 200);
  }, 1400);
}

// Automatic & System-Aware Theme Management
let currentThemeMode = 'auto'; // 'auto', 'dark', 'light'

function getSystemTheme() {
  const tgScheme = window.Telegram?.WebApp?.colorScheme;
  if (tgScheme === 'dark' || tgScheme === 'light') {
    return tgScheme;
  }
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

function resolveTheme() {
  const mode = localStorage.getItem('instasafe_theme_mode') || 'auto';
  currentThemeMode = mode;
  if (mode === 'dark') return true;
  if (mode === 'light') return false;
  return getSystemTheme() === 'dark';
}

function applyResolvedTheme(isDark) {
  if (isDark) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  try {
    window.Telegram?.WebApp?.setHeaderColor(isDark ? '#0f172a' : '#f1f4f9');
    window.Telegram?.WebApp?.setBackgroundColor(isDark ? '#0b0f19' : '#f1f4f9');
  } catch (e) {}
  updateThemeUI(isDark);
}

function initTheme() {
  const saved = localStorage.getItem('instasafe_theme_mode');
  if (!saved) {
    const oldTheme = localStorage.getItem('instasafe_theme');
    if (oldTheme === 'dark' || oldTheme === 'light') {
      localStorage.setItem('instasafe_theme_mode', oldTheme);
      currentThemeMode = oldTheme;
    } else {
      localStorage.setItem('instasafe_theme_mode', 'auto');
      currentThemeMode = 'auto';
    }
  } else {
    currentThemeMode = saved;
  }

  applyResolvedTheme(resolveTheme());

  // Listen to OS / Browser media query changes in real time
  if (window.matchMedia) {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const listener = () => {
      const mode = localStorage.getItem('instasafe_theme_mode') || 'auto';
      if (mode === 'auto') {
        applyResolvedTheme(resolveTheme());
      }
    };
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', listener);
    } else if (mediaQuery.addListener) {
      mediaQuery.addListener(listener);
    }
  }

  // Listen to Telegram WebApp theme change in real time
  if (window.Telegram?.WebApp?.onEvent) {
    window.Telegram.WebApp.onEvent('themeChanged', () => {
      const mode = localStorage.getItem('instasafe_theme_mode') || 'auto';
      if (mode === 'auto') {
        applyResolvedTheme(resolveTheme());
      }
    });
  }
}

function setThemeMode(mode) {
  currentThemeMode = mode;
  localStorage.setItem('instasafe_theme_mode', mode);
  localStorage.removeItem('instasafe_theme');
  applyResolvedTheme(resolveTheme());
  try { window.Telegram?.WebApp?.HapticFeedback?.selectionChanged(); } catch (e) {}
}

function quickToggleTheme() {
  const mode = localStorage.getItem('instasafe_theme_mode') || 'auto';
  const isCurrentlyDark = document.documentElement.classList.contains('dark');
  try { window.Telegram?.WebApp?.HapticFeedback?.impactOccurred('light'); } catch (e) {}

  if (mode === 'auto') {
    setThemeMode(isCurrentlyDark ? 'light' : 'dark');
  } else if (mode === 'dark') {
    setThemeMode('light');
  } else {
    setThemeMode('auto');
  }
}

function toggleDarkMode() {
  quickToggleTheme();
}

function updateThemeUI(isDark) {
  if (isDark === undefined) {
    isDark = document.documentElement.classList.contains('dark');
  }
  const mode = currentThemeMode || localStorage.getItem('instasafe_theme_mode') || 'auto';
  const isUz = currentLang === 'uz';

  // 1. Header quick button icon
  const icon = document.getElementById('themeIcon');
  if (icon) {
    if (mode === 'auto') {
      icon.setAttribute('data-lucide', 'sun-moon');
      icon.className = isDark ? 'w-4 h-4 text-indigo-400' : 'w-4 h-4 text-indigo-600';
    } else if (mode === 'dark') {
      icon.setAttribute('data-lucide', 'moon');
      icon.className = 'w-4 h-4 text-amber-400';
    } else {
      icon.setAttribute('data-lucide', 'sun');
      icon.className = 'w-4 h-4 text-amber-500';
    }
  }

  // 2. Drawer segmented buttons UI
  const activeClass = "py-1.5 px-2 rounded-lg transition-all flex items-center justify-center space-x-1 bg-white dark:bg-indigo-600 text-indigo-700 dark:text-white shadow-sm font-black";
  const inactiveClass = "py-1.5 px-2 rounded-lg transition-all flex items-center justify-center space-x-1 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white font-bold";

  ['auto', 'light', 'dark'].forEach(m => {
    const btn = document.getElementById(`themeBtn_${m}`);
    if (btn) {
      btn.className = (m === mode) ? activeClass : inactiveClass;
    }
  });

  // 3. Drawer current theme badge and description
  const badge = document.getElementById('drawerCurrentThemeBadge');
  if (badge) {
    if (mode === 'auto') {
      badge.innerHTML = `<span class="inline-flex items-center gap-1"><i data-lucide="sun-moon" class="w-3 h-3"></i> ${isUz ? `Avto (${isDark ? "Tungi" : "Yorug'"})` : `Авто (${isDark ? "Темная" : "Светлая"})`}</span>`;
      badge.className = "text-[10px] font-black px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800";
    } else if (mode === 'dark') {
      badge.innerHTML = `<span class="inline-flex items-center gap-1"><i data-lucide="moon" class="w-3 h-3"></i> ${isUz ? "Tungi" : "Темная"}</span>`;
      badge.className = "text-[10px] font-black px-2 py-0.5 rounded-full bg-slate-800 text-amber-400 border border-slate-700";
    } else {
      badge.innerHTML = `<span class="inline-flex items-center gap-1"><i data-lucide="sun" class="w-3 h-3"></i> ${isUz ? "Yorug'" : "Светлая"}</span>`;
      badge.className = "text-[10px] font-black px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200";
    }
  }

  const desc = document.getElementById('drawerThemeDesc');
  if (desc) {
    if (mode === 'auto') {
      desc.textContent = isUz ? "Tizim sozlamasiga moslashadi (Avto)" : "Синхронизировано с системой устройства";
    } else if (mode === 'dark') {
      desc.textContent = isUz ? "Doimiy qorong'u tungi rejim" : "Всегда темная тема";
    } else {
      desc.textContent = isUz ? "Doimiy yorug' kunduzgi rejim" : "Всегда светлая тема";
    }
  }

  lucide.createIcons();
}

function updateThemeIcon(isDark) {
  updateThemeUI(isDark);
}

// Mobile Drawer Menu Handlers
function toggleDrawerMenu(open) {
  const overlay = document.getElementById('drawerMenuOverlay');
  const panel = document.getElementById('drawerMenuPanel');
  if (!overlay || !panel) return;

  if (open) {
    panel.classList.remove('hidden');
    void panel.offsetWidth;
    overlay.classList.remove('opacity-0', 'pointer-events-none');
    overlay.classList.add('opacity-100', 'pointer-events-auto');
    panel.classList.remove('translate-x-full');
    panel.classList.add('translate-x-0');
    document.body.style.overflow = 'hidden';
    updateThemeIcon(document.documentElement.classList.contains('dark'));
    try { window.Telegram?.WebApp?.HapticFeedback?.impactOccurred('light'); } catch (e) {}
  } else {
    overlay.classList.remove('opacity-100', 'pointer-events-auto');
    overlay.classList.add('opacity-0', 'pointer-events-none');
    panel.classList.remove('translate-x-0');
    panel.classList.add('translate-x-full');
    document.body.style.overflow = '';
    setTimeout(() => {
      if (panel.classList.contains('translate-x-full')) {
        panel.classList.add('hidden');
      }
    }, 300);
  }
}

function switchTabFromDrawer(tab) {
  switchTab(tab);
  toggleDrawerMenu(false);
}

function openTutorialFromDrawer() {
  openTutorialModal(selectedPlatform);
  toggleDrawerMenu(false);
}

function scrollToLegalFromDrawer() {
  if (currentTab !== 'check') switchTab('check');
  toggleDrawerMenu(false);
  setTimeout(() => {
    const el = document.getElementById('legalCardTitle');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, 250);
}

function openPaymentFromDrawer() {
  openPaymentModal();
  toggleDrawerMenu(false);
}

window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    toggleDrawerMenu(false);
    closeTutorialModal();
    closePaymentModal();
  }
});

document.addEventListener('DOMContentLoaded', () => {
  initInteractiveMesh();
  initTheme();
  handleSplashScreen();
  applyLanguage();
  initTelegram();
  loadRegistry('all');
  init3DTilt();
});

function initTelegram() {
  const tg = window.Telegram?.WebApp;
  if (tg) {
    tg.ready();
    tg.expand();
    try {
      const isDark = document.documentElement.classList.contains('dark');
      tg.setHeaderColor(isDark ? '#0f172a' : '#f1f4f9');
      tg.setBackgroundColor(isDark ? '#0b0f19' : '#f1f4f9');
    } catch (e) {}

    const user = tg.initDataUnsafe?.user;
    if (user && user.id) {
      currentTelegramUser = user;
      currentTelegramId = user.id;
      document.getElementById('telegramUserGreeting').textContent = `${user.first_name || ''} (@${user.username || 'user'})`;
    }
  }

  if (!currentTelegramId) {
    let localId = localStorage.getItem('instasafe_guest_id');
    if (!localId) {
      localId = Math.floor(100000 + Math.random() * 900000);
      localStorage.setItem('instasafe_guest_id', localId);
    }
    currentTelegramId = parseInt(localId);
    document.getElementById('telegramUserGreeting').textContent = `Mehmon (ID: ${currentTelegramId})`;
  }

  fetchUserStatus();
}

async function fetchUserStatus() {
  if (!currentTelegramId) return;
  try {
    const res = await fetch(`/api/user/status?telegram_id=${currentTelegramId}`);
    const data = await res.json();
    if (data.success && data.user) {
      updateUserBalanceUI(data.user);
    }
  } catch (err) {}
}

function updateUserBalanceUI(userData) {
  const badgeText = document.getElementById('userChecksText');
  const badge = document.getElementById('userChecksBadge');
  const free = userData.free_checks_left || 0;
  const paid = userData.paid_checks_left || 0;
  const total = free + paid;
  userChecksLeft = total;

  if (total > 0) {
    badge.className = "flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 transition shadow-sm";
    badgeText.textContent = free > 0 ? (currentLang === 'uz' ? '1 ta bepul' : '1 бесплатно') : `${total} ta`;
  } else {
    badge.className = "flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 transition shadow-sm animate-pulse";
    badgeText.textContent = currentLang === 'uz' ? '0 ta (To\'ldirish)' : '0 (Пополнить)';
  }
}

function switchTab(tab) {
  currentTab = tab;
  const tabCheck = document.getElementById('tabCheck');
  const tabRegistry = document.getElementById('tabRegistry');
  const btnCheck = document.getElementById('tabBtnCheck');
  const btnRegistry = document.getElementById('tabBtnRegistry');

  if (tab === 'check') {
    tabRegistry.classList.add('hidden');
    tabRegistry.classList.remove('panel-animate');
    tabCheck.classList.remove('hidden');
    void tabCheck.offsetWidth;
    tabCheck.classList.add('panel-animate');
    btnCheck.className = "p-2 sm:px-3.5 sm:py-1.5 rounded-xl text-xs sm:text-sm font-bold transition bg-slate-900 text-white shadow-sm flex items-center space-x-1";
    btnRegistry.className = "p-2 sm:px-3.5 sm:py-1.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition flex items-center space-x-1";
  } else {
    tabCheck.classList.add('hidden');
    tabCheck.classList.remove('panel-animate');
    tabRegistry.classList.remove('hidden');
    void tabRegistry.offsetWidth;
    tabRegistry.classList.add('panel-animate');
    btnRegistry.className = "p-2 sm:px-3.5 sm:py-1.5 rounded-xl text-xs sm:text-sm font-bold transition bg-slate-900 text-white shadow-sm flex items-center space-x-1";
    btnCheck.className = "p-2 sm:px-3.5 sm:py-1.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition flex items-center space-x-1";
  }
  lucide.createIcons();
}

// Single Quick Check Handler
async function handleSingleCheck(event) {
  if (event) event.preventDefault();
  const input = document.getElementById('singleQueryInput');
  const query = input.value.trim();
  if (!query) return;

  hideResults();
  showLoading(true, "Oliy sud bazasidan tekshirilmoqda...", "1560+ ta rasmiy qarorlar bilan solishtirilmoqda");

  try {
    const res = await fetch('/api/check-single', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        platform: selectedPlatform,
        telegram_id: currentTelegramId
      })
    });
    const data = await res.json();
    showLoading(false);

    if (!data.success) {
      if (data.error_type === 'PAYMENT_REQUIRED') openPaymentModal();
      else renderErrorAlert(data.message || "Xatolik yuz berdi");
      return;
    }

    if (data.user_status) updateUserBalanceUI(data.user_status);
    renderResults(data.result, query);
  } catch (err) {
    showLoading(false);
    renderErrorAlert(err.message);
  }
}

// Quick Sample Runner for 1-click testing
function runQuickSample(text, plat = 'telegram') {
  selectPlatform(plat);
  setCheckMode('single');
  const input = document.getElementById('singleQueryInput');
  if (input) {
    input.value = text;
    handleSingleCheck();
  }
}

// Clear Screenshot Preview
function clearScreenshotPreview(event) {
  if (event) event.stopPropagation();
  const previewWrapper = document.getElementById('screenshotPreviewWrapper');
  const previewImg = document.getElementById('screenshotPreviewImg');
  const iconBox = document.getElementById('screenshotIconBox');
  const input = document.getElementById('screenshotInput');
  if (previewImg) previewImg.src = '';
  if (previewWrapper) previewWrapper.classList.add('hidden');
  if (iconBox) iconBox.classList.remove('hidden');
  if (input) input.value = '';
}

// Viral Telegram Share Handler
function shareToTelegram() {
  const botLink = "https://t.me/uz_instasafe_bot";
  const shareText = currentLang === 'uz'
    ? "🛡 Do'stim, Telegram va Instagram kanallaringizni Oliy sudning taqiqlangan ro'yxatiga bepul tekshirib oling! Bitta skrinshot yuborsangiz kifoya:"
    : "🛡 Проверьте свои каналы в Telegram и подписки на экстремистские материалы Верховного суда РУз! Просто отправьте скриншот боту:";
  const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(botLink)}&text=${encodeURIComponent(shareText)}`;
  if (window.Telegram?.WebApp?.openTelegramLink) {
    window.Telegram.WebApp.openTelegramLink(shareUrl);
  } else {
    window.open(shareUrl, '_blank');
  }
}

// Copy Share Link
function copyShareLink() {
  const botLink = "https://t.me/uz_instasafe_bot";
  navigator.clipboard.writeText(botLink).then(() => {
    try { window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('success'); } catch (e) {}
    alert(currentLang === 'uz' ? "Havola nusxalandi: https://t.me/uz_instasafe_bot" : "Ссылка скопирована: https://t.me/uz_instasafe_bot");
  }).catch(() => {
    alert("https://t.me/uz_instasafe_bot");
  });
}

// High-Speed Mobile Screenshot OCR Upload Handler
async function handleScreenshotUpload(event) {
  let file = null;
  if (event && event.target && event.target.files) {
    file = event.target.files[0];
  } else if (event && event.dataTransfer && event.dataTransfer.files) {
    file = event.dataTransfer.files[0];
  } else if (event instanceof File) {
    file = event;
  }
  if (!file) return;

  // Show preview
  const previewWrapper = document.getElementById('screenshotPreviewWrapper');
  const previewImg = document.getElementById('screenshotPreviewImg');
  const iconBox = document.getElementById('screenshotIconBox');
  if (previewWrapper && previewImg) {
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewWrapper.classList.remove('hidden');
      if (iconBox) iconBox.classList.add('hidden');
    };
    reader.readAsDataURL(file);
  }

  hideResults();
  showLoading(
    true,
    currentLang === 'uz' ? "AI skrinshotni tahlil qilmoqda..." : "ИИ анализирует скриншот...",
    currentLang === 'uz' ? "1560+ ta rasmiy sud qarorlari bilan tekshirilmoqda (2 soniya)" : "Сверяю каналы на фото с базой Верховного суда (2 сек.)"
  );

  const formData = new FormData();
  formData.append('file', file);
  formData.append('platform', selectedPlatform);
  if (currentTelegramId) formData.append('telegram_id', currentTelegramId);

  try {
    const res = await fetch('/api/check-screenshot', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    showLoading(false);

    if (!data.success) {
      if (data.error_type === 'PAYMENT_REQUIRED') openPaymentModal();
      else renderErrorAlert(data.message || (currentLang === 'uz' ? "Skrinshotni o'qib bo'lmadi" : "Не удалось распознать скриншот"));
      return;
    }

    if (data.user_status) updateUserBalanceUI(data.user_status);
    renderResults(data.result, file.name);
  } catch (err) {
    showLoading(false);
    renderErrorAlert(err.message);
  }
}

// Universal File Upload Handler (Telegram result.json, Instagram following.json, YouTube CSV, TXT)
async function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  hideResults();
  showLoading(true, "Fayl yuklanmoqda...", "Barcha obunalar Oliy sud bazasiga solishtirilmoqda");

  const formData = new FormData();
  formData.append('file', file);
  if (currentTelegramId) formData.append('telegram_id', currentTelegramId);

  try {
    const res = await fetch('/api/check-file', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    showLoading(false);

    if (!data.success) {
      if (data.error_type === 'PAYMENT_REQUIRED') openPaymentModal();
      else renderErrorAlert(data.message || "Faylni tahlil qilib bo'lmadi");
      return;
    }

    if (data.user_status) updateUserBalanceUI(data.user_status);
    renderResults(data.result, file.name);
  } catch (err) {
    showLoading(false);
    renderErrorAlert(err.message);
  }
}

// Render Results into Popup Modal Window & on-page Container
function renderResults(result, queryTitle) {
  const container = document.getElementById('resultsContainer');
  const modalContent = document.getElementById('resultsModalContent');
  if (container) {
    container.classList.remove('hidden');
    container.classList.remove('panel-animate');
    void container.offsetWidth;
    container.classList.add('panel-animate');
  }

  const t = I18N[currentLang];
  let html = '';

  if (result.is_safe) {
    try { window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('success'); } catch (e) {}

    // Detected channels preview pills if available (from screenshot or batch)
    let detectedChannelsHtml = '';
    if (result.detected_channels && result.detected_channels.length > 0) {
      const channelPills = result.detected_channels.slice(0, 16).map(c => `
        <span class="inline-flex items-center space-x-1 px-2.5 py-1 rounded-xl text-[11px] font-bold bg-emerald-100/90 dark:bg-emerald-950/70 text-emerald-800 dark:text-emerald-300 border border-emerald-300/70 dark:border-emerald-800/70">
          <i data-lucide="check" class="w-3 h-3 text-emerald-600 dark:text-emerald-400 shrink-0"></i>
          <span class="truncate max-w-[170px] sm:max-w-[220px]">${c}</span>
        </span>
      `).join('');

      detectedChannelsHtml = `
        <div class="pt-3 border-t border-emerald-200/70 dark:border-emerald-900/60 text-left">
          <div class="flex items-center justify-between mb-2">
            <p class="text-[11px] font-extrabold text-emerald-900 dark:text-emerald-300 flex items-center space-x-1.5">
              <i data-lucide="list-checks" class="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400"></i>
              <span>${currentLang === 'uz' ? "Aniqlangan va tekshirilgan obunalar:" : "Распознанные и проверенные подписки:"}</span>
            </p>
            <span class="text-[10px] font-black text-emerald-700 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-950 px-2 py-0.5 rounded-full">
              ${result.detected_channels.length} ta
            </span>
          </div>
          <div class="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto pr-1">
            ${channelPills}
          </div>
        </div>
      `;
    }

    html = `
      <div class="glass-card rounded-3xl p-5 sm:p-7 border-2 border-emerald-400 dark:border-emerald-500/60 bg-emerald-50/50 dark:bg-emerald-950/30 text-center space-y-4 shadow-2xl">
        <div class="w-16 h-16 sm:w-20 sm:h-20 mx-auto rounded-3xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-white flex items-center justify-center shadow-xl shadow-emerald-500/30 pulse-glow">
          <i data-lucide="shield-check" class="w-10 h-10 sm:w-12 sm:h-12 stroke-[2.2]"></i>
        </div>

        <div>
          <span class="inline-block px-3 py-1 rounded-full text-xs font-black bg-emerald-100 dark:bg-emerald-900/70 text-emerald-800 dark:text-emerald-300 uppercase tracking-wider mb-2">
            ${currentLang === 'uz' ? "Xavfsiz / Toza" : "Безопасно / Чисто"}
          </span>
          <h2 class="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">${t.safeTitle}</h2>
          <p class="text-slate-600 dark:text-slate-300 text-xs sm:text-sm max-w-md mx-auto mt-2 leading-relaxed">
            ${t.safeDesc.replace('{count}', result.total_checked)}
          </p>
        </div>

        ${detectedChannelsHtml}

        <div class="pt-2 flex flex-col sm:flex-row items-center justify-center gap-2">
          <button onclick="closeResultsModal()" class="w-full sm:flex-1 py-3 px-5 rounded-2xl bg-slate-900 dark:bg-indigo-600 text-white text-xs sm:text-sm font-black hover:bg-slate-800 dark:hover:bg-indigo-700 transition shadow-lg touch-ripple flex items-center justify-center space-x-1.5">
            <i data-lucide="rotate-ccw" class="w-4 h-4"></i>
            <span>${t.btnCheckAgain}</span>
          </button>
          <button onclick="shareToTelegram()" class="w-full sm:w-auto py-3 px-5 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs sm:text-sm font-extrabold transition shadow flex items-center justify-center space-x-1.5 touch-ripple">
            <i data-lucide="send" class="w-4 h-4"></i>
            <span>${currentLang === 'uz' ? "Do'stlarga ulashish" : "Поделиться"}</span>
          </button>
        </div>
      </div>
    `;
  } else {
    try { window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('error'); } catch (e) {}

    let itemsHtml = result.banned_found.map(item => {
      const b = item.details?.banned_item || {};
      const plat = (item.platform || b.platform || selectedPlatform).toUpperCase();
      const targetHandle = item.username || b.username || '';
      let linkUrl = '';
      if (plat.includes('TELEGRAM') && targetHandle) linkUrl = `https://t.me/${targetHandle}`;
      else if (plat.includes('YOUTUBE') && targetHandle) linkUrl = `https://youtube.com/@${targetHandle}`;
      else if (plat.includes('INSTAGRAM') && targetHandle) linkUrl = `https://instagram.com/${targetHandle}`;
      else if (plat.includes('FACEBOOK') && targetHandle) linkUrl = `https://facebook.com/${targetHandle}`;

      return `
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-3.5 sm:p-4 border-2 border-rose-300 dark:border-rose-900/70 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-rose-500 transition">
          <div class="flex items-start space-x-2.5 sm:space-x-3 min-w-0">
            <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-rose-100 dark:bg-rose-900/60 text-rose-700 dark:text-rose-300 flex items-center justify-center font-black text-xs shrink-0 mt-0.5 sm:mt-0">
              #${b.id || '?'}
            </div>
            <div class="truncate text-left">
              <div class="flex items-center space-x-2">
                <span class="font-extrabold text-slate-900 dark:text-white text-xs sm:text-sm truncate">@${item.username || b.title}</span>
                <span class="text-[9px] font-semibold px-2 py-0.2 rounded-full bg-rose-50 dark:bg-rose-950 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-800 shrink-0">${plat}</span>
              </div>
              <p class="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 mt-0.5 truncate">Sud qarori: <b class="text-rose-700 dark:text-rose-400 font-bold">${b.original || b.title}</b></p>
            </div>
          </div>
          ${linkUrl ? `
            <a href="${linkUrl}" target="_blank" rel="noopener noreferrer" class="w-full sm:w-auto px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs flex items-center justify-center space-x-1.5 shadow transition shrink-0">
              <span>${t.unsubscribeBtn}</span>
              <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
            </a>
          ` : ''}
        </div>
      `;
    }).join('');

    html = `
      <div class="glass-card rounded-3xl p-5 sm:p-7 border-2 border-rose-500 dark:border-rose-600/70 bg-rose-50/40 dark:bg-rose-950/30 space-y-4 shadow-2xl">
        <div class="flex items-center space-x-3 text-left border-b border-rose-200 dark:border-rose-900/60 pb-4">
          <div class="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-rose-600 text-white flex items-center justify-center shadow-lg shadow-rose-600/40 shrink-0 animate-pulse">
            <i data-lucide="alert-triangle" class="w-7 h-7 stroke-[2.2]"></i>
          </div>
          <div>
            <span class="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-black bg-rose-600 text-white uppercase tracking-wider mb-0.5">Xavf / Опасность</span>
            <h2 class="text-lg sm:text-xl font-black text-slate-900 dark:text-white">${t.bannedTitle.replace('{count}', result.banned_count)}</h2>
            <p class="text-xs text-slate-600 dark:text-slate-400">Jami tekshirildi: ${result.total_checked} ta obuna / kanal</p>
          </div>
        </div>

        <div class="space-y-2.5 max-h-60 overflow-y-auto pr-1">
          <h4 class="font-bold text-slate-800 dark:text-slate-200 text-xs text-left">Zudlik bilan chiqib ketish (unfollow) tavsiya etiladi:</h4>
          ${itemsHtml}
        </div>

        <div class="bg-rose-100/90 dark:bg-rose-950/70 border border-rose-200 dark:border-rose-900/60 rounded-2xl p-3 text-[11px] sm:text-xs text-rose-900 dark:text-rose-200 leading-relaxed text-left">
          ${t.bannedAlertNote}
        </div>

        <div class="pt-2 flex flex-col sm:flex-row items-center gap-2">
          <button onclick="closeResultsModal()" class="w-full py-2.5 px-4 rounded-xl bg-slate-900 dark:bg-indigo-600 text-white font-extrabold text-xs shadow hover:bg-slate-800 transition">
            ${currentLang === 'uz' ? "Tushundim, yopish" : "Понятно, закрыть"}
          </button>
        </div>
      </div>
    `;
  }

  if (container) container.innerHTML = html;
  if (modalContent) modalContent.innerHTML = html;

  // Open popup modal immediately so user sees results front and center
  openModal('resultsModal', 'resultsModalDialog');
  lucide.createIcons();
}

function closeResultsModal() {
  closeModal('resultsModal', 'resultsModalDialog');
  const target = document.getElementById('searchArea') || document.getElementById('dropZone') || document.getElementById('singleQueryInput');
  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

function renderErrorAlert(msg) {
  const container = document.getElementById('resultsContainer');
  const modalContent = document.getElementById('resultsModalContent');
  const errorHtml = `
    <div class="glass-card rounded-3xl p-6 border-2 border-rose-300 dark:border-rose-800 bg-rose-50 dark:bg-rose-950/40 text-center space-y-3 shadow-xl">
      <div class="w-12 h-12 mx-auto rounded-2xl bg-rose-100 dark:bg-rose-900 text-rose-600 dark:text-rose-300 flex items-center justify-center font-bold">
        <i data-lucide="alert-circle" class="w-6 h-6"></i>
      </div>
      <div>
        <h3 class="text-base font-black text-rose-800 dark:text-rose-200">${currentLang === 'uz' ? "Xatolik" : "Ошибка"}</h3>
        <p class="text-rose-700 dark:text-rose-300 font-semibold text-xs mt-1">${msg}</p>
      </div>
      <button onclick="closeResultsModal()" class="px-5 py-2 rounded-xl bg-slate-900 dark:bg-indigo-600 text-white text-xs font-bold hover:bg-slate-800 transition shadow">
        ${currentLang === 'uz' ? "Yopish" : "Закрыть"}
      </button>
    </div>
  `;
  if (container) {
    container.classList.remove('hidden');
    container.innerHTML = errorHtml;
  }
  if (modalContent) {
    modalContent.innerHTML = errorHtml;
    openModal('resultsModal', 'resultsModalDialog');
  }
  lucide.createIcons();
}

function hideResults() {
  closeResultsModal();
  const c = document.getElementById('resultsContainer');
  if (c) c.classList.add('hidden');
}

function showLoading(show, title = "", subtitle = "") {
  const el = document.getElementById('loadingBox');
  const bar = document.getElementById('loadingProgressBar');

  if (loadingInterval) {
    clearInterval(loadingInterval);
    loadingInterval = null;
  }

  if (show) {
    el.classList.remove('hidden');
    el.classList.remove('panel-animate');
    void el.offsetWidth;
    el.classList.add('panel-animate');
    document.getElementById('loadingTitle').textContent = title;
    document.getElementById('loadingSubtitle').textContent = subtitle;

    let progress = 10;
    if (bar) bar.style.width = '10%';

    loadingInterval = setInterval(() => {
      if (progress < 90) {
        progress += Math.floor(Math.random() * 10) + 5;
        if (progress > 90) progress = 90;
        if (bar) bar.style.width = `${progress}%`;
      }
    }, 300);
  } else {
    if (bar) bar.style.width = '100%';
    setTimeout(() => {
      el.classList.add('hidden');
    }, 200);
  }
}

// Registry Loader and Filter
async function loadRegistry(platform = 'all') {
  try {
    const url = platform === 'all' ? '/api/banned-list' : `/api/banned-list?platform=${platform}`;
    const res = await fetch(url);
    const data = await res.json();
    allBannedItems = data.items || [];
    renderRegistryTable(allBannedItems);
  } catch (err) {}
}

function filterRegistryPlatform(plat) {
  selectedRegistryFilter = plat;
  ['all', 'telegram', 'instagram', 'facebook', 'youtube', 'tiktok'].forEach(p => {
    const btn = document.getElementById(`rfBtn_${p}`);
    if (!btn) return;
    if (p === plat) {
      btn.className = "px-3 py-1 rounded-xl text-xs font-bold bg-slate-900 text-white shadow-sm";
    } else {
      btn.className = "px-3 py-1 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100";
    }
  });
  loadRegistry(plat);
}

function renderRegistryTable(items) {
  const tbody = document.getElementById('registryTableBody');
  if (!items || items.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="p-4 text-center text-slate-400">Hech narsa topilmadi / Ничего не найдено</td></tr>`;
    return;
  }
  tbody.innerHTML = items.map(it => {
    const plat = (it.platform || 'all').toUpperCase();
    const handle = it.username || '';
    let link = '';
    if (plat.includes('TELEGRAM') && handle) link = `https://t.me/${handle}`;
    else if (plat.includes('YOUTUBE') && handle) link = `https://youtube.com/@${handle}`;
    else if (plat.includes('INSTAGRAM') && handle) link = `https://instagram.com/${handle}`;
    else if (plat.includes('FACEBOOK') && handle) link = `https://facebook.com/${handle}`;

    return `
      <tr class="hover:bg-slate-50 transition">
        <td class="p-2.5 font-bold text-slate-400 text-xs">#${it.id}</td>
        <td class="p-2.5"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700">${plat}</span></td>
        <td class="p-2.5">
          ${link ? `
            <a href="${link}" target="_blank" rel="noopener noreferrer" class="font-bold text-indigo-600 hover:underline">
              @${handle}
            </a>
          ` : `<span class="font-bold text-slate-800">${it.title || '-'}</span>`}
        </td>
        <td class="p-2.5 text-slate-700">${it.original || it.title}</td>
      </tr>
    `;
  }).join('');
  lucide.createIcons();
}

function filterRegistry() {
  const q = document.getElementById('registrySearchInput').value.toLowerCase().trim();
  if (!q) {
    renderRegistryTable(allBannedItems);
    return;
  }
  const filtered = allBannedItems.filter(it => 
    (it.original && it.original.toLowerCase().includes(q)) ||
    (it.username && it.username.toLowerCase().includes(q)) ||
    (it.title && it.title.toLowerCase().includes(q))
  );
  renderRegistryTable(filtered);
}

// Generic Silky Animated Modal Open/Close Helpers
function openModal(modalId, dialogId) {
  const modal = document.getElementById(modalId);
  const dialog = document.getElementById(dialogId);
  if (!modal) return;
  modal.classList.remove('hidden');
  void modal.offsetWidth; // Trigger CSS reflow so animation starts smoothly
  modal.classList.add('modal-open');
  if (dialog) dialog.classList.add('modal-card-open');
  document.body.style.overflow = 'hidden';
}

function closeModal(modalId, dialogId) {
  const modal = document.getElementById(modalId);
  const dialog = document.getElementById(dialogId);
  if (!modal) return;
  modal.classList.remove('modal-open');
  if (dialog) dialog.classList.remove('modal-card-open');
  document.body.style.overflow = '';
  setTimeout(() => {
    if (!modal.classList.contains('modal-open')) {
      modal.classList.add('hidden');
    }
  }, 280);
}

// Payment and Modal Handlers
function openPaymentModal() {
  openModal('paymentModal', 'paymentModalDialog');
  try { window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('warning'); } catch (e) {}
  lucide.createIcons();
}

function closePaymentModal() {
  closeModal('paymentModal', 'paymentModalDialog');
}

async function handlePaymentCheckout(provider) {
  const selectedPlan = document.querySelector('input[name="plan"]:checked')?.value || 'single';
  try {
    const res = await fetch('/api/payment/create-order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        telegram_id: currentTelegramId,
        package: selectedPlan,
        provider: provider
      })
    });
    const data = await res.json();
    if (!data.success) {
      alert("To'lov yaratishda xatolik");
      return;
    }

    const payUrl = provider === 'click' ? data.click_url : data.payme_url;
    if (window.Telegram?.WebApp?.openLink) {
      window.Telegram.WebApp.openLink(payUrl);
    } else {
      window.open(payUrl, '_blank');
    }

    const msg = currentLang === 'uz'
      ? `To'lov sahifasi ochilmoqda (№${data.order_id}). To'lov amalga oshirilgach, hisobingizga ${data.checks_count} ta tekshiruv avtomatik qo'shiladi.`
      : `Открывается страница оплаты (Заказ №${data.order_id}). После оплаты вам будет начислено ${data.checks_count} проверок.`;
    alert(msg);
  } catch (err) {
    alert(err.message);
  }
}

async function handleDemoFreePayment() {
  const selectedPlan = document.querySelector('input[name="plan"]:checked')?.value || 'single';
  try {
    const resOrder = await fetch('/api/payment/create-order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        telegram_id: currentTelegramId,
        package: selectedPlan,
        provider: "demo"
      })
    });
    const dataOrder = await resOrder.json();
    const resConfirm = await fetch('/api/payment/confirm-order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: dataOrder.order_id })
    });
    const dataConfirm = await resConfirm.json();

    if (dataConfirm.success) {
      try { window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('success'); } catch (e) {}
      alert(`✅ Muvaffaqiyatli to'ldirildi: ${dataOrder.checks_count} ta tekshiruv!`);
      closePaymentModal();
      fetchUserStatus();
    }
  } catch (err) {
    alert(err.message);
  }
}

// Tutorial Modal Multi-Platform & Device State
let tutorialPlatform = 'telegram';
let tutorialDevice = 'mobile';

function openTutorialModal(plat) {
  if (plat) tutorialPlatform = plat;
  else if (selectedPlatform) tutorialPlatform = selectedPlatform;
  else tutorialPlatform = 'instagram';

  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  tutorialDevice = isMobile ? 'mobile' : 'desktop';

  openModal('tutorialModal', 'tutorialModalDialog');
  updateTutorialTabsUI();
  renderTutorialContent();
  lucide.createIcons();
}

function closeTutorialModal() {
  closeModal('tutorialModal', 'tutorialModalDialog');
}

function switchTutorialPlatform(plat) {
  tutorialPlatform = plat;
  updateTutorialTabsUI();
  renderTutorialContent();
  lucide.createIcons();
}

function switchTutorialDevice(dev) {
  tutorialDevice = dev;
  updateTutorialTabsUI();
  renderTutorialContent();
  lucide.createIcons();
}

function updateTutorialTabsUI() {
  ['telegram', 'youtube', 'instagram', 'facebook', 'tiktok'].forEach(p => {
    const btn = document.getElementById(`tutTab_${p}`);
    if (!btn) return;
    if (p === tutorialPlatform) {
      btn.className = `flex-1 py-1.5 px-1 rounded-xl transition flex items-center justify-center space-x-1.5 plat-active-${p} shadow-md font-extrabold`;
    } else {
      btn.className = "flex-1 py-1.5 px-1 rounded-xl transition flex items-center justify-center space-x-1.5 text-slate-600 dark:text-slate-300 hover:text-slate-900 font-bold bg-white/70 dark:bg-slate-800/60";
    }
  });

  const btnMob = document.getElementById('tutDev_mobile');
  const btnDsk = document.getElementById('tutDev_desktop');
  if (btnMob && btnDsk) {
    if (tutorialDevice === 'mobile') {
      btnMob.className = "py-1 px-3.5 rounded-full text-[11px] font-extrabold transition flex items-center space-x-1 bg-slate-900 text-white dark:bg-indigo-600 shadow-sm";
      btnDsk.className = "py-1 px-3.5 rounded-full text-[11px] font-bold transition flex items-center space-x-1 text-slate-600 hover:text-slate-900 bg-slate-100 dark:bg-slate-800 dark:text-slate-300";
    } else {
      btnDsk.className = "py-1 px-3.5 rounded-full text-[11px] font-extrabold transition flex items-center space-x-1 bg-slate-900 text-white dark:bg-indigo-600 shadow-sm";
      btnMob.className = "py-1 px-3.5 rounded-full text-[11px] font-bold transition flex items-center space-x-1 text-slate-600 hover:text-slate-900 bg-slate-100 dark:bg-slate-800 dark:text-slate-300";
    }
  }
}

function renderTutorialContent() {
  const stepsContainer = document.getElementById('tutStepsContent');
  const gifBadge = document.getElementById('tutGifFormatBadge');
  const gifImg = document.getElementById('tutGifImg');
  const deliveryFileBadge = document.getElementById('tutDeliveryFileBadge');
  const deliveryDesc = document.getElementById('tutDeliveryDesc');
  const isUz = currentLang === 'uz';

  const GUIDES = {
    telegram: {
      format: "JSON (result.json)",
      file: "result.json",
      delivery: isUz 
        ? "Fayl kompyuteringiz yoki telefoningizdagi <b>Yuklamalar (Downloads) ➔ Telegram Desktop</b> papkasiga saqlanadi. Ushbu <code>result.json</code> faylini botimizga tashlang!"
        : "Файл сразу сохраняется в папке <b>Загрузки (Downloads) ➔ Telegram Desktop</b> на вашем компьютере или телефоне. Отправьте <code>result.json</code> в наш бот!",
      mobile: {
        steps: isUz ? [
          "<b>1. Eng tezkor usul:</b> Telegram ilovasida kanallaringiz ro'yxatini shunchaki <b>skrinshot qiling</b> va botga rasm sifatida yuboring! AI 2 soniyada barcha kanallarni tekshiradi.",
          "<b>2. Bitta kanalni tekshirish:</b> Shubhali kanaldan xabarni to'g'ridan-to'g'ri botimizga <b>forward (uzatish)</b> qiling.",
          "<b>3. Kompyuterda eksport:</b> Telegram Desktop ➔ Sozlamalar ➔ Qo'shimcha ➔ Export Telegram data (faqat «Channels list», JSON)."
        ] : [
          "<b>1. Самый быстрый способ:</b> Сделайте <b>скриншот списка каналов</b> на телефоне и отправьте фото в чат бота! ИИ проверит все каналы за 2 секунды.",
          "<b>2. Проверка любого канала:</b> Просто перешлите (forward) сообщение из канала прямо в бот.",
          "<b>3. Экспорт на компьютере:</b> Telegram Desktop ➔ Настройки ➔ Продвинутые настройки ➔ Экспорт данных Telegram (только «Список каналов», JSON)."
        ]
      },
      desktop: {
        steps: isUz ? [
          "<b>1. Dasturni ochish:</b> Kompyuterda <b>Telegram Desktop</b> ilovasini oching.",
          "<b>2. Sozlamalar:</b> <b>Settings (Sozlamalar)</b> ➔ <b>Advanced (Qo'shimcha)</b> ➔ <b>Export Telegram data</b>.",
          "<b>3. Tanlash:</b> Barcha belgilarni olib tashlab, faqat <b>«Channels list» (Kanallar ro'yxati)</b>ni qoldiring.",
          "<b>4. Format:</b> Pastda formatni <b>JSON (Machine-readable)</b> qilib tanlang va «Export» tugmasini bosing.",
          "<b>5. Yuklash:</b> Tayyor bo'lgan <code>result.json</code> faylini shu yerga tashlang yoki botga yuboring!"
        ] : [
          "<b>1. Открытие:</b> Запустите <b>Telegram Desktop</b> на компьютере.",
          "<b>2. Настройки:</b> <b>Настройки</b> ➔ <b>Продвинутые настройки</b> ➔ <b>Экспорт данных Telegram</b>.",
          "<b>3. Выбор:</b> Снимите все галочки и оставьте только <b>«Список каналов»</b>.",
          "<b>4. Формат:</b> Внизу выберите формат <b>JSON</b> (машиночитаемый) и нажмите «Экспорт».",
          "<b>5. Загрузка:</b> Отправьте полученный файл <code>result.json</code> на сайт или в бот!"
        ]
      }
    },
    instagram: {
      format: "JSON (following.json)",
      file: "following.json",
      delivery: isUz
        ? "Instagram profilingizga biriktirilgan <b>Email pochtangizga</b> xavfsiz yuklab olish havolasi keladi (yoki Ilovaning bildirishnomalar bo'limidan olasiz). Yuklab olingan arxivdan <code>following.json</code> faylini botga yuboring!"
        : "На вашу <b>электронную почту</b> или во вкладку уведомлений Instagram придёт безопасная ссылка на скачивание архива. Извлеките и отправьте файл <code>following.json</code> в наш бот!",
      mobile: {
        steps: isUz ? [
          "<b>1. Sozlamalarga kirish:</b> Instagram ilovasida Profilingizga o'ting ➔ Yuqoridagi ☰ menyu ➔ <b>Hisoblar markazi (Accounts Center)</b>.",
          "<b>2. Ma'lumotlarni yuklab olish:</b> <b>«Sizning ma'lumotlaringiz va ruxsatlaringiz»</b> ➔ <b>«Ma'lumotlaringizni yuklab olish» (Download info)</b>.",
          "<b>3. Obunalarni tanlash:</b> «Ba'zi ma'lumotlarni yuklab olish» ➔ Ro'yxatdan faqat <b>«Obunachilar va obunalar» (Followers and following)</b>ni belgilang.",
          "<b>4. Formatni tanlash:</b> Format bo'limida <b>JSON</b>ni tanlang (HTML emas!) va faylni so'rang.",
          "<b>5. Yuklash:</b> Email pochtangizga kelgan arxivdan <code>following.json</code> faylini botga yuboring!",
          "💡 <b>Yana ham oson usul:</b> Instagram obunalaringiz sahifasini skrinshot qilib botga rasm yuboring!"
        ] : [
          "<b>1. Меню настроек:</b> В приложении Instagram откройте профиль ➔ ☰ Меню ➔ <b>Центр аккаунтов (Accounts Center)</b>.",
          "<b>2. Выгрузка данных:</b> <b>«Ваша информация и разрешения»</b> ➔ <b>«Скачать информацию» (Download info)</b>.",
          "<b>3. Выбор подписок:</b> Выберите «Выбрать информацию» ➔ отметьте только <b>«Подписчики и подписки»</b>.",
          "<b>4. Формат:</b> Обязательно укажите формат <b>JSON</b> (не HTML!) и запросите файл.",
          "<b>5. Загрузка:</b> Отправьте полученный файл <code>following.json</code> в наш бот!",
          "💡 <b>Еще быстрее:</b> Просто сделайте скриншот списка подписок и пришлите фото в бот!"
        ]
      },
      desktop: {
        steps: isUz ? [
          "<b>1. Saytga kirish:</b> Kompyuterda <code>instagram.com</code> saytini oching va tizimga kiring.",
          "<b>2. Sozlamalar:</b> Chap pastki menyudan Sozlamalar ➔ Maxfiylik va xavfsizlik ➔ Ma'lumotlarni yuklab olish.",
          "<b>3. JSON tanlash:</b> Format sifatida <b>JSON</b>ni ko'rsatib eksport qiling.",
          "<b>4. Yuklash:</b> <code>following.json</code> faylini ushbu sahifaga tashlang."
        ] : [
          "<b>1. Сайт:</b> Откройте <code>instagram.com</code> на компьютере и войдите в аккаунт.",
          "<b>2. Настройки:</b> Настройки ➔ Конфиденциальность и безопасность ➔ Скачивание данных.",
          "<b>3. Формат:</b> Укажите формат <b>JSON</b> и нажмите «Далее».",
          "<b>4. Загрузка:</b> Перетащите файл <code>following.json</code> в форму на сайте."
        ]
      }
    },
    youtube: {
      format: "CSV (subscriptions.csv)",
      file: "subscriptions.csv",
      delivery: isUz
        ? "Google Takeout sizning <b>Gmail pochtangizga</b> yuklab olish havolasini yuboradi. <code>takeout-*.zip</code> arxivini ochib, ichidagi <code>subscriptions.csv</code> faylini botimizga tashlang!"
        : "Google Takeout отправит архив на вашу <b>почту Gmail</b>. Скачайте архив и отправьте файл <code>subscriptions.csv</code> в бот!",
      mobile: {
        steps: isUz ? [
          "<b>1. Eng tezkor usul:</b> YouTube ilovasida pastdagi <b>«Obunalar» (Subscriptions)</b> sahifasini skrinshot qilib botga rasm sifatida yuboring!",
          "<b>2. Google Takeout orqali:</b> Mobil brauzerda <code>takeout.google.com</code> saytini oching.",
          "<b>3. Tanlash:</b> Barcha belgilarni bekor qilib, faqat <b>«YouTube»</b>ni tanlang ➔ Faqat <b>«Obunalar» (CSV)</b>ni qoldiring.",
          "<b>4. Yuklash:</b> Olingan <code>subscriptions.csv</code> faylini botga yuboring."
        ] : [
          "<b>1. Самый быстрый способ:</b> Откройте вкладку <b>«Подписки»</b> в приложении YouTube, сделайте скриншот и отправьте фото в бот!",
          "<b>2. Через Google Takeout:</b> В мобильном браузере откройте <code>takeout.google.com</code>.",
          "<b>3. Выбор:</b> Отмените всё и выберите только <b>«YouTube»</b> ➔ оставьте только <b>«Подписки» (CSV)</b>.",
          "<b>4. Загрузка:</b> Отправьте файл <code>subscriptions.csv</code> в бот."
        ]
      },
      desktop: {
        steps: isUz ? [
          "<b>1. Saytga o'tish:</b> Kompyuter brauzerida <code>takeout.google.com</code> saytini oching.",
          "<b>2. YouTube'ni tanlash:</b> «Barchasini bekor qilish» tugmasini bosing va faqat <b>«YouTube va YouTube Music»</b>ni belgilang.",
          "<b>3. Obunalar:</b> «Barcha YouTube ma'lumotlari kiritilgan» tugmasini bosib, faqat <b>«Obunalar»</b> katakchasini qoldiring.",
          "<b>4. Yaratish:</b> «Keyingi bosqich» ➔ «Eksport yaratish».",
          "<b>5. Faylni tashlash:</b> Yuklangan arxivdagi <code>subscriptions.csv</code> faylini shu yerga tashlang."
        ] : [
          "<b>1. Переход:</b> В браузере перейдите на <code>takeout.google.com</code>.",
          "<b>2. Выбор YouTube:</b> Нажмите «Снять все отметки» и отметьте только <b>«YouTube и YouTube Music»</b>.",
          "<b>3. Только подписки:</b> Нажмите «Все данные YouTube включены» и оставьте галочку только на <b>«Подписки»</b>.",
          "<b>4. Экспорт:</b> Нажмите «Далее» ➔ «Создать экспорт».",
          "<b>5. Загрузка:</b> Перетащите файл <code>subscriptions.csv</code> в поле загрузки на сайте."
        ]
      }
    },
    facebook: {
      format: "JSON (friends_and_followers.json)",
      file: "friends_and_followers.json",
      delivery: isUz
        ? "Facebook sizning <b>Email pochtangizga</b> va ilovadagi bildirishnomalarga yuklab olish xabarini yuboradi. <code>friends_and_followers.json</code> faylini botga yuboring!"
        : "Facebook отправит ссылку на скачивание на вашу <b>электронную почту</b> и в уведомления приложения. Отправьте <code>friends_and_followers.json</code> в бот!",
      mobile: {
        steps: isUz ? [
          "<b>1. Sozlamalar:</b> Facebook ilovasi ➔ Menyu ➔ Sozlamalar va maxfiylik ➔ <b>Sozlamalar</b>.",
          "<b>2. Yuklab olish:</b> <b>«Ma'lumotlaringizni yuklab olish» (Download your information)</b> bo'limiga kiring.",
          "<b>3. Tanlash:</b> Faqat <b>«Do'stlar va obunachilar» (Friends and followers)</b>ni belgilang.",
          "<b>4. Format:</b> Formatni <b>JSON</b> qilib belgilang va faylni yuklab oling.",
          "<b>5. Tekshirish:</b> Olingan JSON faylini saytga yoki botga yuboring."
        ] : [
          "<b>1. Настройки:</b> В приложении Facebook откройте Меню ➔ Настройки и конфиденциальность ➔ <b>Настройки</b>.",
          "<b>2. Выгрузка:</b> Перейдите в раздел <b>«Скачать информацию» (Download your information)</b>.",
          "<b>3. Выбор:</b> Выберите только <b>«Друзья и подписчики»</b>.",
          "<b>4. Формат:</b> Укажите формат <b>JSON</b> и запросите выгрузку.",
          "<b>5. Проверка:</b> Отправьте полученный JSON-файл в наш бот или загрузите на сайт."
        ]
      },
      desktop: {
        steps: isUz ? [
          "<b>1. Sayt:</b> <code>facebook.com</code> saytida Profilingiz ➔ Sozlamalar va maxfiylik ➔ Sozlamalar.",
          "<b>2. Maxfiylik:</b> Sizning Facebook ma'lumotlaringiz ➔ Ma'lumotlarni yuklab olish.",
          "<b>3. Format:</b> Format: JSON ➔ Yuklab olingan faylni botga tashlang."
        ] : [
          "<b>1. Сайт:</b> На <code>facebook.com</code> откройте Настройки и конфиденциальность ➔ Настройки.",
          "<b>2. Данные:</b> Ваша информация на Facebook ➔ Скачать информацию.",
          "<b>3. Формат:</b> Выберите JSON и загрузите файл в бота."
        ]
      }
    },
    tiktok: {
      format: "JSON (user_data.json)",
      file: "user_data.json",
      delivery: isUz
        ? "Fayl TikTok ilovasidagi <b>Profil ➔ Sozlamalar ➔ Hisob ➔ «Download data» (Ma'lumotlarni yuklab olish)</b> varaqasida tayyor bo'ladi. <code>user_data.json</code> faylini yuklab olib botga yuboring!"
        : "Файл будет доступен прямо в приложении TikTok во вкладке <b>Профиль ➔ Настройки ➔ Скачать данные ➔ «Download data»</b>. Скачайте <code>user_data.json</code> и отправьте в бот!",
      mobile: {
        steps: isUz ? [
          "<b>1. Profilga o'tish:</b> TikTok ilovasida Profilingizga kiring ➔ Yuqoridagi ☰ menyu ➔ <b>Sozlamalar va maxfiylik (Settings and privacy)</b>.",
          "<b>2. Hisob bo'limi:</b> <b>«Hisob» (Account)</b> ➔ <b>«Ma'lumotlaringizni yuklab olish» (Download your data)</b>.",
          "<b>3. Formatni tanlash:</b> Format variantlaridan <b>«JSON - Machine-readable file»</b> ni tanlang (TXT emas!).",
          "<b>4. So'rov yuborish:</b> Qizil «Request data» tugmasini bosing.",
          "<b>5. Faylni olish:</b> Tayyor bo'lgach, «Download data» varaqasidan <code>user_data.json</code> faylini yuklab olib botga yuboring.",
          "💡 <b>Yana ham osoni:</b> TikTok'da 'Obunalar' (Following) ro'yxatini ochib skrinshot qiling va botga rasm tashlang!"
        ] : [
          "<b>1. Меню профиля:</b> В приложении TikTok откройте Профиль ➔ ☰ Меню ➔ <b>Настройки и конфиденциальность (Settings and privacy)</b>.",
          "<b>2. Раздел Аккаунт:</b> Нажмите <b>«Аккаунт» (Account)</b> ➔ <b>«Скачать свои данные» (Download your data)</b>.",
          "<b>3. Выбор формата:</b> Выберите формат <b>«JSON - Машиночитаемый файл»</b> (не TXT!).",
          "<b>4. Запрос данных:</b> Нажмите красную кнопку «Запросить данные» (Request data).",
          "<b>5. Получение файла:</b> Когда архив будет готов, скачайте его во вкладке «Скачать данные» и отправьте <code>user_data.json</code> в бот.",
          "💡 <b>Еще быстрее:</b> Откройте список «Подписки» в TikTok, сделайте скриншот и отправьте фото в бот!"
        ]
      },
      desktop: {
        steps: isUz ? [
          "<b>1. Sayt:</b> <code>tiktok.com</code> saytida Profilingiz ➔ Sozlamalar ➔ Maxfiylik.",
          "<b>2. Yuklab olish:</b> Ma'lumotlarni yuklab olish ➔ Format: JSON.",
          "<b>3. Botga yuborish:</b> Olingan JSON faylini botga yuklang."
        ] : [
          "<b>1. Сайт:</b> На <code>tiktok.com</code> перейдите в Настройки ➔ Конфиденциальность.",
          "<b>2. Выгрузка:</b> Скачать данные ➔ Формат: JSON.",
          "<b>3. Проверка:</b> Загрузите полученный файл в бот."
        ]
      }
    }
  };

  const item = GUIDES[tutorialPlatform] || GUIDES.instagram;
  const devData = item[tutorialDevice] || item.mobile;

  // Silky smooth crossfading GIF transition
  if (gifImg) {
    const targetGifSrc = `/gifs/${tutorialPlatform}.gif`;
    const currentActive = gifImg.getAttribute('data-active-src');
    if (currentActive !== targetGifSrc) {
      gifImg.setAttribute('data-active-src', targetGifSrc);
      gifImg.style.opacity = '0.35';
      gifImg.style.transform = 'scale(0.97)';

      const preload = new Image();
      preload.onload = () => {
        if (gifImg.getAttribute('data-active-src') === targetGifSrc) {
          gifImg.src = targetGifSrc;
          gifImg.style.opacity = '1';
          gifImg.style.transform = 'scale(1)';
        }
      };
      preload.onerror = () => {
        if (gifImg.getAttribute('data-active-src') === targetGifSrc) {
          gifImg.src = targetGifSrc;
          gifImg.style.opacity = '1';
          gifImg.style.transform = 'scale(1)';
        }
      };
      preload.src = targetGifSrc;
    } else {
      gifImg.style.opacity = '1';
      gifImg.style.transform = 'scale(1)';
    }
  }
  if (gifBadge) {
    gifBadge.textContent = item.format;
  }
  if (deliveryFileBadge) {
    deliveryFileBadge.textContent = item.file;
  }
  if (deliveryDesc) {
    deliveryDesc.innerHTML = item.delivery;
  }

  // Render collapsible text steps
  if (stepsContainer) {
    stepsContainer.innerHTML = devData.steps.map((st, i) => `
      <div class="p-2.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-start space-x-2 shadow-sm">
        <span class="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">${i+1}</span>
        <div class="text-[11px] sm:text-xs text-slate-700 dark:text-slate-300 leading-relaxed">${st}</div>
      </div>
    `).join('');
  }
}

// INTERACTIVE MOUSE GRADIENT SPHERE (FOLLOWS CURSOR)
function initInteractiveMesh() {
  const sphere = document.getElementById('mouseGlowSphere');
  if (!sphere) return;

  let targetX = window.innerWidth / 2;
  let targetY = window.innerHeight / 3;
  let currentX = targetX;
  let currentY = targetY;

  function updatePointer(x, y) {
    targetX = x;
    targetY = y;
  }

  window.addEventListener('mousemove', (e) => {
    updatePointer(e.clientX, e.clientY);
  }, { passive: true });

  window.addEventListener('touchstart', (e) => {
    if (e.touches && e.touches[0]) {
      updatePointer(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: true });

  window.addEventListener('touchmove', (e) => {
    if (e.touches && e.touches[0]) {
      updatePointer(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: true });

  sphere.style.left = `${currentX}px`;
  sphere.style.top = `${currentY}px`;

  function animateGlow() {
    currentX += (targetX - currentX) * 0.085;
    currentY += (targetY - currentY) * 0.085;
    sphere.style.left = `${currentX}px`;
    sphere.style.top = `${currentY}px`;
    requestAnimationFrame(animateGlow);
  }
  requestAnimationFrame(animateGlow);
}

// INTERACTIVE 3D TILT EFFECT WITH DYNAMIC SPECULAR GLARE
function init3DTilt() {
  const tiltElements = document.querySelectorAll('.tilt-3d');

  tiltElements.forEach(el => {
    if (el.dataset.tiltInitialized) return;
    el.dataset.tiltInitialized = 'true';

    // Specular glare reflection overlay
    let glareLayer = null;
    let glareHighlight = null;
    if (el.dataset.tiltGlare !== 'false') {
      glareLayer = document.createElement('div');
      glareLayer.className = 'tilt-glare-layer';
      glareHighlight = document.createElement('div');
      glareHighlight.className = 'tilt-glare-highlight';
      glareLayer.appendChild(glareHighlight);
      el.appendChild(glareLayer);
    }

    const maxTilt = parseFloat(el.dataset.tiltMax || '10');
    const scale = parseFloat(el.dataset.tiltScale || '1.02');
    const perspective = parseFloat(el.dataset.tiltPerspective || '1000');

    let rafId = null;
    let isHovered = false;

    function applyTilt(clientX, clientY) {
      const rect = el.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) return;

      const x = Math.max(0, Math.min(rect.width, clientX - rect.left));
      const y = Math.max(0, Math.min(rect.height, clientY - rect.top));

      const normX = (x / rect.width) * 2 - 1; // -1 to 1
      const normY = (y / rect.height) * 2 - 1; // -1 to 1

      const rotX = (-normY * maxTilt).toFixed(2);
      const rotY = (normX * maxTilt).toFixed(2);

      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => {
        el.style.transform = `perspective(${perspective}px) rotateX(${rotX}deg) rotateY(${rotY}deg) scale3d(${scale}, ${scale}, ${scale})`;

        if (glareHighlight) {
          const isDark = document.documentElement.classList.contains('dark');
          const glareColor = isDark ? 'rgba(255, 255, 255, 0.16)' : 'rgba(255, 255, 255, 0.38)';
          glareHighlight.style.background = `radial-gradient(circle 320px at ${x}px ${y}px, ${glareColor} 0%, transparent 75%)`;
        }
      });
    }

    function resetTilt() {
      isHovered = false;
      if (rafId) cancelAnimationFrame(rafId);
      el.style.transition = 'transform 0.55s cubic-bezier(0.16, 1, 0.3, 1)';
      el.style.transform = `perspective(${perspective}px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
      if (glareLayer) glareLayer.style.opacity = '0';
    }

    // Pointer events for desktop mouse & trackpad
    el.addEventListener('pointerenter', (e) => {
      if (e.pointerType === 'touch') return;
      isHovered = true;
      el.style.transition = 'transform 0.12s ease-out';
      if (glareLayer) glareLayer.style.opacity = '1';
      applyTilt(e.clientX, e.clientY);
    });

    el.addEventListener('pointermove', (e) => {
      if (!isHovered || e.pointerType === 'touch') return;
      applyTilt(e.clientX, e.clientY);
    });

    el.addEventListener('pointerleave', (e) => {
      if (e.pointerType === 'touch') return;
      resetTilt();
    });

    // Touch device press & tilt
    el.addEventListener('touchstart', (e) => {
      if (e.touches && e.touches[0]) {
        isHovered = true;
        el.style.transition = 'transform 0.15s ease-out';
        if (glareLayer) glareLayer.style.opacity = '1';
        applyTilt(e.touches[0].clientX, e.touches[0].clientY);
      }
    }, { passive: true });

    el.addEventListener('touchend', resetTilt, { passive: true });
    el.addEventListener('touchcancel', resetTilt, { passive: true });
  });
}

// Drag & Drop Setup
document.addEventListener('DOMContentLoaded', () => {
  const dropZone = document.getElementById('dropZone');
  const screenshotDropZone = document.getElementById('screenshotDropZone');

  function bindDrop(el, handler) {
    if (!el) return;
    ['dragenter', 'dragover'].forEach(eventName => {
      el.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        el.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      el.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        el.classList.remove('dragover');
      }, false);
    });

    el.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files && files.length > 0) {
        handler(files[0]);
      }
    }, false);
  }

  bindDrop(dropZone, (f) => handleFileUpload({ target: { files: [f] } }));
  bindDrop(screenshotDropZone, (f) => handleScreenshotUpload(f));

  // Global Clipboard Paste Listener (Ctrl+V / Cmd+V for screenshots)
  window.addEventListener('paste', (e) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile();
        if (file) {
          setCheckMode('screenshot');
          handleScreenshotUpload(file);
          break;
        }
      }
    }
  });
});
