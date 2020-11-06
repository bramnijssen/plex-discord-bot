import discord

# Message timeout
timeout = 20


# Define arrow (nav) emojis
left = "\U00002B05"
right = "\U000027A1"


async def add_nav_reactions(msg, page, total):
    if total != 1:
        if page != 1:
            await msg.add_reaction(left)

        if page != total:
            await msg.add_reaction(right)
    

def from_dm(ctx):
    return ctx.guild is None


def gen_embed(title, desc):
    return discord.Embed(
        colour=discord.Colour.from_rgb(229, 160, 13),
        title=title,
        description=desc
    )


async def msg_embed(ctx, msg, embed):
    if from_dm(ctx):
        await msg.delete()
        msg = await ctx.send(embed=embed)

    else:
        await msg.clear_reactions()
        await msg.edit(embed=embed)

    return msg


async def msg_embed_nav(ctx, msg, embed, page, total):
    msg = await msg_embed(ctx, msg, embed)
    await add_nav_reactions(msg, page, total)

    return msg


async def msg_timeout(msg, title):
    await msg.edit(embed=gen_embed(title, f"\U000023F0 Timeout reached after {timeout} seconds"))
    await msg.clear_reactions()


def total_pages(length):
    total = length // 10

    # If remainder exists, add one page
    if length % 10 != 0:
        total += 1

    return total


def bullet_list(db_result, i, desc):
    show = db_result[i][1]

    desc += f"- {show}\n"
    return desc


def number_list(db_result, i, desc):
    show = db_result[i][1]

    desc += f"{i + 1} | {show}\n"
    return desc


def page_embed(page, db_result, template, title, **kwargs):
    desc = ""
    length = len(db_result)
    total = total_pages(length)

    start = (page - 1) * 10
    end = page * 10

    if page == total and end > length:
        end = length

    add_msg = kwargs.get('add_msg')
    if add_msg:
        desc = f"{add_msg}\n\n"

    for i in range(start, end):
        desc = template(db_result, i, desc)

    return gen_embed(title, desc).set_footer(text=f"Page {page}/{total}")
