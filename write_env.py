from pathlib import Path
p = Path('.env')
p.write_text('DISCORD_TOKEN=YOUR_TOKEN_HERE\nclient_id=1523393388521590854\nGUILD_ID=1508217876383793242\n', encoding='utf-8')
print(p.read_text(encoding='utf-8'))
