from ..telegram_helper.bot_commands import BotCommands
from ...core.nuwa_client import TgClient

mirror = """<b>Kirim link bareng sama perintahnya atau</b>

/cmd link

<b>Dengan cara reply ke link/file</b>:

/cmd -n nama baru -e -up tujuan upload

<b>CATATAN:</b>
1. Perintah yang mulai dengan <b>qb</b> CUMA buat torrent doang."""

yt = """<b>Kirim link bareng sama perintahnya</b>:

/cmd link
<b>Dengan cara reply ke link</b>:
/cmd -n nama baru -z password -opt x:y|x1:y1

Cek semua <a href='https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md'>SITUS</a> yang didukung di sini
Cek semua opsi yt-dlp dari <a href='https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L212'>FILE</a> ini atau pake <a href='https://t.me/mltb_official_channel/177'>script</a> ini buat ubah argumen CLI ke opsi API."""

clone = """Kirim link Gdrive|Gdot|Filepress|Filebee|Appdrive|Gdflix atau path rclone bareng perintah atau dengan reply ke link/rc_path pake perintah.
Pake -sync buat pake metode sync di rclone. Contoh: /cmd rcl/rclone_path -up rcl/rclone_path/rc -sync"""

new_name = """<b>Nama Baru</b>: -n

/cmd link -n nama baru
Catatan: Ga bisa buat torrent"""

multi_link = """<b>Multiple link cuma bisa dengan reply ke link/file pertama</b>: -i

/cmd -i 10(jumlah link/file)"""

same_dir = """<b>Pindahin file/folder ke folder baru</b>: -m

Lo juga bisa pake argumen ini buat pindahin beberapa konten link/torrent ke direktori yang sama, jadi semua link bakal diupload bersamaan sebagai satu tugas

/cmd link -m folder baru (cuma satu link di dalam folder baru)
/cmd -i 10(jumlah link/file) -m nama folder (semua konten link dalam satu folder)
/cmd -b -m nama folder (reply ke kumpulan pesan/file (setiap link di baris baru))

Pas pake bulk, lo juga bisa pake argumen ini dengan nama folder yang beda bareng sama link di pesan atau file batch
Contoh:
link1 -m folder1
link2 -m folder1
link3 -m folder2
link4 -m folder2
link5 -m folder3
link6
jadi konten link1 dan link2 bakal diupload dari folder yang sama yaitu folder1
konten link3 dan link4 bakal diupload dari folder yang sama juga yaitu folder2
link5 bakal diupload sendiri di dalam folder baru namanya folder3
link6 bakal diupload biasa sendiri
"""

thumb = """<b>Thumbnail untuk task sekarang</b>: -t

/cmd link -t link-pesan-tg (dokumen atau foto) atau none (file tanpa thumb)"""

split_size = """<b>Ukuran split untuk task sekarang</b>: -sp

/cmd link -sp (500mb atau 2gb atau 4000000000)
Catatan: Cuma mb sama gb yang didukung atau tulis dalam bytes tanpa satuan!"""

upload = """<b>Tujuan Upload</b>: -up

/cmd link -up rcl/gdl (rcl: buat pilih config rclone, remote & path | gdl: Buat pilih token.pickle, id gdrive) pake tombol
Lo bisa langsung tambahin path upload: -up remote:dir/subdir atau -up Gdrive_id atau -up id/username (telegram) atau -up id/username|topic_id (telegram)
Kalo DEFAULT_UPLOAD itu `rc` maka lo bisa kasih up: `gd` buat upload pake tools gdrive ke GDRIVE_ID.
Kalo DEFAULT_UPLOAD itu `gd` maka lo bisa kasih up: `rc` buat upload ke RCLONE_PATH.

Kalo mau nambahin path atau gdrive manual dari config/token lo (DIUPLOAD DARI USER SETTING) tambahin mrcc: buat rclone dan mtp: sebelum path/gdrive_id tanpa spasi.
/cmd link -up mrcc:main:dump atau -up mtp:gdrive_id <strong>atau lo bisa langsung edit upload pake token/config owner/user dari user setting tanpa nambahin mtp: atau mrcc: sebelum path upload/id</strong>

Buat nambahin tujuan leech:
-up id/@username/pm
-up b:id/@username/pm (b: artinya leech oleh bot) (id atau username chat atau tulis pm artinya private message jadi bot bakal kirim file secara private ke lo)
kapan lo harus pake b:(leech oleh bot)? Pas setting default lo adalah leech oleh user dan lo mau leech oleh bot untuk task tertentu.
-up u:id/@username(u: artinya leech oleh user) Ini kalo OWNER nambahin USER_STRING_SESSION.
-up h:id/@username(leech hybrid) h: buat upload file oleh bot dan user berdasarkan ukuran file.
-up id/@username|topic_id(leech di chat dan topic tertentu) tambahin | tanpa spasi dan tulis topic id setelah chat id atau username.

Kalo lo mau tentuin pake token.pickle atau service accounts, lo bisa tambahin tp:gdrive_id (pake token.pickle) atau sa:gdrive_id (pake service accounts) atau mtp:gdrive_id (pake token.pickle yang diupload dari user setting).
DEFAULT_UPLOAD ga ngaruh ke command leech.
"""

