"""Multi-language support (i18n) for NUWA-MLTB.

Provides a simple ``get_string(key, lang)`` lookup so any module can
grab a translated message by key.  Languages are stored as plain
Python dicts — no external files needed.

Supported languages:
  • en  – English (default / fallback)
  • hi  – Hindi
  • ar  – Arabic
  • id  – Indonesian
  • tr  – Turkish
  • pt  – Portuguese
  • bn  – Bengali
"""

from __future__ import annotations

from ... import LOGGER

# ── language data ──────────────────────────────────────────────────

_MESSAGES: dict[str, dict[str, str]] = {
    # ── English (master) ───────────────────────────────────────────
    "en": {
        # General
        "welcome": "👋 Welcome to <b>NUWA-MLTB</b>!\n\nUse /help to see all available commands.",
        "not_authorized": "⛔ You are not authorized to use this bot.",
        "task_cancelled": "✅ Task <code>{gid}</code> cancelled.",
        "task_not_found": "❌ Task not found.",
        "no_active_tasks": "📭 No active tasks!",
        "settings_reset": "♻️ Your settings have been reset.",

        # Download / Upload
        "download_starting": "⬇️ Download starting…",
        "download_complete": "✅ Download complete: <b>{name}</b> ({size})",
        "download_error": "❌ Download error: {error}",
        "upload_starting": "⬆️ Upload starting…",
        "upload_complete": "✅ Upload complete: <b>{name}</b> ({size})",
        "upload_error": "❌ Upload error: {error}",

        # Duplicate
        "dup_detected": "⚠️ <b>Duplicate detected!</b>\n\nThis file was already downloaded {age} ago.\nPath: <code>{path}</code>",

        # Task limits
        "bot_task_limit_reached": "⚠️ Bot task limit reached ({limit}). Please wait for a task to finish.",
        "user_task_limit_reached": "⚠️ Your task limit reached ({limit}). Please wait for your current tasks to finish.",
        "user_banned": "🚫 You have been banned from using this bot.\nReason: {reason}",

        # Ban / Unban
        "user_banned_success": "✅ User {user_id} has been banned.",
        "user_unbanned_success": "✅ User {user_id} has been unbanned.",
        "user_already_banned": "ℹ️ User {user_id} is already banned.",
        "user_not_banned": "ℹ️ User {user_id} is not banned.",

        # Analytics
        "analytics_title": "📊 <b>Bot Analytics</b>",
        "analytics_downloads": "Downloads: {count}",
        "analytics_uploads": "Uploads: {count}",
        "analytics_success_rate": "Success Rate: {rate}%",
    },

    # ── Hindi ──────────────────────────────────────────────────────
    "hi": {
        "welcome": "👋 <b>NUWA-MLTB</b> में आपका स्वागत है!\n\nसभी कमांड देखने के लिए /help का उपयोग करें।",
        "not_authorized": "⛔ आपको इस बॉट का उपयोग करने की अनुमति नहीं है।",
        "task_cancelled": "✅ टास्क <code>{gid}</code> रद्द कर दिया गया।",
        "task_not_found": "❌ टास्क नहीं मिला।",
        "no_active_tasks": "📭 कोई सक्रिय टास्क नहीं!",
        "settings_reset": "♻️ आपकी सेटिंग्स रीसेट कर दी गई हैं।",

        "download_starting": "⬇️ डाउनलोड शुरू हो रहा है…",
        "download_complete": "✅ डाउनलोड पूरा: <b>{name}</b> ({size})",
        "download_error": "❌ डाउनलोड त्रुटि: {error}",
        "upload_starting": "⬆️ अपलोड शुरू हो रहा है…",
        "upload_complete": "✅ अपलोड पूरा: <b>{name}</b> ({size})",
        "upload_error": "❌ अपलोड त्रुटि: {error}",

        "dup_detected": "⚠️ <b>डुप्लिकेट मिला!</b>\n\nयह फ़ाइल पहले ही {age} पहले डाउनलोड हो चुकी है।\nपथ: <code>{path}</code>",

        "bot_task_limit_reached": "⚠️ बॉट टास्क लिमिट पूरी हो गई ({limit})। कृपया किसी टास्क के खत्म होने का इंतज़ार करें।",
        "user_task_limit_reached": "⚠️ आपकी टास्क लिमिट पूरी हो गई ({limit})। कृपया अपने मौजूदा टास्क खत्म होने का इंतज़ार करें।",
        "user_banned": "🚫 आपको इस बॉट का उपयोग करने से प्रतिबंधित कर दिया गया है।\nकारण: {reason}",

        "user_banned_success": "✅ यूज़र {user_id} को बैन कर दिया गया।",
        "user_unbanned_success": "✅ यूज़र {user_id} को अनबैन कर दिया गया।",
        "user_already_banned": "ℹ️ यूज़र {user_id} पहले से बैन है।",
        "user_not_banned": "ℹ️ यूज़र {user_id} बैन नहीं है।",

        "analytics_title": "📊 <b>बॉट एनालिटिक्स</b>",
        "analytics_downloads": "डाउनलोड: {count}",
        "analytics_uploads": "अपलोड: {count}",
        "analytics_success_rate": "सफलता दर: {rate}%",
    },

    # ── Arabic ─────────────────────────────────────────────────────
    "ar": {
        "welcome": "👋 مرحباً بك في <b>NUWA-MLTB</b>!\n\nاستخدم /help لرؤية جميع الأوامر المتاحة.",
        "not_authorized": "⛔ غير مصرح لك باستخدام هذا البوت.",
        "task_cancelled": "✅ تم إلغاء المهمة <code>{gid}</code>.",
        "task_not_found": "❌ المهمة غير موجودة.",
        "no_active_tasks": "📭 لا توجد مهام نشطة!",
        "settings_reset": "♻️ تم إعادة تعيين إعداداتك.",

        "download_starting": "⬇️ جاري بدء التنزيل…",
        "download_complete": "✅ اكتمل التنزيل: <b>{name}</b> ({size})",
        "download_error": "❌ خطأ في التنزيل: {error}",
        "upload_starting": "⬆️ جاري بدء الرفع…",
        "upload_complete": "✅ اكتمل الرفع: <b>{name}</b> ({size})",
        "upload_error": "❌ خطأ في الرفع: {error}",

        "dup_detected": "⚠️ <b>تم اكتشاف ملف مكرر!</b>\n\nتم تنزيل هذا الملف بالفعل منذ {age}.\nالمسار: <code>{path}</code>",

        "bot_task_limit_reached": "⚠️ تم الوصول إلى حد مهام البوت ({limit}). يرجى الانتظار حتى تنتهي إحدى المهام.",
        "user_task_limit_reached": "⚠️ تم الوصول إلى حد مهامك ({limit}). يرجى الانتظار حتى تنتهي مهامك الحالية.",
        "user_banned": "🚫 تم حظرك من استخدام هذا البوت.\nالسبب: {reason}",

        "user_banned_success": "✅ تم حظر المستخدم {user_id}.",
        "user_unbanned_success": "✅ تم رفع الحظر عن المستخدم {user_id}.",
        "user_already_banned": "ℹ️ المستخدم {user_id} محظور بالفعل.",
        "user_not_banned": "ℹ️ المستخدم {user_id} غير محظور.",

        "analytics_title": "📊 <b>إحصائيات البوت</b>",
        "analytics_downloads": "التنزيلات: {count}",
        "analytics_uploads": "الرفع: {count}",
        "analytics_success_rate": "نسبة النجاح: {rate}%",
    },

    # ── Indonesian ─────────────────────────────────────────────────
    "id": {
        "welcome": "👋 Selamat datang di <b>NUWA-MLTB</b>!\n\nGunakan /help untuk melihat semua perintah.",
        "not_authorized": "⛔ Anda tidak diizinkan menggunakan bot ini.",
        "task_cancelled": "✅ Tugas <code>{gid}</code> dibatalkan.",
        "task_not_found": "❌ Tugas tidak ditemukan.",
        "no_active_tasks": "📭 Tidak ada tugas aktif!",
        "settings_reset": "♻️ Pengaturan Anda telah direset.",

        "download_starting": "⬇️ Memulai unduhan…",
        "download_complete": "✅ Unduhan selesai: <b>{name}</b> ({size})",
        "download_error": "❌ Kesalahan unduhan: {error}",
        "upload_starting": "⬆️ Memulai unggahan…",
        "upload_complete": "✅ Unggahan selesai: <b>{name}</b> ({size})",
        "upload_error": "❌ Kesalahan unggahan: {error}",

        "dup_detected": "⚠️ <b>Duplikat terdeteksi!</b>\n\nFile ini sudah diunduh {age} yang lalu.\nPath: <code>{path}</code>",

        "bot_task_limit_reached": "⚠️ Batas tugas bot tercapai ({limit}). Silakan tunggu hingga tugas selesai.",
        "user_task_limit_reached": "⚠️ Batas tugas Anda tercapai ({limit}). Silakan tunggu hingga tugas Anda selesai.",
        "user_banned": "🚫 Anda telah dilarang menggunakan bot ini.\nAlasan: {reason}",

        "user_banned_success": "✅ Pengguna {user_id} telah diblokir.",
        "user_unbanned_success": "✅ Pengguna {user_id} telah dibuka blokirnya.",
        "user_already_banned": "ℹ️ Pengguna {user_id} sudah diblokir.",
        "user_not_banned": "ℹ️ Pengguna {user_id} tidak diblokir.",

        "analytics_title": "📊 <b>Analitik Bot</b>",
        "analytics_downloads": "Unduhan: {count}",
        "analytics_uploads": "Unggahan: {count}",
        "analytics_success_rate": "Tingkat Keberhasilan: {rate}%",
    },

    # ── Turkish ────────────────────────────────────────────────────
    "tr": {
        "welcome": "👋 <b>NUWA-MLTB</b>'ye hoş geldiniz!\n\nTüm komutları görmek için /help kullanın.",
        "not_authorized": "⛔ Bu botu kullanmaya yetkiniz yok.",
        "task_cancelled": "✅ Görev <code>{gid}</code> iptal edildi.",
        "task_not_found": "❌ Görev bulunamadı.",
        "no_active_tasks": "📭 Aktif görev yok!",
        "settings_reset": "♻️ Ayarlarınız sıfırlandı.",

        "download_starting": "⬇️ İndirme başlıyor…",
        "download_complete": "✅ İndirme tamamlandı: <b>{name}</b> ({size})",
        "download_error": "❌ İndirme hatası: {error}",
        "upload_starting": "⬆️ Yükleme başlıyor…",
        "upload_complete": "✅ Yükleme tamamlandı: <b>{name}</b> ({size})",
        "upload_error": "❌ Yükleme hatası: {error}",

        "dup_detected": "⚠️ <b>Kopya algılandı!</b>\n\nBu dosya zaten {age} önce indirildi.\nYol: <code>{path}</code>",

        "bot_task_limit_reached": "⚠️ Bot görev limiti aşıldı ({limit}). Lütfen bir görevin bitmesini bekleyin.",
        "user_task_limit_reached": "⚠️ Görev limitiniz aşıldı ({limit}). Lütfen mevcut görevlerinizin bitmesini bekleyin.",
        "user_banned": "🚫 Bu botu kullanmanız yasaklandı.\nNeden: {reason}",

        "user_banned_success": "✅ Kullanıcı {user_id} yasaklandı.",
        "user_unbanned_success": "✅ Kullanıcı {user_id} yasağı kaldırıldı.",
        "user_already_banned": "ℹ️ Kullanıcı {user_id} zaten yasaklı.",
        "user_not_banned": "ℹ️ Kullanıcı {user_id} yasaklı değil.",

        "analytics_title": "📊 <b>Bot Analitikleri</b>",
        "analytics_downloads": "İndirmeler: {count}",
        "analytics_uploads": "Yüklemeler: {count}",
        "analytics_success_rate": "Başarı Oranı: {rate}%",
    },

    # ── Portuguese ─────────────────────────────────────────────────
    "pt": {
        "welcome": "👋 Bem-vindo ao <b>NUWA-MLTB</b>!\n\nUse /help para ver todos os comandos disponíveis.",
        "not_authorized": "⛔ Você não está autorizado a usar este bot.",
        "task_cancelled": "✅ Tarefa <code>{gid}</code> cancelada.",
        "task_not_found": "❌ Tarefa não encontrada.",
        "no_active_tasks": "📭 Nenhuma tarefa ativa!",
        "settings_reset": "♻️ Suas configurações foram redefinidas.",

        "download_starting": "⬇️ Iniciando download…",
        "download_complete": "✅ Download concluído: <b>{name}</b> ({size})",
        "download_error": "❌ Erro no download: {error}",
        "upload_starting": "⬆️ Iniciando upload…",
        "upload_complete": "✅ Upload concluído: <b>{name}</b> ({size})",
        "upload_error": "❌ Erro no upload: {error}",

        "dup_detected": "⚠️ <b>Duplicata detectada!</b>\n\nEste arquivo já foi baixado há {age}.\nCaminho: <code>{path}</code>",

        "bot_task_limit_reached": "⚠️ Limite de tarefas do bot atingido ({limit}). Aguarde uma tarefa terminar.",
        "user_task_limit_reached": "⚠️ Seu limite de tarefas atingido ({limit}). Aguarde suas tarefas atuais terminarem.",
        "user_banned": "🚫 Você foi banido de usar este bot.\nMotivo: {reason}",

        "user_banned_success": "✅ Usuário {user_id} foi banido.",
        "user_unbanned_success": "✅ Usuário {user_id} foi desbanido.",
        "user_already_banned": "ℹ️ Usuário {user_id} já está banido.",
        "user_not_banned": "ℹ️ Usuário {user_id} não está banido.",

        "analytics_title": "📊 <b>Análises do Bot</b>",
        "analytics_downloads": "Downloads: {count}",
        "analytics_uploads": "Uploads: {count}",
        "analytics_success_rate": "Taxa de Sucesso: {rate}%",
    },

    # ── Bengali ────────────────────────────────────────────────────
    "bn": {
        "welcome": "👋 <b>NUWA-MLTB</b>-তে স্বাগতম!\n\nসমস্ত কমান্ড দেখতে /help ব্যবহার করুন।",
        "not_authorized": "⛔ আপনি এই বট ব্যবহারের অনুমোদিত নন।",
        "task_cancelled": "✅ টাস্ক <code>{gid}</code> বাতিল করা হয়েছে।",
        "task_not_found": "❌ টাস্ক পাওয়া যায়নি।",
        "no_active_tasks": "📭 কোনো সক্রিয় টাস্ক নেই!",
        "settings_reset": "♻️ আপনার সেটিংস রিসেট করা হয়েছে।",

        "download_starting": "⬇️ ডাউনলোড শুরু হচ্ছে…",
        "download_complete": "✅ ডাউনলোড সম্পন্ন: <b>{name}</b> ({size})",
        "download_error": "❌ ডাউনলোড ত্রুটি: {error}",
        "upload_starting": "⬆️ আপলোড শুরু হচ্ছে…",
        "upload_complete": "✅ আপলোড সম্পন্ন: <b>{name}</b> ({size})",
        "upload_error": "❌ আপলোড ত্রুটি: {error}",

        "dup_detected": "⚠️ <b>ডুপ্লিকেট সনাক্ত হয়েছে!</b>\n\nএই ফাইলটি ইতিমধ্যে {age} আগে ডাউনলোড হয়েছে।\nপথ: <code>{path}</code>",

        "bot_task_limit_reached": "⚠️ বট টাস্ক লিমিট পূর্ণ ({limit})। অনুগ্রহ করে একটি টাস্ক শেষ হওয়ার জন্য অপেক্ষা করুন।",
        "user_task_limit_reached": "⚠️ আপনার টাস্ক লিমিট পূর্ণ ({limit})। অনুগ্রহ করে আপনার বর্তমান টাস্ক শেষ হওয়ার জন্য অপেক্ষা করুন।",
        "user_banned": "🚫 আপনাকে এই বট ব্যবহার থেকে নিষেধ করা হয়েছে।\nকারণ: {reason}",

        "user_banned_success": "✅ ব্যবহারকারী {user_id} কে নিষেধ করা হয়েছে।",
        "user_unbanned_success": "✅ ব্যবহারকারী {user_id} এর নিষেধাজ্ঞা তুলে নেওয়া হয়েছে।",
        "user_already_banned": "ℹ️ ব্যবহারকারী {user_id} ইতিমধ্যে নিষিদ্ধ।",
        "user_not_banned": "ℹ️ ব্যবহারকারী {user_id} নিষিদ্ধ নয়।",

        "analytics_title": "📊 <b>বট বিশ্লেষণ</b>",
        "analytics_downloads": "ডাউনলোড: {count}",
        "analytics_uploads": "আপলোড: {count}",
        "analytics_success_rate": "সফলতার হার: {rate}%",
    },
}

# ── public API ─────────────────────────────────────────────────────

# Allowed language codes
SUPPORTED_LANGUAGES: list[str] = list(_MESSAGES.keys())
DEFAULT_LANGUAGE = "en"


def get_string(key: str, lang: str = "", **kwargs) -> str:
    """Return the translated string for *key* in *lang*.

    Falls back to English if the key or language is missing.
    Extra *kwargs* are ``str.format()``-ed into the result.
    """
    lang = (lang or DEFAULT_LANGUAGE).lower().strip()
    lang_dict = _MESSAGES.get(lang, _MESSAGES[DEFAULT_LANGUAGE])
    template = lang_dict.get(key) or _MESSAGES[DEFAULT_LANGUAGE].get(key, key)
    try:
        return template.format(**kwargs) if kwargs else template
    except (KeyError, IndexError):
        return template