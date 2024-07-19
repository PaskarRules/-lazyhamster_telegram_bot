import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Установка уровня логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ANNOUNCEMENT_URL = 'http://127.0.0.1:8000/api/announcement/?limit={limit}&offset={offset}'
CURRENT_ANNOUNCEMENT_URL = 'http://127.0.0.1:8000/api/announcement/{}/'
ANNOUNCEMENT_COUNT_URL = 'http://127.0.0.1:8000/api/announcement/counter/'
LIKE_URL = 'http://127.0.0.1:8000/api/announcement/{}/like/'
DISLIKE_URL = 'http://127.0.0.1:8000/api/announcement/{}/dislike/'

users_data = {}


def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    if user_id not in users_data:
        users_data[user_id] = {'count': 0}

    markups = [[InlineKeyboardButton('Получить новые сообщения', callback_data='poll')],]
    new_markup = InlineKeyboardMarkup(markups)

    update.message.reply_text(
        text='Привет! Используйте кнопку снизу что бы всегда быть вкурсе!',
        reply_markup=new_markup
    )


def poll(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    response = requests.get(ANNOUNCEMENT_COUNT_URL)

    if response.status_code == 200:
        data = response.json()

        count = data['count'] - users_data[query.from_user.id]['count']

        if count == 0:
            query.answer("Новых сообщений нету.", show_alert=True)
            return

        users_data[query.from_user.id]['limit'] = 1
        query.answer(f"Новых сообщений {count}. Изучайте с самих свежих новостей!", show_alert=True)
        poll_announcement(update, context)
    else:
        query.answer('Ошибка при выполнении запроса', show_alert=True)


def poll_announcement(update: Update, context: CallbackContext, url='') -> None:
    query = update.callback_query
    user_id = query.from_user.id

    limit = users_data[query.from_user.id]['limit']
    offset = users_data[query.from_user.id]['count']

    response = requests.get(ANNOUNCEMENT_URL.format(limit=limit, offset=offset) if not url else url)
    if response.status_code == 200:
        data = response.json()

        users_data[user_id]['count'] = data['count']
        users_data[user_id]['posts'] = data['results']
        users_data[user_id]['next'] = data['next']
        users_data[user_id]['previous'] = data['previous']
    else:
        query.answer('Ошибка при выполнении запроса', show_alert=True)

    show_posts(update, context)


def show_posts(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    user_id = query.from_user.id
    post = users_data[user_id]['posts'][0]

    keyboard = [[
        InlineKeyboardButton(f"❤️ {post['like_count']}", callback_data=f'like_{post["id"]}'),
        InlineKeyboardButton(f"💔 {post['dislike_count']}", callback_data=f'dislike_{post["id"]}')
    ]]
    prev_next_b = []
    if users_data[user_id]['previous']:
        prev_next_b.append(InlineKeyboardButton("Назад", callback_data='prev_page'))

    if users_data[user_id]['next']:
        prev_next_b.append(InlineKeyboardButton("Вперед", callback_data='next_page'))

    keyboard.append(prev_next_b)
    keyboard.append([InlineKeyboardButton('Получить новые сообщения', callback_data='poll')])

    new_text = f"{post['title']}\n{post['description']}"
    new_markup = InlineKeyboardMarkup(keyboard)

    try:
        query.edit_message_text(
            text=new_text,
            reply_markup=new_markup
        )
    except Exception as e:
        logger.error(f"Failed to edit message: {e}")


def change_page(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    url = ''

    if data == 'next_page':
        url = users_data[user_id]['next']
    elif data == 'prev_page':
        url = users_data[user_id]['previous']

    poll_announcement(update, context, url=url)


def like_dislike(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    action, post_id = data.split('_')
    post_id = int(post_id)

    if action == 'like':
        url = LIKE_URL.format(post_id)
    else:
        url = DISLIKE_URL.format(post_id)

    response = requests.post(url, json={'user_id': user_id})
    if response.status_code == 200:
        announcement_response = requests.get(CURRENT_ANNOUNCEMENT_URL.format(post_id))
        if announcement_response.status_code == 200:
            announcement_data = announcement_response.json()
            users_data[user_id]['posts'] = [announcement_data]

            show_posts(update, context)

    else:
        query.answer('Ошибка при выполнении запроса', show_alert=True)


def main() -> None:
    updater = Updater("7441871392:AAHlh0VLEhtIUmBTx1-FMAT9JgFLlp_Lp2s")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(poll, pattern='^poll$'))
    dispatcher.add_handler(CallbackQueryHandler(show_posts, pattern='^show_posts$'))
    dispatcher.add_handler(CallbackQueryHandler(change_page, pattern='^(next_page|prev_page|first_page|last_page)$'))
    dispatcher.add_handler(CallbackQueryHandler(like_dislike, pattern='^(like|dislike)_'))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