user_download = """<b>Download User</b>: link

/cmd tp:link buat download pake token.pickle owner kalo service account aktif.
/cmd sa:link buat download pake service account kalo service account nonaktif.
/cmd tp:gdrive_id buat download pake token.pickle dan file_id kalo service account aktif.
/cmd sa:gdrive_id buat download pake service account dan file_id kalo service account nonaktif.
/cmd mtp:gdrive_id atau mtp:link buat download pake token.pickle user yang diupload dari user setting
/cmd mrcc:remote:path buat download pake config rclone user yang diupload dari user setting
lo bisa langsung edit upload pake token/config owner/user dari user setting tanpa nambahin mtp: atau mrcc: sebelum path/id"""

rcf = """<b>Rclone Flags</b>: -rcf

/cmd link|path|rcl -up path|rcl -rcf --buffer-size:8M|--drive-starred-only|key|key:value
Ini bakal timpa semua flags lain kecuali --exclude
Cek semua <a href='https://rclone.org/flags/'>RcloneFlags</a> di sini."""

bulk = """<b>Bulk Download</b>: -b

Bulk cuma bisa dipake dengan reply ke pesan teks atau file teks yang berisi link yang dipisah oleh baris baru.
Contoh:
link1 -n nama baru -up remote1:path1 -rcf |key:value|key:value
link2 -z -n nama baru -up remote2:path2
link3 -e -n nama baru -up remote2:path2
Reply contoh ini pake command -> /cmd -b(bulk)

Catatan: Argumen apapun yang bareng sama command bakal diset ke semua link
/cmd -b -up remote: -z -m nama folder (semua konten link dalam satu folder ter-zip yang diupload ke satu tujuan)
jadi lo ga bisa set tujuan upload yang beda bareng sama link kalo lo udah nambahin -m bareng sama command
Lo bisa set mulai dan akhir link dari bulk kayak seed, dengan -b start:end atau cuma end pake -b :end atau cuma start pake -b start.
Default start itu dari nol (link pertama) sampai tak terbatas."""

rlone_dl = """<b>Download Rclone</b>:

Anggep path rclone persis kayak link
/cmd main:dump/ubuntu.iso atau rcl(Buat pilih config, remote dan path)
User bisa nambahin rclone mereka sendiri dari user settings
Kalo mau nambahin path manual dari config lo tambahin mrcc: sebelum path tanpa spasi
/cmd mrcc:main:dump/ubuntu.iso
Lo bisa langsung edit pake config owner/user dari user setting tanpa nambahin mrcc: sebelum path"""

extract_zip = """<b>Extract/Zip</b>: -e -z

/cmd link -e password (extract yang dipassword)
/cmd link -z password (zip yang dipassword)
/cmd link -z password -e (extract dan zip yang dipassword)
Catatan: Pas extract dan zip dua-duanya ditambahin sama command, dia bakal extract dulu baru zip, jadi selalu extract dulu"""

join = """<b>Gabung File yang Terpisah</b>: -j

Opsi ini cuma bakal kerja sebelum extract dan zip, jadi kebanyakan dipake sama argumen -m (samedir)
Dengan Reply:
/cmd -i 3 -j -m nama folder
/cmd -b -j -m nama folder
kalo lo punya link (folder) yang ada file terpisah:
/cmd link -j"""

