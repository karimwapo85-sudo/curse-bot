import os
import random
import datetime
import discord
from discord.ext import commands
from keep_alive import keep_alive  # <--- Asegúrate de que esta línea esté

# 1. START INVISIBLE WEB SERVER
print("Iniciando servidor keep_alive...") # <--- Añade este print para rastrearlo en los logs
keep_alive()
print("Servidor keep_alive iniciado con éxito!") # <--- Añade este otro