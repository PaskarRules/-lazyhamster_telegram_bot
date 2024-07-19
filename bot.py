import logging
import requests
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('YOUR_TELEGRAM_BOT_TOKEN')

ANNOUNCEMENT_URL = 'http://139.59.215.111/api/announcement/'
LIKE_URL = 'http://139.59.215.111/api/announcement/{}/like/'

user_likes = {}
last_post_id = {}
active_chats = set()


def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    active_chats.add(user_id)
    update.message.reply_text('Привет! Здесь вы можете следить за последними новостями. Новости обновляется на лету!')


def get_posts(context: CallbackContext) -> None:
    bot = context.bot
    for user_id in active_chats:
        response = requests.get(ANNOUNCEMENT_URL)
        if response.status_code == 200:
            posts = response.json()
            last_id = last_post_id.get(user_id, 0)
            new_posts = [post for post in posts if post["id"] > last_id]
            if not new_posts:
                continue

            logger.info(f'Полученные новые данные для пользователя {user_id}: {new_posts}')
            for post in new_posts:
                title = post.get("title", "Без названия")
                content = post.get("content", "Без содержания")
                like_count = post.get("like_count", 0)
                post_id = post["id"]
                liked_by_user = user_likes.get(user_id, {}).get(post_id, False)
                if liked_by_user:
                    like_button_text = f"👍 {like_count} ❤️"
                else:
                    like_button_text = f"👍 {like_count}"
                keyboard = [
                    [InlineKeyboardButton(like_button_text, callback_data=f'like_{post_id}')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(chat_id=user_id, text=f'{title}\n{content}', reply_markup=reply_markup)

                last_post_id[user_id] = post_id
        else:
            bot.send_message(chat_id=user_id, text='Не удалось получить посты.')


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    post_id = query.data.split('_')[1]
    user_id = query.from_user.id
    data = {
        "user_id": user_id
    }
    response = requests.post(LIKE_URL.format(post_id), json=data)
    if response.status_code == 200:
        post_response = requests.get(f'{ANNOUNCEMENT_URL}{post_id}')
        if post_response.status_code == 200:
            post = post_response.json()
            title = post.get("title", "Без названия")
            content = post.get("content", "Без содержания")
            like_count = post.get("like_count", 0)
            if user_likes.get(user_id, {}).get(post_id, False):
                user_likes[user_id][post_id] = False
                like_button_text = f"👍 {like_count}"
            else:
                if user_id not in user_likes:
                    user_likes[user_id] = {}
                user_likes[user_id][post_id] = True
                like_button_text = f"👍 {like_count} ❤️"
            keyboard = [
                [InlineKeyboardButton(like_button_text, callback_data=f'like_{post_id}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text=f'{title}\n{content}', reply_markup=reply_markup)
        else:
            query.edit_message_text(text='Не удалось получить обновленные данные поста.')
    else:
        query.edit_message_text(text='Не удалось лайкнуть пост.')


def periodic_task(context: CallbackContext) -> None:
    get_posts(context)


def main() -> None:
    if not TOKEN:
        raise ValueError("Необходимо задать переменную окружения 'YOUR_TELEGRAM_BOT_TOKEN'")

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))

    job_queue = updater.job_queue
    job_queue.run_repeating(periodic_task, interval=10, first=0)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