tg_links = """<b>Link TG</b>:

Anggep link kayak link langsung
Beberapa link butuh akses user jadi lo harus nambahin USER_SESSION_STRING buat itu.
Tiga jenis link:
Public: https://t.me/nama_channel/id_pesan
Private: tg://openmessage?user_id=xxxxxx&message_id=xxxxx
Super: https://t.me/c/id_channel/id_pesan
Range: https://t.me/nama_channel/id_pesan_pertama-id_pesan_terakhir
Contoh Range: tg://openmessage?user_id=xxxxxx&message_id=555-560 atau https://t.me/nama_channel/100-150
Catatan: Link range cuma bakal kerja dengan reply command ke situ"""

sample_video = """<b>Sample Video</b>: -sv

Buat sample video untuk satu video atau folder video.
/cmd -sv (dia bakal ambil nilai default yaitu durasi sample 60 detik dan durasi bagian 4 detik).
Lo bisa kontrol nilai-nilai itu. Contoh: /cmd -sv 70:5(durasi-sample:durasi-bagian) atau /cmd -sv :5 atau /cmd -sv 70."""

screenshot = """<b>Screenshot</b>: -ss

Buat screenshot untuk satu video atau folder video.
/cmd -ss (dia bakal ambil nilai default yaitu 10 foto).
Lo bisa kontrol nilai ini. Contoh: /cmd -ss 6."""

seed = """<b>Bittorrent seed</b>: -d

/cmd link -d ratio:seed_time atau dengan reply ke file/link
Buat tentuin ratio dan seed time tambahin -d ratio:time.
Contoh: -d 0.7:10 (ratio dan time) atau -d 0.7 (cuma ratio) atau -d :10 (cuma time) dimana time dalam menit"""

zip_arg = """<b>Zip</b>: -z password

/cmd link -z (zip)
/cmd link -z password (zip yang dipassword)"""

qual = """<b>Tombol Kualitas</b>: -s

Kalo kualitas default udah ditambahin dari opsi yt-dlp pake opsi format dan lo perlu pilih kualitas untuk link tertentu atau link dengan fitur multi link.
/cmd link -s"""

yt_opt = """<b>Opsi</b>: -opt

/cmd link -opt {"format": "bv*+mergeall[vcodec=none]", "nocheckcertificate": True, "playliststart": 10, "fragment_retries": float("inf"), "matchtitle": "S13", "writesubtitles": True, "live_from_start": True, "postprocessor_args": {"ffmpeg": ["-threads", "4"]}, "wait_for_video": (5, 100), "download_ranges": [{"start_time": 0, "end_time": 10}]}

Cek semua opsi API yt-dlp dari <a href='https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L184'>FILE</a> ini atau pake <a href='https://t.me/mltb_official_channel/177'>script</a> ini buat ubah argumen CLI ke opsi API."""

convert_media = """<b>Convert Media</b>: -ca -cv
/cmd link -ca mp3 -cv mp4 (convert semua audio ke mp3 dan semua video ke mp4)
/cmd link -ca mp3 (convert semua audio ke mp3)
/cmd link -cv mp4 (convert semua video ke mp4)
/cmd link -ca mp3 + flac ogg (convert cuma audio flac dan ogg ke mp3)
/cmd link -cv mkv - webm flv (convert semua video ke mp4 kecuali webm dan flv)"""

force_start = """<b>Force Start</b>: -f -fd -fu
/cmd link -f (paksa download dan upload)
/cmd link -fd (paksa download aja)
/cmd link -fu (paksa upload langsung setelah download selesai)"""

gdrive = """<b>Gdrive</b>: link
Kalo DEFAULT_UPLOAD itu `rc` maka lo bisa kasih up: `gd` buat upload pake tools gdrive ke GDRIVE_ID.
/cmd linkGdrive atau gdl atau idGdrive -up gdl atau idGdrive atau gd
/cmd tp:linkGdrive atau tp:idGdrive -up tp:idGdrive atau gdl atau gd (buat pake token.pickle kalo service account aktif)
/cmd sa:linkGdrive atau sa:idGdrive -p sa:idGdrive atau gdl atau gd (buat pake service account kalo service account nonaktif)
/cmd mtp:linkGdrive atau mtp:idGdrive -up mtp:idGdrive atau gdl atau gd(kalo lo udah nambahin idGdrive upload dari user setting) (buat pake token.pickle user yang diupload dari user setting)
Lo bisa langsung edit pake token owner/user dari user setting tanpa nambahin mtp: sebelum id"""

