import main

print('commands count', len(main.bot.tree.get_commands()))
for cmd in main.bot.tree.get_commands():
    print('---')
    print('name:', cmd.name)
    print('qualified_name:', getattr(cmd, 'qualified_name', None))
    print('description:', getattr(cmd, 'description', None))
    print('guild_ids:', getattr(cmd, 'guild_ids', None))
    print('cmd_type:', type(cmd).__name__)
    print('command obj:', cmd)
