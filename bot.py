import os
import asyncio
import tempfile
import glob
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = os.environ.get("604439759:AAEemVGYyZBpuvqsPPYAkjP6NozDLxS1Cdw")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋\n"
        "لینک پست یا ریلز اینستاگرام رو بفرست تا دانلود کنم.\n\n"
        "⚠️ فقط پست‌های عمومی قابل دانلود هستن."
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "instagram.com" not in url:
        await update.message.reply_text("❌ لینک اینستاگرام نیست!")
        return

    msg = await update.message.reply_text("⏳ در حال دانلود...")

    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": "mp4",
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

            files = glob.glob(os.path.join(tmpdir, "*"))

            if not files:
                await msg.edit_text("❌ فایلی دانلود نشد.")
                return

            for file_path in files:
                ext = os.path.splitext(file_path)[1].lower()
                with open(file_path, "rb") as f:
                    if ext in [".mp4", ".mov", ".webm"]:
                        await update.message.reply_video(video=f, caption="✅ دانلود شد")
                    elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
                        await update.message.reply_photo(photo=f, caption="✅ دانلود شد")
                    else:
                        await update.message.reply_document(document=f, caption="✅ دانلود شد")

            await msg.delete()

        except yt_dlp.utils.DownloadError as e:
            err = str(e)
            if "login" in err.lower() or "private" in err.lower():
                await msg.edit_text("🔒 این پست خصوصیه و قابل دانلود نیست.")
            else:
                await msg.edit_text(f"❌ خطا در دانلود:\n{err[:200]}")
        except Exception as e:
            await msg.edit_text(f"❌ خطای غیرمنتظره:\n{str(e)[:200]}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