rclone_cl = """<b>Rclone</b>: path
Kalo DEFAULT_UPLOAD itu `gd` maka lo bisa kasih up: `rc` buat upload ke RCLONE_PATH.
/cmd rcl/rclone_path -up rcl/rclone_path/rc -rcf flagkey:flagvalue|flagkey|flagkey:flagvalue
/cmd rcl atau rclone_path -up rclone_path atau rc atau rcl
/cmd mrcc:rclone_path -up rcl atau rc(kalo lo udah nambahin rclone path dari user setting) (buat pake config user)
Lo bisa langsung edit pake config owner/user dari user setting tanpa nambahin mrcc: sebelum path"""

name_sub = r"""<b>Ganti Nama</b>: -ns
/cmd link -ns script/code/s | mirror/leech | tea/ /s | clone | cpu/ | \[mltb\]/mltb | \\text\\/text/s
Ini bakal pengaruhin semua file. Format: kataYangDiganti/kataPengganti/caseSensitive
Ganti Kata. Lo bisa nambahin pattern daripada teks biasa. Timeout: 60 detik
CATATAN: Lo harus nambahin \ sebelum karakter apa pun, ini karakternya: \^$.|?*+()[]{}-
1. script bakal diganti sama code dengan case sensitive
2. mirror bakal diganti sama leech
4. tea bakal diganti sama spasi dengan case sensitive
5. clone bakal dihapus
6. cpu bakal diganti sama spasi
7. [mltb] bakal diganti sama mltb
8. \text\ bakal diganti sama text dengan case sensitive
"""

transmission = """<b>Transmisi Tg</b>: -hl -ut -bt
/cmd link -hl (leech oleh session user dan bot berdasarkan ukuran) (Leech Hybrid)
/cmd link -bt (leech oleh session bot)
/cmd link -ut (leech oleh user)"""

thumbnail_layout = """Layout Thumbnail: -tl
/cmd link -tl 3x3 (lebarxtinggi) 3 foto dalam baris dan 3 foto dalam kolom"""

leech_as = """<b>Leech sebagai</b>: -doc -med
/cmd link -doc (Leech sebagai dokumen)
/cmd link -med (Leech sebagai media)"""

ffmpeg_cmds = """<b>Perintah FFmpeg</b>: -ff
list dari list perintah ffmpeg. Lo bisa set beberapa perintah ffmpeg untuk semua file sebelum upload. Jangan tulis ffmpeg di awal, mulai langsung sama argumennya.
Catatan:
1. Tambahin <code>-del</code> ke list yang lo mau bot hapus file aslinya setelah perintah selesai dijalanin!
3. Buat jalanin salah satu list yang udah ditambahin di bot kayak: ({"subtitle": ["-i mltb.mkv -c copy -c:s srt mltb.mkv"]}), lo harus pake -ff subtitle (key list)
Contoh: ["-i mltb.mkv -c copy -c:s srt mltb.mkv", "-i mltb.video -c copy -c:s srt mltb", "-i mltb.m4a -c:a libmp3lame -q:a 2 mltb.mp3", "-i mltb.audio -c:a libmp3lame -q:a 2 mltb.mp3", "-i mltb -map 0:a -c copy mltb.mka -map 0:s -c copy mltb.srt", "-i mltb -i tg://openmessage?user_id=5272663208&message_id=322801 -filter_complex 'overlay=W-w-10:H-h-10' -c:a copy mltb"]
Sini gue jelasin cara pake mltb.* yang referensi ke file yang lo mau kerjain.
1. Perintah pertama: inputnya mltb.mkv jadi perintah ini cuma bakal kerja di video mkv dan outputnya juga mltb.mkv jadi semua output adalah mkv. -del bakal hapus media asli setelah perintah selesai dijalanin.
2. Perintah kedua: inputnya mltb.video jadi perintah ini bakal kerja di semua video dan outputnya cuma mltb jadi ekstensinya sama kayak file input.
3. Perintah ketiga: inputnya mltb.m4a jadi perintah ini cuma bakal kerja di audio m4a dan outputnya mltb.mp3 jadi ekstensi output adalah mp3.
4. Perintah keempat: inputnya mltb.audio jadi perintah ini bakal kerja di semua audio dan outputnya mltb.mp3 jadi ekstensi output adalah mp3.
5. Perintah kelima: Lo bisa nambahin link telegram untuk input ukuran kecil kayak foto buat set watermark"""

