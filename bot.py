from modules.characters import attach_characters_module
from modules.chat import attach_chat_module
from modules.core import attach_core_module, create_bot
import config


def main():
    bot = create_bot()
    compose_attached_modules(bot)
    bot.run(config.BOT_TOKEN)


def compose_attached_modules(bot):
    attach_characters_module(bot)
    attach_chat_module(bot)
    attach_core_module(bot)


if __name__ == "__main__":
    main()
