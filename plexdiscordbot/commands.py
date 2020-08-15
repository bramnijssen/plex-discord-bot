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
    @command(name="tvshows")
    async def tv_shows(self, ctx: Context):
        # Define page count
        tv_shows = db.get_all_tv_shows()
        page = 1
        total = len(tv_shows) // 10

        # If remainder exists, add one page
        if len(tv_shows) % 10 != 0:
            total += 1

        # Generate embed for message
        def gen_embed():
            desc = ""

            for i in range((page - 1) * 10, page * 10):
                title = tv_shows[i]["title"]
                slug = tv_shows[i]["slug"]

                desc += f"- [{title}](https://thetvdb.com/series/{slug})\n"

            return discord.Embed(
                colour=discord.Colour.from_rgb(229, 160, 13),
                title="TV Shows",
                description=desc
            ).set_footer(text=f"Page {page}/{total}")

        # Define arrow emojis
        left = "\U00002B05"
        right = "\U000027A1"

        # Add reactions to message
        async def add_reactions(message):
            await message.add_reaction(left)
            await message.add_reaction(right)

        # Send message and add reactions
        msg: discord.Message = await ctx.send(embed=gen_embed())
        await add_reactions(msg)

        timeout = 20
        from_dm = ctx.guild is None
        
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=timeout)

                # Check if message on which reaction was added is previously sent message AND if reacting user is
                # user who executed command
                if reaction.message.id == msg.id and user == ctx.author:
                    # If sent via DM, remove message and send new one
                    if from_dm:

                        if str(reaction.emoji) == left:
                            # If left reacted on first page, don't decrease page
                            if page != 1:
                                page -= 1

                            await msg.delete()
                            msg = await ctx.send(embed=gen_embed())
                            await add_reactions(msg)

                        elif str(reaction.emoji) == right:
                            # If right reacted on last page, don't increase page
                            if page != total:
                                page += 1

                            await msg.delete()
                            msg = await ctx.send(embed=gen_embed())
                            await add_reactions(msg)

                    # If sent on guild, remove reaction and edit message
                    else:

                        if str(reaction.emoji) == left:
                            # If left reacted on first page, just remove reaction
                            if page != 1:
                                page -= 1
                                await msg.edit(embed=gen_embed())

                        elif str(reaction.emoji) == right:
                            # If right reacted on last page, just remove reaction
                            if page != total:
                                page += 1
                                await msg.edit(embed=gen_embed())

            except asyncio.TimeoutError:
                embed = discord.Embed(
                    colour=discord.Colour.from_rgb(229, 160, 13),
                    title="TV Shows",
                    description=f"\U000023F0 Timeout reached after {timeout} seconds"
                )

                # When timeout reached, send timeout message and break
                if from_dm:
                    await msg.delete()
                    await ctx.send(embed=embed)

                else:
                    await msg.edit(embed=embed)
                    await msg.clear_reactions()

                break

            # If reaction on message in guild, remove reaction afterwards from all users except bot
            if reaction.message.guild is not None and reaction.message.id == msg.id and user != self.bot.user:
                await reaction.remove(user)

    # Subscribe to TV Show
    @command()
    async def subscribe(self, ctx, *, arg):
        res = db.search_tv_show(arg)

        # Generate embed for message
        def gen_embed(desc):
            return discord.Embed(
                colour=discord.Colour.from_rgb(229, 160, 13),
                title="Subscribe",
                description=desc
            )

        # If no results
        if len(res) == 0:
            await ctx.send(embed=gen_embed("\U0000274C No results"))

        # If one result
        elif len(res) == 1:
            tv_show_id = res[0]["tv_show_id"]
            tv_show = res[0]["title"]
            member_id = db.get_member_id(ctx.author.id)
            
            # Check if already subscribed to TV show
            if db.is_subscribed(member_id, tv_show_id):
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
                from_dm = ctx.guild is None
                
                while True:
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=timeout)
                        emoji = str(reaction.emoji)

                        # If reaction on correct message equals yes or no AND if reacted by correct user
                        if reaction.message.id == msg.id and user == ctx.author and (emoji == yes or emoji == no):
                            # Set correct embed
                            if emoji == yes:
                                embed = gen_embed(f"{yes} Subscribed to {tv_show}")

                                # Persist in DB
                                db.subscribe(member_id, tv_show_id)                        

                            else:
                                embed = gen_embed(f"{no} Cancelled subscription for {tv_show}")

                            # Send/Edit message
                            if from_dm:
                                await msg.delete()
                                msg = await ctx.send(embed=embed)

                            else:                           
                                await msg.edit(embed=embed)
                                await msg.clear_reactions()
                            
                            break

                        # If different reaction on message in guild, remove reaction
                        if reaction.message.guild is not None and reaction.message.id == msg.id \
                                and user != self.bot.user:
                            await reaction.remove(user)

                    except asyncio.TimeoutError:
                        # When timeout reached, send timeout message
                        embed = gen_embed(f"\U000023F0 Timeout reached after {timeout} seconds")

                        if from_dm:
                            await msg.delete()
                            await ctx.send(embed=embed)

                        else:
                            await msg.edit(embed=embed)
                            await msg.clear_reactions()

                        break