YT_HELP_DICT = {
    "main": yt,
    "New-Name": f"{new_name}\nCatatan: Jangan nambahin ekstensi file",
    "Zip": zip_arg,
    "Quality": qual,
    "Options": yt_opt,
    "Multi-Link": multi_link,
    "Same-Directory": same_dir,
    "Thumb": thumb,
    "Split-Size": split_size,
    "Upload-Destination": upload,
    "Rclone-Flags": rcf,
    "Bulk": bulk,
    "Sample-Video": sample_video,
    "Screenshot": screenshot,
    "Convert-Media": convert_media,
    "Force-Start": force_start,
    "Name-Substitute": name_sub,
    "TG-Transmission": transmission,
    "Thumb-Layout": thumbnail_layout,
    "Leech-Type": leech_as,
    "FFmpeg-Cmds": ffmpeg_cmds,
}

MIRROR_HELP_DICT = {
    "main": mirror,
    "New-Name": new_name,
    "DL-Auth": "<b>Otorisasi link langsung</b>: -au -ap\n\n/cmd link -au username -ap password",
    "Headers": "<b>Header kustom link langsung</b>: -h\n\n/cmd link -h key:value|key1:value1",
    "Extract/Zip": extract_zip,
    "Select-Files": "<b>Pemilihan File Bittorrent/JDownloader/Sabnzbd</b>: -s\n\n/cmd link -s atau dengan reply ke file/link",
    "Torrent-Seed": seed,
    "Multi-Link": multi_link,
    "Same-Directory": same_dir,
    "Thumb": thumb,
    "Split-Size": split_size,
    "Upload-Destination": upload,
    "Rclone-Flags": rcf,
    "Bulk": bulk,
    "Join": join,
    "Rclone-DL": rlone_dl,
    "Tg-Links": tg_links,
    "Sample-Video": sample_video,
    "Screenshot": screenshot,
    "Convert-Media": convert_media,
    "Force-Start": force_start,
    "User-Download": user_download,
    "Name-Substitute": name_sub,
    "TG-Transmission": transmission,
    "Thumb-Layout": thumbnail_layout,
    "Leech-Type": leech_as,
    "FFmpeg-Cmds": ffmpeg_cmds,
}

CLONE_HELP_DICT = {
    "main": clone,
    "Multi-Link": multi_link,
    "Bulk": bulk,
    "Gdrive": gdrive,
    "Rclone": rclone_cl,
}

RSS_HELP_MESSAGE = """
Pake format ini buat nambahin feed url:
Judul1 link (wajib)
Judul2 link -c cmd -inf xx -exf xx
Judul3 link -c cmd -d ratio:time -z password

-c command -up mrcc:remote:path/subdir -rcf --buffer-size:8M|key|key:value
-inf Buat filter kata yang termasuk.
-exf Buat filter kata yang dikecualikan.
-stv true atau false (filter sensitif)

Contoh: Judul https://www.rss-url.com -inf 1080 or 720 or 144p|mkv or mp4|hevc -exf flv or web|xxx
Filter ini bakal parse link yang judulnya mengandung `(1080 or 720 or 144p) and (mkv or mp4) and hevc` dan ga mengandung kata (flv or web) dan xxx. Lo bisa nambahin apa aja yang lo mau.

Contoh lain: -inf  1080  or 720p|.web. or .webrip.|hvec or x264. Ini bakal parse judul yang mengandung ( 1080  or 720p) and (.web. or .webrip.) and (hvec or x264). Gue udah nambahin spasi sebelum dan sesudah 1080 buat hindari salah match. Kalo angka `10805695` ini ada di judul, dia bakal match 1080 kalo ditambahin 1080 tanpa spasi setelahnya.

Catatan Filter:
1. | artinya dan.
2. Tambahin `or` antara key yang mirip, lo bisa nambahin antara kualitas atau antara ekstensi, jadi jangan tambahin filter kayak gini f: 1080|mp4 or 720|web karena ini bakal parse 1080 and (mp4 or 720) and web ... bukan (1080 and mp4) or (720 and web).
3. Lo bisa nambahin `or` dan `|` sebanyak yang lo mau.
4. Liat judulnya kalo ada karakter khusus statis setelah atau sebelum kualitas atau ekstensi atau apa pun dan pake mereka di filter buat hindari salah match.
Timeout: 60 detik.
"""

