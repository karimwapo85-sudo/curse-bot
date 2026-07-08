from pathlib import Path
import main

print('loaded main.py')
print('TOKEN exists:', bool(main.TOKEN))
print('GUILD_ID:', main.GUILD_ID)
print('prefix commands:', len(main.bot.commands))
print([c.name for c in main.bot.commands])
print('tree commands:', len(main.bot.tree._commands))
print([c.name for c in main.bot.tree._commands])
print('tree commands details:')
for c in main.bot.tree._commands:
    print('-', c.name, c.qualified_name, type(c).__name__)
