import telegram
import os
import time

ADD_THRESHOLD = 3
ADMIN_ID = 232787997
filtered_strings = ['POLLSCIEMO']

bot = telegram.Bot(os.environ['tg_bot_antiflood'])

def handle_update(update):
    if not update.message:
        return

    kickable = []

    message = update.message

    # check for filtered strings
    if message.text and message.from_user.id != ADMIN_ID:
        for filtered_string in filtered_strings:
            if filtered_string.lower() in message.text.lower():
                kickable.append(message.from_user.id)

    # check for adding many users
    if len(message.new_chat_members) >= ADD_THRESHOLD:
        if message.from_user.id == ADMIN_ID:
            message.reply_text('woah there, I almost lifted my hammer')
        else:
            kickable.append(message.from_user.id)
            for user in message.new_chat_members:
                kickable.append(user.id)

    if not kickable:
        return

    message.reply_text('[Admin!](tg://user?id={}), here are the ids: {}'.format(
        ADMIN_ID,
        ' '.join(str(v) for v in kickable)
    ), parse_mode='Markdown')

    for user_id in kickable:
        try:
            message.bot.kickChatMember(message.chat.id, user_id)
        except Exception as e:
            print('failed to kick', message.chat.id, user_id, e)

next_update_id = -100
while 1:
    try:
        updates = bot.getUpdates(offset=next_update_id)
    except telegram.error.TimedOut:
        updates = []

    for update in updates:
        handle_update(update)
        next_update_id = update.update_id + 1

    time.sleep(1)