PASSWORD_ERROR_MESSAGE = """
<b>Link ini butuh password!</b>
- Sisipin <b>::</b> setelah link dan tulis password setelah tanda itu.

<b>Contoh:</b> link::password gue
"""

user_settings_text = {
    "LEECH_SPLIT_SIZE": f"Kirim ukuran split Leech dalam bytes atau pake gb atau mb. Contoh: 40000000 atau 2.5gb atau 1000mb. IS_PREMIUM_USER: {TgClient.IS_PREMIUM_USER}. Timeout: 60 detik",
    "LEECH_DUMP_CHAT": """"Kirim ID/USERNAME/PM tujuan leech. 
* b:id/@username/pm (b: artinya leech oleh bot) (id atau username chat atau tulis pm artinya private message jadi bot bakal kirim file secara private ke lo) kapan lo harus pake b:(leech oleh bot)? Pas setting default lo adalah leech oleh user dan lo mau leech oleh bot untuk task tertentu.
* u:id/@username(u: artinya leech oleh user) Ini kalo OWNER nambahin USER_STRING_SESSION.
* h:id/@username(leech hybrid) h: buat upload file oleh bot dan user berdasarkan ukuran file.
* id/@username|topic_id(leech di chat dan topic tertentu) tambahin | tanpa spasi dan tulis topic id setelah chat id atau username. Timeout: 60 detik""",
    "LEECH_FILENAME_PREFIX": r"Kirim Awalan Nama File Leech. Lo bisa nambahin tag HTML. Contoh: <code>@channelgue</code>. Timeout: 60 detik",
    "THUMBNAIL_LAYOUT": "Kirim layout thumbnail (lebarxtinggi, 2x2, 3x3, 2x4, 4x4, ...). Contoh: 3x3. Timeout: 60 detik",
    "RCLONE_PATH": "Kirim Path Rclone. Kalo mau pake config rclone lo, edit pake config owner/user dari user setting atau tambahin mrcc: sebelum path rclone. Contoh mrcc:remote:folder. Timeout: 60 detik",
    "RCLONE_FLAGS": "key:value|key|key|key:value . Cek semua <a href='https://rclone.org/flags/'>RcloneFlags</a> di sini\nContoh: --buffer-size:8M|--drive-starred-only",
    "GDRIVE_ID": "Kirim ID Gdrive. Kalo mau pake token.pickle lo, edit pake token owner/user dari user setting atau tambahin mtp: sebelum id. Contoh: mtp:F435RGGRDXXXXXX . Timeout: 60 detik",
    "INDEX_URL": "Kirim Index URL. Timeout: 60 detik",
    "UPLOAD_PATHS": "Kirim Dict dari key yang punya nilai path. Contoh: {'path 1': 'remote:folder_rclone', 'path 2': 'id_gdrive1', 'path 3': 'id_chat_tg', 'path 4': 'mrcc:remote:', 'path 5': b:@username} . Timeout: 60 detik",
    "EXCLUDED_EXTENSIONS": "Kirim ekstensi yang dikecualikan dipisah spasi tanpa titik di awal. Timeout: 60 detik",
    "NAME_SUBSTITUTE": r"""Ganti Kata. Lo bisa nambahin pattern daripada teks biasa. Timeout: 60 detik
CATATAN: Lo harus nambahin \ sebelum karakter apa pun, ini karakternya: \^$.|?*+()[]{}-
Contoh: script/code/s | mirror/leech | tea/ /s | clone | cpu/ | \[mltb\]/mltb | \\text\\/text/s
1. script bakal diganti sama code dengan case sensitive
2. mirror bakal diganti sama leech
4. tea bakal diganti sama spasi dengan case sensitive
5. clone bakal dihapus
6. cpu bakal diganti sama spasi
7. [mltb] bakal diganti sama mltb
8. \text\ bakal diganti sama text dengan case sensitive
""",
    "YT_DLP_OPTIONS": """Kirim dict dari YT-DLP Options. Timeout: 60 detik
Format: {key: value, key: value, key: value}.
Contoh: {"format": "bv*+mergeall[vcodec=none]", "nocheckcertificate": True, "playliststart": 10, "fragment_retries": float("inf"), "matchtitle": "S13", "writesubtitles": True, "live_from_start": True, "postprocessor_args": {"ffmpeg": ["-threads", "4"]}, "wait_for_video": (5, 100), "download_ranges": [{"start_time": 0, "end_time": 10}]}
Cek semua opsi API yt-dlp dari <a href='https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L184'>FILE</a> ini atau pake <a href='https://t.me/mltb_official_channel/177'>script</a> ini buat ubah argumen CLI ke opsi API.""",
    "FFMPEG_CMDS": """Dict dari nilai list perintah ffmpeg. Lo bisa set beberapa perintah ffmpeg untuk semua file sebelum upload. Jangan tulis ffmpeg di awal, mulai langsung sama argumennya.
Contoh: {"subtitle": ["-i mltb.mkv -c copy -c:s srt mltb.mkv", "-i mltb.video -c copy -c:s srt mltb"], "convert": ["-i mltb.m4a -c:a libmp3lame -q:a 2 mltb.mp3", "-i mltb.audio -c:a libmp3lame -q:a 2 mltb.mp3"], "extract": ["-i mltb -map 0:a -c copy mltb.mka -map 0:s -c copy mltb.srt"], "metadata": ["-i mltb.mkv -map 0 -map -0:v:1 -map -0:s -map 0:s:0 -map -0:v:m:attachment -c copy -metadata:s:v:0 title={title} -metadata:s:a:0 title={title} -metadata:s:a:1 title={title2} -metadata:s:a:2 title={title2} -c:s srt -metadata:s:s:0 title={title3} mltb -y -del"], "watermark": ["-i mltb -i tg://openmessage?user_id=5272663208&message_id=322801 -filter_complex 'overlay=W-w-10:H-h-10' -c:a copy mltb"]}
Catatan:
- Tambahin `-del` ke list yang lo mau bot hapus file aslinya setelah perintah selesai dijalanin!
- Buat jalanin salah satu list itu di bot contohnya, lo harus pake -ff subtitle (key list) atau -ff convert (key list)
Sini gue jelasin cara pake mltb.* yang referensi ke file yang lo mau kerjain.
1. Perintah pertama: inputnya mltb.mkv jadi perintah ini cuma bakal kerja di video mkv dan outputnya juga mltb.mkv jadi semua output adalah mkv. -del bakal hapus media asli setelah perintah selesai dijalanin.
2. Perintah kedua: inputnya mltb.video jadi perintah ini bakal kerja di semua video dan outputnya cuma mltb jadi ekstensinya sama kayak file input.
3. Perintah ketiga: inputnya mltb.m4a jadi perintah ini cuma bakal kerja di audio m4a dan outputnya mltb.mp3 jadi ekstensi output adalah mp3.
4. Perintah keempat: inputnya mltb.audio jadi perintah ini bakal kerja di semua audio dan outputnya mltb.mp3 jadi ekstensi output adalah mp3.
5. Variabel FFmpeg di perintah terakhir yang metadata ({title}, {title2}, dll...), lo bisa edit mereka di user setting
6. Link telegram untuk input ukuran kecil kayak foto buat set watermark.""",
}


