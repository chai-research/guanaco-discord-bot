import asyncio
import discord
from bs4 import BeautifulSoup
from discord.ext import tasks
from html2image import Html2Image

from chai_guanaco import metrics
from chai_guanaco.utils import cache

import config

NUM_ROWS = 10
LAST_MESSAGE_ID = None


def attach_leaderboard_module(bot: discord.ext.commands.Bot):
    @tasks.loop(hours=6)
    async def send_leaderboard():
        global LAST_MESSAGE_ID
        channel = bot.get_channel(config.LEADERBOARD_CHANNEL_ID)
        leaderboard = await get_leaderboard_data_async()
        leaderboard = prepare_leaderboard_data(leaderboard)
        files = get_files_from_leaderboard(leaderboard)
        embeds = create_embeds(len(files))
        await delete_last_message(channel, bot.application_id)
        message = await channel.send("🏆 Guanaco Leaderboard", embeds=embeds, files=files)
        await message.pin()
        await channel.last_message.delete()
        LAST_MESSAGE_ID = message.id

    @bot.event
    async def on_ready():
        send_leaderboard.start()


async def get_leaderboard_data_async():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_leaderboard_data)


def get_leaderboard_data():
    leaderboard_data = cache(metrics.get_leaderboard, regenerate=False)(config.DEVELOPER_KEY)
    leaderboard_data["thumbs_up_ratio"] *= 100.0
    return leaderboard_data


def prepare_leaderboard_data(leaderboard):
    leaderboard = metrics._print_formatted_leaderboard(leaderboard)
    return leaderboard


def get_files_from_leaderboard(leaderboard):
    files = [_create_discord_file(prize_func(leaderboard), filename)
             for prize_func, filename in zip(
            [_get_grand_prize, _get_thumbs_up_prize, _get_engagement_prize],
            ["image1.png", "image2.png", "image3.png"])]
    return files


def create_embeds(num_of_files):
    embeds = [_create_embed(filename) for filename in [f"image{i + 1}.png" for i in range(num_of_files)]]
    return embeds


async def delete_last_message(channel, bot_id):
    if LAST_MESSAGE_ID:
        await channel.get_partial_message(LAST_MESSAGE_ID).delete()
        return
    pins = await channel.pins()
    for pin in pins:
        if pin.author.id == bot_id:
            await pins[0].delete()
            return


def _create_discord_file(content, filename):
    return discord.File(content, filename=filename)


def _create_embed(filename):
    embed = discord.Embed(type="image")
    embed.set_image(url=f"attachment://{filename}")
    return embed


def _get_grand_prize(df):
    df = df.sort_values('overall_rank').reset_index(drop=True)
    html = get_html_leaderboard(df.round(3).head(NUM_ROWS), 'Grand Prize Contenders')
    image_path = save_html_as_image(html, image_path="grand_prize.png")
    return image_path


def _get_thumbs_up_prize(df):
    df = df.sort_values('thumbs_up_ratio', ascending=False).reset_index(drop=True)
    html = get_html_leaderboard(df.round(3).head(NUM_ROWS), 'Thumbs Up Prize Contenders')
    image_path = save_html_as_image(html, image_path="thumbs_up_prize.png")
    return image_path


def _get_engagement_prize(df):
    df = df.sort_values('engagement_score', ascending=False).reset_index(drop=True)
    html = get_html_leaderboard(df.round(3).head(NUM_ROWS), 'Engagement Prize Contenders')
    image_path = save_html_as_image(html, image_path="engagement_prize.png")
    return image_path


def save_html_as_image(html, image_path):
    hti = Html2Image(custom_flags=["--disable-gpu"])
    data = hti.screenshot(html_str=html, save_as=image_path, size=(1000, 800))
    full_image_path = data[0]
    return full_image_path


def get_html_leaderboard(dataframe, title):
    soup = BeautifulSoup(_get_leaderboard_template(), 'html.parser')
    _add_margin(soup)
    leaderboard = _get_leaderboard_section(soup)
    _update_legend(soup, title)
    _add_columns_to_leaderboard(dataframe, soup, leaderboard)
    return str(soup)


