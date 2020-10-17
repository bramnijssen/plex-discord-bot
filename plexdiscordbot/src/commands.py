from discord.ext.commands import Cog, Bot, command, Context
import database as db
import discord
import asyncio


def setup(bot):
    bot.add_cog(Commands(bot))


# Message timeout
timeout = 20


# Define arrow (nav) emojis
left = "\U00002B05"
right = "\U000027A1"


async def add_nav_reactions(message):
    await message.add_reaction(left)
    await message.add_reaction(right)


def from_dm(ctx):
    return ctx.guild is None


async def msg_embed(ctx, msg, embed):
    if from_dm(ctx):
        await msg.delete()
        await ctx.send(embed=embed)

    else:
        await msg.edit(embed=embed)
        await msg.clear_reactions()


async def msg_embed_nav(ctx, msg, embed):
    if from_dm(ctx):
        await msg.delete()
        msg = await ctx.send(embed=embed)
        await add_nav_reactions(msg)

    else:
        await msg.edit(embed=embed)

    return msg


async def msg_timeout(ctx, msg, title, timeout):
    embed = discord.Embed(
        colour=discord.Colour.from_rgb(229, 160, 13),
        title=title,
        description=f"\U000023F0 Timeout reached after {timeout} seconds"
    )

    await msg_embed(ctx, msg, embed)


def total_pages(length):
    total = length // 10

    # If remainder exists, add one page
    if length % 10 != 0:
        total += 1

    return total


def bullet_list(db_result, i, desc):
    show = db_result[i]["title"]

    desc += f"- {show}\n"
    return desc


def number_list(db_result, i, desc):
    show = db_result[i]["title"]

    desc += f"{i + 1} | {show}\n"
    return desc


def page_embed(page, db_result, template, title):
    desc = ""
    length = len(db_result)
    total = total_pages(length)

    start = (page - 1) * 10
    end = page * 10

    if page == total and end > length:
        end = length

    for i in range(start, end):
        desc = template(db_result, i, desc)

    return discord.Embed(
        colour=discord.Colour.from_rgb(229, 160, 13),
        title=title,
        description=desc
    ).set_footer(text=f"Page {page}/{total}")


class Commands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # List all TV shows
    @command(name="tvshows")
    async def tv_shows(self, ctx: Context):
        tv_shows = db.get_all_tv_shows()
        title = "TV Shows"
        page = 1
        total = total_pages(len(tv_shows))

        # Send message and add reactions
        msg: discord.Message = await ctx.send(embed=page_embed(page, tv_shows, bullet_list, title))
        await add_nav_reactions(msg)

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
                    msg = await msg_embed_nav(ctx, msg, page_embed(page, tv_shows, bullet_list, title))

                # Remove reaction
                if not from_dm(ctx):
                    await reaction.remove(user)

            except asyncio.TimeoutError:
                await msg_timeout(ctx, msg, title, timeout)
                break

    # Change notification setting for TV Show
    @command()
    async def notify(self, ctx, *, arg):
        res = db.search_tv_show(arg)
        title = "Notify"

        # Generate embed for message
        def gen_embed(desc):
            return discord.Embed(
                colour=discord.Colour.from_rgb(229, 160, 13),
                title=title,
                description=desc
            )

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
                embed = gen_embed(f"\U00002757 You are already subscribed to {tv_show}. Do you want to unsubscribe?")
                embed_yes = gen_embed(f"{yes} Unsubscribed from {tv_show}")
                embed_no = gen_embed(f"{no} Cancelled unsubscription of {tv_show}")

            else:
                embed = gen_embed(f"\U00002753 Do you want to subscribe to {tv_show}?")
                embed_yes = gen_embed(f"{yes} Subscribed to {tv_show}")
                embed_no = gen_embed(f"{no} Cancelled subscription for {tv_show}")

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
                    await msg_timeout(ctx, msg, title, timeout)
                    break

        # If no results
        if len(res) == 0:
            await ctx.send(embed=gen_embed("\U0000274C No results"))

        # If one result
        elif len(res) == 1:
            await approve(res[0])     
        
        # If many results
        else:
            page = 1
            length = len(res)
            total = total_pages(length)

            # Send message and add reactions
            msg: discord.Message = await ctx.send(embed=page_embed(page, res, number_list, title))
            await add_nav_reactions(msg)

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
                        msg = await msg_embed_nav(ctx, msg, page_embed(page, res, number_list, title))

                    # Remove reaction
                    if not from_dm(ctx):
                        await reaction.remove(user)

                # Message containing number
                elif message_task in done:
                    for task in done:
                        message = await task

                    num = int(message.content)

                    await approve(res[num - 1])

                else:
                    await msg_timeout(ctx, msg, title, timeout)
                    break

    # List subscriptions
    @command()
    async def subs(self, ctx: Context):
        discord_id = ctx.author.id
        res = db.get_subscriptions(discord_id)
        title = "Subscriptions"
        page = 1
        total = total_pages(len(res))   

        # Send message and add reactions
        msg: discord.Message = await ctx.send(embed=page_embed(page, res, bullet_list, title))
        await add_nav_reactions(msg)

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
                    msg = await msg_embed_nav(ctx, msg, page_embed(page, res, bullet_list, title))

                # Remove reaction
                if not from_dm(ctx):
                    await reaction.remove(user)

            except asyncio.TimeoutError:
                await msg_timeout(ctx, msg, title, timeout)
                break