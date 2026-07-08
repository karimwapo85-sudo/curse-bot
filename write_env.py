from pathlib import Path
p = Path('.env')
p.write_text('DISCORD_TOKEN=MTUyMzM5MzM4ODUyMTU5MDg1NA.GHVAHi.gBFqogtwl88xSqlNPGJse6ND5ouZmVU2WI6-vQ\nclient_id=1523393388521590854\nGUILD_ID=1508217876383793242\n', encoding='utf-8')
print(p.read_text(encoding='utf-8'))
