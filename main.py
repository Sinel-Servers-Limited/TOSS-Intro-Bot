# TOSS-Intro-Bot - Discord Bot
# Copyright (C) 2020 - 2021 Dylan Prins
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.
# If not, see <https://www.gnu.org/licenses/gpl-3.0.txt>.

# You may contact me at toss@sinelservers.xyz

import os
from typing import List
from discord.ext import commands
from discord.ext.commands import errors
from discord import AllowedMentions, Message, Embed, Activity, ActivityType, Member, TextChannel, File
from database.history import History

# Enable colors on windows
if os.name == "nt":
    os.system("color")


bot = commands.Bot(command_prefix="i! ", allowed_mentions=AllowedMentions(roles=False, everyone=False))


@bot.event
async def on_ready():
    joyte = await bot.fetch_user(246862123328733186)
    bot.joy_url = joyte.avatar_url

    await bot.change_presence(activity=Activity(type=ActivityType.watching, name="over TOSS's Introductions"))
    print(f"Logged in as the bot ({bot.user})!")


@bot.event
async def on_command_error(ctx: Member, error: errors):
    if isinstance(error, errors.MemberNotFound):
        await ctx.send("That's not a valid member!")
        return

    if isinstance(error, errors.CommandNotFound):
        return

    raise error


@bot.event
async def on_message(message: Message):
    if bot.user in message.mentions:
        await message.channel.send("Hey, my prefix is `i! `!")
        return

    if message.author.bot:
        return

    history = History(message.guild.id)

    if history.get_intro_channel() != message.channel.id:
        await bot.process_commands(message)
        return

    history.add(message.author.id, message.id)
    total = history.get(message.author.id)
    if total == 1:
        return

    message_links_formatted = ""
    # noinspection PyTypeChecker
    for index, message_id in enumerate(history.get(message.author.id, ids=True)):
        message_links_formatted += f"[{index+1}: {message_id}](https://discord.com/channels/{message.guild.id}/{history.get_intro_channel()}/{message_id})\n"

    if len(message_links_formatted) > 5000:
        with open(f"./{message.author.id}.txt", "w+") as fp:
            fp.write(message_links_formatted)

        message_links_formatted = f"[{total}: {message.id}](https://discord.com/channels/{message.guild.id}/{history.get_intro_channel()}/{message.id})\nRest is in file"

    e = Embed(colour=0x00FF00)
    e.title = "Messages Exceeded"
    e.description = f"`{message.author}` **|** `{message.author.id}`\nThis user has sent `{total}` messages in <#{message.channel.id}>"
    e.add_field(name="Message links", value=message_links_formatted, inline=False)
    e.set_thumbnail(url=message.author.avatar_url)
    e.timestamp = message.created_at
    e.set_footer(text="TOSS Intro Bot made by Joyte", icon_url=bot.joy_url)

    log_channel = message.guild.get_channel(history.get_log_channel())

    await log_channel.send(embed=e)
    if len(message_links_formatted) > 5000:
        await log_channel.send(file=File("./" + str(message.author.id) + ".txt"))
        os.remove("./" + str(message.author.id) + ".txt")


@bot.event
async def on_message_delete(message: Message):
    history = History(message.guild.id)
    if message.channel.id != history.get_intro_channel():
        return

    if message.author.bot:
        return

    history.remove(message.author.id, message.id)

    e = Embed(colour=0xFF0000)
    e.title = f"Message Deleted"
    e.description = f"`{message.author}` **|** `{message.author.id}`\nA message was deleted, and it was removed from the database."
    e.add_field(name="Content", value=message.content, inline=False)
    if message.attachments:
        urls = "\n".join([attachment.url for attachment in message.attachments])
        e.add_field(name="Attachments", value=urls, inline=False)
    e.set_thumbnail(url=message.author.avatar_url)
    e.timestamp = message.created_at
    e.set_footer(text="TOSS Intro Bot made by Joyte", icon_url=bot.joy_url)

    log_channel = message.guild.get_channel(history.get_log_channel())
    await log_channel.send(embed=e)