help_string = f"""
CATATAN: Coba setiap command tanpa argumen apa pun buat liat detail lebih lanjut.
/{BotCommands.MirrorCommand[0]} atau /{BotCommands.MirrorCommand[1]}: Mulai mirroring ke cloud.
/{BotCommands.QbMirrorCommand[0]} atau /{BotCommands.QbMirrorCommand[1]}: Mulai Mirroring ke cloud pake qBittorrent.
/{BotCommands.JdMirrorCommand[0]} atau /{BotCommands.JdMirrorCommand[1]}: Mulai Mirroring ke cloud pake JDownloader.
/{BotCommands.NzbMirrorCommand[0]} atau /{BotCommands.NzbMirrorCommand[1]}: Mulai Mirroring ke cloud pake Sabnzbd.
/{BotCommands.YtdlCommand[0]} atau /{BotCommands.YtdlCommand[1]}: Mirror link yang didukung yt-dlp.
/{BotCommands.LeechCommand[0]} atau /{BotCommands.LeechCommand[1]}: Mulai leeching ke Telegram.
/{BotCommands.QbLeechCommand[0]} atau /{BotCommands.QbLeechCommand[1]}: Mulai leeching pake qBittorrent.
/{BotCommands.JdLeechCommand[0]} atau /{BotCommands.JdLeechCommand[1]}: Mulai leeching pake JDownloader.
/{BotCommands.NzbLeechCommand[0]} atau /{BotCommands.NzbLeechCommand[1]}: Mulai leeching pake Sabnzbd.
/{BotCommands.YtdlLeechCommand[0]} atau /{BotCommands.YtdlLeechCommand[1]}: Leech link yang didukung yt-dlp.
/{BotCommands.CloneCommand} [drive_url]: Copy file/folder ke Google Drive.
/{BotCommands.CountCommand} [drive_url]: Hitung file/folder dari Google Drive.
/{BotCommands.DeleteCommand} [drive_url]: Hapus file/folder dari Google Drive (Cuma Owner & Sudo).
/{BotCommands.UserSetCommand[0]} atau /{BotCommands.UserSetCommand[1]} [query]: Pengaturan User.
/{BotCommands.BotSetCommand[0]} atau /{BotCommands.BotSetCommand[1]} [query]: Pengaturan Bot.
/{BotCommands.SelectCommand}: Pilih file dari torrents atau nzb oleh gid atau reply.
/{BotCommands.CancelTaskCommand[0]} atau /{BotCommands.CancelTaskCommand[1]} [gid]: Batalkan task oleh gid atau reply.
/{BotCommands.ForceStartCommand[0]} atau /{BotCommands.ForceStartCommand[1]} [gid]: Paksa mulai task oleh gid atau reply.
/{BotCommands.CancelAllCommand} [query]: Batalkan semua task [status].
/{BotCommands.ListCommand} [query]: Cari di Google Drive(s).
/{BotCommands.SearchCommand} [query]: Cari torrents dengan API.
/{BotCommands.StatusCommand}: Nampilin status semua download.
/{BotCommands.StatsCommand}: Nampilin stats mesin tempat bot dihost.
/{BotCommands.PingCommand}: Cek berapa lama buat Ping Bot (Cuma Owner & Sudo).
/{BotCommands.AuthorizeCommand}: Otorisasi chat atau user buat pake bot (Cuma Owner & Sudo).
/{BotCommands.UnAuthorizeCommand}: Hapus otorisasi chat atau user buat pake bot (Cuma Owner & Sudo).
/{BotCommands.UsersCommand}: Nampilin pengaturan user (Cuma Owner & Sudo).
/{BotCommands.AddSudoCommand}: Tambah user sudo (Cuma Owner).
/{BotCommands.RmSudoCommand}: Hapus user sudo (Cuma Owner).
/{BotCommands.RestartCommand}: Restart dan update bot (Cuma Owner & Sudo).
/{BotCommands.LogCommand}: Dapat file log bot. Berguna buat laporan crash (Cuma Owner & Sudo).
/{BotCommands.ShellCommand}: Jalankan perintah shell (Cuma Owner).
/{BotCommands.AExecCommand}: Exec fungsi async (Cuma Owner).
/{BotCommands.ExecCommand}: Exec fungsi sync (Cuma Owner).
/{BotCommands.ClearLocalsCommand}: Hapus lokal {BotCommands.AExecCommand} atau {BotCommands.ExecCommand} (Cuma Owner).
/{BotCommands.RssCommand}: Menu RSS.
"""