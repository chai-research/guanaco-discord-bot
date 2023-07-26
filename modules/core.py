from discord import Object, Intents, ext

import config


def attach_core_module(bot):
    @bot.event
    async def on_ready():
        await bot.tree.sync(guild=Object(id=config.GUILD_ID))

    @bot.command(name="sync", guilds=[Object(id=config.GUILD_ID)])
    async def sync(ctx: ext.commands.Context):
        await ctx.message.delete()
        await bot.tree.sync(guild=ctx.guild)

    @bot.command(name="info", guilds=[Object(id=config.GUILD_ID)])
    async def info(ctx: ext.commands.Context):
        await ctx.reply(
            "You can chat with any currently deployed model and a bot from the list."
            "Here are some commands you need to know:\n"
            "1. `/bots` — Lists all available bots to talk with.\n"
            "2. `/chat <submission_id> <bot_name>` — Starts conversation with the bot, served by deployed submission."
        )


def create_bot():
    bot = ext.commands.Bot(command_prefix='/', intents=Intents.all(), aplication_id=config.APPLICATION_ID)
    return bot