def _add_margin(soup):
    style_tag = soup.new_tag('style')
    style_tag.string = 'body { margin: 70px 85px 85px 90px; }'
    soup.head.append(style_tag)


def _get_leaderboard_section(soup):
    return soup.find('div', {'class': 'chai-competition-detailed-leaderboard'})


def _update_legend(soup, title):
    leaderboard_legend = soup.find('div', {'class': 'chai-competition-detailed-leaderboard-legend'})
    leaderboard_legend.clear()
    legend_icon = soup.new_tag('div')
    legend_icon['class'] = 'chai-competition-detailed-leaderboard-legend-icon'
    leaderboard_legend.append(legend_icon)
    leaderboard_legend.append(title)


def _add_columns_to_leaderboard(dataframe, soup, leaderboard):
    for column_name, pretty_name in _get_column_names().items():
        new_column = _create_column(soup, column_name, pretty_name, dataframe)
        leaderboard.append(new_column)


def _create_column(soup, column_name, pretty_name, dataframe):
    new_column = soup.new_tag('div')
    new_column['class'] = 'chai-competition-detailed-leaderboard-column'
    column_name_entry = _create_column_name_entry(soup, pretty_name)
    new_column.append(column_name_entry)
    _add_entries_to_column(dataframe, soup, column_name, new_column)
    return new_column


def _create_column_name_entry(soup, pretty_name):
    column_name_entry = soup.new_tag('div')
    column_name_entry['class'] = 'chai-competition-detailed-leaderboard-entry'
    column_name_entry.string = pretty_name
    return column_name_entry


def _add_entries_to_column(dataframe, soup, column_name, new_column):
    if column_name == "#":
        for rank in range(1, len(dataframe) + 1):
            new_entry = _create_entry(soup, str(rank), rank <= 3)
            new_column.append(new_entry)
    elif column_name in dataframe.columns:
        for idx, entry in enumerate(dataframe[column_name]):
            new_entry = _create_entry(soup, str(entry), False)
            new_column.append(new_entry)


def _create_entry(soup, entry_text, is_winner):
    new_entry = soup.new_tag('div')
    new_entry['class'] = _get_entry_class(is_winner)
    new_entry.string = entry_text
    return new_entry


def _get_entry_class(is_winner):
    base_class = 'chai-competition-detailed-leaderboard-entry'
    if is_winner:
        return base_class + ' chai-competition-detailed-leaderboard-winner'
    return base_class


def _get_column_names():
    column_names = {
        "#": "#",
        "submission_id": "Submission ID",
        "thumbs_up_ratio": "Thumbs Ups",
        "mcl": "MCL",
        "user_response_length": "User Response Length",
        "engagement_score": "Engagement",
        "overall_rank": "Overall Rank"
    }
    return column_names


def _get_leaderboard_template():
    leaderboard_template = '''<!DOCTYPE html>
    <html>
       <head>
          <link rel="stylesheet" href="https://www.chai-research.com/css/chai-mid.css">
          <link rel="stylesheet" href="https://www.chai-research.com/css/chai-mobile.css">
          <link rel="stylesheet" href="https://www.chai-research.com/css/chai.css">
          <link rel="stylesheet" href="https://www.chai-research.com/css/competition-mobile.css">
          <link rel="stylesheet" href="https://www.chai-research.com/css/competition.css">
          <link rel="stylesheet" href="https://www.chai-research.com/css/main.css">
          <link rel="stylesheet" href="https://www.chai-research.com/css/normalize.css">
       </head>
       <body>
          <div class="competition-evaluation-body-container leaderboard-container">
             <div class="competition-detailed-leaderboard-wrapper">
                <div class="chai-competition-detailed-leaderboard-legend">
                   <div class="chai-competition-detailed-leaderboard-legend-icon"></div>
                   Prize contenders
                </div>
                <div class="chai-competition-detailed-leaderboard">
                </div>
             </div>
          </div>
       </body>
    </html>
    '''
    return leaderboard_template
