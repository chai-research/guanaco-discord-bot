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


def create_bot():
    bot = ext.commands.Bot(command_prefix='/', intents=Intents.all(), aplication_id=config.APPLICATION_ID)
    return bot
