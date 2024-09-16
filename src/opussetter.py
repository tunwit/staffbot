import ctypes
import ctypes.util
import discord

def opusloader():
    print("ctypes - Find opus:")
    a = ctypes.util.find_library('opus')
    print(a)
    
    print("Discord - Load Opus:")
    b = discord.opus.load_opus(a)
    print(b)
    
    print("Discord - Is loaded:")
    c = discord.opus.is_loaded()
    print(c)