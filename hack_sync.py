import main
import asyncio

async def go():
    await main.bot.login(main.TOKEN)
    guild_id = int(main.GUILD_ID)
    print('app id', main.bot.application_id)
    print('bot user', main.bot.user)
    print('global commands count', len(main.bot.tree._global_commands))
    print('guild commands before', main.bot.tree._guild_commands.get(guild_id))
    main.bot.tree.copy_global_to(guild=main.bot.get_guild(guild_id) or main.bot._connection._get_guild(guild_id) if False else main.bot.guilds[0])
    print('copied global to guild')
    await main.bot.close()

asyncio.run(go())