@bot.event
async def on_bulk_message_delete(messages: List[Message]):
    for message in messages:
        history = History(message.guild.id)
        if message.channel.id != history.get_intro_channel():
            return

        if message.author.bot:
            return

        history.remove(message.author.id, message.id)

        e = Embed(colour=0xFF0000)
        e.title = f"Message Deleted"
        e.description = f"`{message.author}` **|** `{message.author.id}`\nA message was deleted, and it was removed from the database."
        e.add_field(name="Content", value=message.content, inline=False)
        if message.attachments:
            urls = "\n".join([attachment.url for attachment in message.attachments])
            e.add_field(name="Attachments", value=urls, inline=False)
        e.set_thumbnail(url=message.author.avatar_url)
        e.timestamp = message.created_at
        e.set_footer(text="TOSS Intro Bot made by Joyte", icon_url=bot.joy_url)

        log_channel = message.guild.get_channel(history.get_log_channel())
        await log_channel.send(embed=e)


@bot.command()
async def fetchall(ctx: commands.Context, limit: int = 2000):
    """ Fetches all the intro posts """
    if ctx.author.id not in [246862123328733186]:
        await ctx.send("Hey, you can't use this!")
        return

    history = History(ctx.guild.id)
    intro_channel = history.get_intro_channel()

    if intro_channel == 0:
        await ctx.send("The intro channel hasn't been set!")
        return

    channel = ctx.guild.get_channel(intro_channel)

    msg = await ctx.send("Getting history... (this might take a while)")
    entire_history = await channel.history(limit=limit, oldest_first=True).flatten()

    await msg.edit(content="History gotten, beginning processing...")
    for entry in entire_history:
        history.add(entry.author.id, entry.id, commit=False)

    history.manual_commit()
    await msg.edit(content="Processing done! Enjoy your new database!")


@bot.command()
async def delete(ctx: commands.Context, message_id: int = None):
    """ Removes one from users post count """
    if ctx.author.id not in [246862123328733186]:
        await ctx.send("Hey, you can't use this!")
        return

    if message_id is None:
        await ctx.send("Please give a message ID to delete!")

    history = History(ctx.guild.id)

    channel = ctx.guild.get_intro_channel(history.get_intro_channel())
    message = channel.get_message(message_id)
    history.remove(message.author.id, message.id)

    await message.delete()
    await ctx.send("Removed the message!")


@bot.command()
async def introset(ctx: commands.Context, channel: TextChannel = None):
    """ Sets the intro channel """
    if ctx.author.id not in [246862123328733186]:
        await ctx.send("Hey, you can't use this!")
        return

    if channel is None:
        await ctx.send("Please give a channel!")

    history = History(ctx.guild.id)
    history.set_channel_intro(channel.id)

    await ctx.send(f"Set the introduction channel to <#{channel.id}>")


@bot.command()
async def logset(ctx: commands.Context, channel: TextChannel = None):
    """ Sets the log channel """
    if ctx.author.id not in [246862123328733186]:
        await ctx.send("Hey, you can't use this!")
        return

    if channel is None:
        await ctx.send("Please give a channel ID!")

    history = History(ctx.guild.id)
    history.set_channel_log(channel.id)

    await ctx.send(f"Set the log channel to <#{channel.id}>")


@bot.command()
async def info(ctx: commands.Context, user: Member = None):
    """ Gets a user's intro information """
    if user is None:
        user = ctx.author

    history = History(ctx.guild.id)
    e = Embed(color=0xffff00)
    e.title = f"`{user}`'s intro information"
    e.description = None

    if history.get(user.id) == 0:
        e.add_field(name="Intro information", value="This person hasn't posted an introduction!", inline=False)
        message_links_formatted = ""

    else:
        e.add_field(name="Intro information", value=f"Times posted in intro: `{history.get(user.id)}`", inline=False)

        message_links_formatted = ""
        # noinspection PyTypeChecker
        for index, message_id in enumerate(history.get(user.id, ids=True)):
            message_links_formatted += f"[{index + 1}: {message_id}](https://discord.com/channels/{ctx.guild.id}/{history.get_intro_channel()}/{message_id})\n"

        if len(message_links_formatted) > 5000:
            with open(f"./{user.id}.txt", "w+") as fp:
                fp.write(message_links_formatted)

            message_links_formatted = "Check attached file"

        e.add_field(name="Links", value=message_links_formatted, inline=False)

    await ctx.send(embed=e)
    if len(message_links_formatted) > 5000:
        await ctx.send(file=File("./" + str(user.id) + ".txt"))
        os.remove("./" + str(user.id) + ".txt")


if __name__ == "__main__":
    bot.run(os.environ["DISCORD_TOSS_TOKEN"])