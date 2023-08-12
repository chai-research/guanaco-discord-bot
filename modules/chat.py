import discord
from discord import ChannelType
from discord.ext import commands
from chai_guanaco import chat as chai_chat

import utils

THREAD_NAME_TEMPLATE = "Chat with {bot_name} by {submission_id}"


def attach_chat_module(bot):
    @bot.command(name="chat", description='Starts conversation with the bot, served by deployed submission.')
    async def chat(ctx: commands.Context, submission_id: str, bot_name: str):
        channel = bot.get_channel(ctx.channel.id)
        thread = await channel.create_thread(
            name=THREAD_NAME_TEMPLATE.format(bot_name=bot_name, submission_id=submission_id),
            type=ChannelType.public_thread
        )

        if not utils.validate_bot_name(bot_name):
            await thread.send(f"Unable to find {bot_name}, ensure such character exist.")
            await thread.edit(archived=True, locked=True)
            return

        if not utils.validate_submission_id(submission_id):
            await thread.send(f"Unable to find {submission_id}, ensure such submission exist.")
            await thread.edit(archived=True, locked=True)
            return

        bot_config = chai_chat.SubmissionChatbot._get_bot_config(bot_name)
        await thread.send(f"{bot_config.bot_label}: {bot_config.first_message}")

    @bot.event
    async def on_message(message: discord.Message):
        if message.channel.type != ChannelType.public_thread:
            await bot.process_commands(message)
            return
        if message.channel.archived or message.channel.locked:
            return
        if message.author.id == bot.application_id:
            return

        await message.channel.typing()
        bot_name, submission_id = utils.parse_bot_name_and_submission_id(message.channel.name)
        messages = await utils.get_messages(message.channel)
        bot_config = chai_chat.SubmissionChatbot._get_bot_config(bot_name)
        response = utils.get_response(messages, submission_id, bot_config, bot.application_id)
        await message.reply(f"{bot_config.bot_label}: {response}")
