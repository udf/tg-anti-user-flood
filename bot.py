import telegram
import os
import time

ADD_THRESHOLD = 5
filtered_strings = ['POLLSCIEMO']

bot = telegram.Bot(os.environ['tg_bot_antiflood'])

def get_admin_mentions(chat_id):
    mentions = []
    admins = bot.getChatAdministrators(-1001145055784)
    for admin in admins:
        if admin.user.username:
            mentions.append('@' + admin.user.username)
        else:
            mentions.append('[{}](tg://user?id={})'.format(admin.user.first_name, admin.user.id))
    return ' '.join(mentions)

def handle_update(update):
    if not update.message:
        return

    kickable = []

    message = update.message

    # check for filtered strings
    if message.text:
        for filtered_string in filtered_strings:
            if filtered_string.lower() in message.text.lower():
                kickable.append(message.from_user.id)

    # check for adding many users
    if len(message.new_chat_members) >= ADD_THRESHOLD:
        kickable.append(message.from_user.id)
        for user in message.new_chat_members:
            kickable.append(user.id)

    if not kickable:
        return

    print('trying to kick {} user(s) from {}: {}'.format(
        len(kickable),
        message.chat.id,
        kickable
    ))

    # if the first user is an admin, then we shouldn't kick anyone
    try:
        message.bot.kickChatMember(message.chat.id, kickable.pop(0))
    except Exception as e:
        if 'user is an administrator' in e.message.lower():
            message.reply_text('woah there, I almost lifted my hammer')
            print('first user was admin, so not kicking anyone')
            return

    for user_id in kickable:
        try:
            message.bot.kickChatMember(message.chat.id, user_id)
        except Exception as e:
            print('failed to kick', user_id, e, type(e))

    message.reply_text('{}, here are the ids: {}'.format(
        get_admin_mentions(message.chat.id),
        ' '.join(str(v) for v in kickable)
    ), parse_mode='Markdown')


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
