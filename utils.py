from chai_guanaco import chat as chai_chat
from chai_guanaco.submit import get_model_info

import config


def get_available_bots():
    available_bots = chai_chat.get_available_bots().split("\n")
    return available_bots


def validate_bot_name(bot_name):
    try:
        chai_chat.SubmissionChatbot._get_bot_config(bot_name)
        return True
    except FileNotFoundError:
        return False


def validate_submission_id(submission_id):
    try:
        get_model_info(submission_id, developer_key=config.DEVELOPER_KEY)
        return True
    except AssertionError:
        return False


def get_response(messages, submission_id, bot_config, application_id):
    chai_bot = chai_chat.Bot(submission_id, config.DEVELOPER_KEY, bot_config)
    chat_history = get_chat_history(messages, bot_config.bot_label, application_id)
    for content, sender in chat_history:
        chai_bot._update_chat_history(content, sender)
    response = chai_bot.response(messages[-1].content)['model_output']
    return response


async def get_messages(thread):
    messages = []
    async for message in thread.history(limit=100):
        messages.append(message)
    messages.reverse()
    return messages


def get_chat_history(messages, bot_label, application_id):
    chat_history = []
    for message in messages[1:-1]:
        content = message.content
        sender = "user"
        if message.author.id == application_id:
            content = "".join(content.split(":")[1:]).strip()
            sender = bot_label
        chat_history.append((content, sender))
    return chat_history


def parse_bot_name_and_submission_id(thread_name):
    parts = thread_name.split(' ')
    bot_name = parts[2]
    submission_id = parts[-1]
    return bot_name, submission_id
