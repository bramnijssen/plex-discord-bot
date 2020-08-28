from discord.ext.commands import Cog, Bot, command, Context
import database as db
import discord
import asyncio


def setup(bot):
    bot.add_cog(Commands(bot))


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


class Commands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # List all TV shows
    @command(name="tvshows")
    async def tv_shows(self, ctx: Context):
        # Define page count
        tv_shows = db.get_all_tv_shows()
        title = "TV Shows"
        page = 1
        total = len(tv_shows) // 10

        # If remainder exists, add one page
        if len(tv_shows) % 10 != 0:
            total += 1

        # Generate embed for message
        def gen_page_embed():
            desc = ""

            start = (page - 1) * 10
            end = page * 10

            if page == total and end > len(tv_shows):
                end = len(tv_shows)

            for i in range(start, end):
                show = tv_shows[i]["title"]
                slug = tv_shows[i]["slug"]

                desc += f"- [{show}](https://thetvdb.com/series/{slug})\n"

            return discord.Embed(
                colour=discord.Colour.from_rgb(229, 160, 13),
                title=title,
                description=desc
            ).set_footer(text=f"Page {page}/{total}")   

        # Send message and add reactions
        msg: discord.Message = await ctx.send(embed=gen_page_embed())
        await add_nav_reactions(msg)

        timeout = 20

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
                    msg = await msg_embed_nav(ctx, msg, gen_page_embed())

                # Remove reaction
                if not from_dm(ctx):
                    await reaction.remove(user)

            except asyncio.TimeoutError:
                await msg_timeout(ctx, msg, title, timeout)
                break

    # Subscribe to TV Show
    @command()
    async def subscribe(self, ctx, *, arg):
        res = db.search_tv_show(arg)
        title = "Subscribe"

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

            # Check if already subscribed to TV show
            if db.is_subscribed(discord_id, tv_show_id):
                await ctx.send(embed=gen_embed(f"\U00002757 You are already subscribed to {tv_show}"))

            else:
                # Define choice emojis
                yes = "\U00002705"
                no = "\U0000274C"

                # Send message and add reactions
                msg: discord.Message = await ctx.send(
                    embed=gen_embed(f"\U00002753 Do you want to subscribe to {tv_show}?"))
                await msg.add_reaction(yes)
                await msg.add_reaction(no)

                timeout = 20

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
                                embed = gen_embed(f"{yes} Subscribed to {tv_show}")

                                # Persist in DB
                                db.subscribe(discord_id, tv_show_id)                        

                            else:
                                embed = gen_embed(f"{no} Cancelled subscription for {tv_show}")

                            # Send/Edit message
                            await msg_embed(ctx, msg, embed)
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
            total = length // 10

            # If remainder exists, add one page
            if length % 10 != 0:
                total += 1

            # Generate embed for message
            def gen_page_embed():
                desc = ""

                start = (page - 1) * 10
                end = page * 10

                if page == total and end > length:
                    end = length

                for i in range(start, end):
                    show = res[i]["title"]
                    slug = res[i]["slug"]

                    desc += f"{i + 1} | [{show}](https://thetvdb.com/series/{slug})\n"

                return discord.Embed(
                    colour=discord.Colour.from_rgb(229, 160, 13),
                    title=title,
                    description=desc
                ).set_footer(text=f"Page {page}/{total}")            

            # Send message and add reactions
            msg: discord.Message = await ctx.send(embed=gen_page_embed())
            await add_nav_reactions(msg)

            def reaction_check(rct, usr):
                return rct.message.id == msg.id and usr != self.bot.user

            def message_check(message):
                try:
                    num = int(message.content)
                    return (1 <= num <= length) and message.author == ctx.author
                
                except ValueError:
                    return False

            timeout = 20

            while True:
                reaction_task = asyncio.create_task(self.bot.wait_for("reaction_add", check=reaction_check))
                message_task = asyncio.create_task(self.bot.wait_for("message", check=message_check))

                done, pending = await asyncio.wait([reaction_task, message_task], timeout=timeout, return_when=asyncio.FIRST_COMPLETED)

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
                        msg = await msg_embed_nav(ctx, msg, gen_page_embed())

                    # Remove reaction
                    if not from_dm(ctx):
                        await reaction.remove(user)

                elif message_task in done:
                    for task in done:
                        message = await task

                    num = int(message.content)

                    await approve(res[num - 1])

                else:
                    await msg_timeout(ctx, msg, title, timeout)
                    break
