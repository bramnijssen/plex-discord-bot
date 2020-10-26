from helpers import *
from discord.ext import commands
from discord.ext.commands import Cog, Bot, command, Context
import database as db
import discord
import asyncio


def setup(bot):
    bot.add_cog(Commands(bot))


class Commands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # List all TV shows
    @command(
        aliases=["shows"],
        name="tvshows", 
        help="Lists available TV Shows")
    async def tv_shows(self, ctx: Context):
        tv_shows = db.get_all_tv_shows()
        title = "TV Shows"
        no_res_desc = "No TV Shows available"
        
        await self.spread_list(tv_shows, title, no_res_desc, ctx)

    # List subscriptions
    @command(
        aliases=["subs"],
        help="Lists subscriptions")
    async def subscriptions(self, ctx: Context):
        subs = db.get_subscriptions(ctx.author.id)
        title = "Subscriptions"
        no_res_desc = "You have no subscriptions"

        await self.spread_list(subs, title, no_res_desc, ctx)

    # List spread across pages
    async def spread_list(self, res, title, no_res_desc, ctx):
        page = 1
        total = total_pages(len(res))

        if total == 0:
            await ctx.send(embed=gen_embed(title, "\U0000274C " + no_res_desc))
        else:
            # Send message and add reactions
            msg: discord.Message = await ctx.send(embed=page_embed(page, res, bullet_list, title))
            await add_nav_reactions(msg, page, total)

            def check(rct, usr):
                return rct.message.id == msg.id and usr != self.bot.user

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=timeout)
                    emoji = str(reaction.emoji)

                    if user == ctx.author and (emoji == left or emoji == right):
                        # Change page
                        if emoji == left:
                            # If left reacted on first page, don't decrease page
                            if page != 1:
                                page -= 1
                        
                        else:
                            # If right reacted on last page, don't increase page
                            if page != total:
                                page += 1
                        
                        # Send/Edit message
                        msg = await msg_embed_nav(ctx, msg, page_embed(page, res, bullet_list, title), page, total)

                    # Remove reaction
                    elif not from_dm(ctx):
                        await reaction.remove(user)

                except asyncio.TimeoutError:
                    await msg_timeout(msg, title)
                    break

    # Change notification setting for TV Show
    @command(
        aliases=["sub"], 
        brief="Subscribe to / Unsubscribe from a TV Show", 
        help="Subscribe to / Unsubscribe from a TV Show from which you would like to receive notifications when new episodes have been added")
    async def subscribe(self, ctx, *, search_term):
        res = db.search_tv_show(search_term)
        title = "Subscribe"

        def approve_embed(desc):
            return gen_embed(title, desc)

        async def approve(show):
            tv_show_id = show["tv_show_id"]
            tv_show = show["title"]
            discord_id = ctx.author.id

            # Define choice emojis
            yes = "\U00002705"
            no = "\U0000274C"

            is_subscribed = db.is_subscribed(discord_id, tv_show_id)

            # Check if already subscribed to TV show
            if is_subscribed:
                embed = approve_embed(f"\U00002757 You are currently subscribed to {tv_show}. Do you want to unsubscribe?")
                embed_yes = approve_embed(f"{yes} Unsubscribed from {tv_show}")
                embed_no = approve_embed(f"{no} Cancelled unsubscription of {tv_show}")

            else:
                embed = approve_embed(f"\U00002753 Do you want to subscribe to {tv_show}?")
                embed_yes = approve_embed(f"{yes} Subscribed to {tv_show}")
                embed_no = approve_embed(f"{no} Cancelled subscription for {tv_show}")

            # Send message and add reactions
            msg: discord.Message = await ctx.send(embed=embed)
            await msg.add_reaction(yes)
            await msg.add_reaction(no)

            def check(rct, usr):
                return rct.message.id == msg.id and usr != self.bot.user
            
            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=timeout)
                    emoji = str(reaction.emoji)

                    # If reaction on correct message equals yes or no AND if reacted by correct user
                    if user == ctx.author and (emoji == yes or emoji == no):
                        # Set correct embed
                        if emoji == yes:                           
                            if is_subscribed:
                                db.unsubscribe(discord_id, tv_show_id) 

                            else:
                                db.subscribe(discord_id, tv_show_id)  

                            await msg_embed(ctx, msg, embed_yes)                      

                        else:
                            await msg_embed(ctx, msg, embed_no)
                        
                        break

                    # Remove reaction
                    if not from_dm(ctx):
                        await reaction.remove(user)

                except asyncio.TimeoutError:
                    await msg_timeout(msg, title)
                    break

        # If no results
        if len(res) == 0:
            await ctx.send(embed=approve_embed("\U0000274C No results"))

        # If one result
        elif len(res) == 1:
            await approve(res[0])     
        
        # If many results
        else:
            page = 1
            length = len(res)
            total = total_pages(length)
            add_msg = "Send the number, corresponding to the show to which you want to subscribe, in a new message"

            # Send message and add reactions
            msg: discord.Message = await ctx.send(embed=page_embed(page, res, number_list, title, add_msg=add_msg))
            await add_nav_reactions(msg, page, total)

            def reaction_check(rct, usr):
                return rct.message.id == msg.id and usr != self.bot.user

            def message_check(message):
                try:
                    num = int(message.content)
                    return (1 <= num <= length) and message.author == ctx.author
                
                except ValueError:
                    return False

            while True:
                reaction_task = asyncio.create_task(self.bot.wait_for("reaction_add", check=reaction_check))
                message_task = asyncio.create_task(self.bot.wait_for("message", check=message_check))

                done, pending = await asyncio.wait([reaction_task, message_task], timeout=timeout, return_when=asyncio.FIRST_COMPLETED)

                # Reaction on message
                if reaction_task in done:
                    for task in done:
                        reaction, user = await task
                    
                    emoji = str(reaction.emoji)

                    if user == ctx.author and (emoji == left or emoji == right):
                        # Change page
                        if emoji == left:
                            # If left reacted on first page, don't decrease page
                            if page != 1:
                                page -= 1
                        
                        else:
                            # If right reacted on last page, don't increase page
                            if page != total:
                                page += 1
                        
                        # Send/Edit message
                        msg = await msg_embed_nav(ctx, msg, page_embed(page, res, number_list, title, add_msg=add_msg), page, total)

                    # Remove reaction
                    elif not from_dm(ctx):
                        await reaction.remove(user)

                # Message containing number
                elif message_task in done:
                    for task in done:
                        message = await task

                    num = int(message.content)
                    await msg.delete()

                    if not from_dm(ctx):
                        await message.delete()

                    await approve(res[num - 1])

                # Timeout
                else:
                    await msg_timeout(msg, title)
                    break

    # If no search term provided
    @subscribe.error
    async def subscribe_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=gen_embed("Error", f"Please enter (parts of) the TV show's name to which you want to subscribe.\n Command usage: `.subscribe {ctx.command.signature}`"))