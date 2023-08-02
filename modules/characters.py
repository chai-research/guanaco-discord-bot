from discord.ext.commands import Context

import utils


def attach_characters_module(bot):
    @bot.command(name="bots", description='Lists all available bots to talk with.')
    async def bots(ctx: Context):
        available_bots = utils.get_available_bots()
        text = "Available bots:\n"
        for bot_name in available_bots:
            text += f"- {bot_name}\n"
        await ctx.reply(text)

    @bot.command(name="models", description='Lists all available models to talk with.')
    async def models(ctx: Context):
        available_models = utils.get_available_models()
        text = "Available models:\n"
        for bot_name in available_models:
            text += f"- {bot_name}\n"
        await ctx.reply(text)
