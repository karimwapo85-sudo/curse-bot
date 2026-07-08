import main
print('application_id', main.bot.application_id)
print('has app id', hasattr(main.bot, 'application_id'))
print('bot user id', main.bot.user)
print('tree global', len(main.bot.tree._global_commands))
print('tree guilds', list(main.bot.tree._guild_commands.keys()))
print('tree global names', [k[0] for k in main.bot.tree._global_commands.keys()])
