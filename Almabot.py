import discord
#from dotenv import load_dotenv
import schedule
import asyncio
import os
from discord.ext import commands, tasks
import threading
import time

######### Scheduler ##########

def event_starter(func):
    if not func.is_running():
        func.start()

schedstop = threading.Event()
def timer():
    while not schedstop.is_set():
        schedule.run_pending()
        time.sleep(5)
schedthread = threading.Thread(target=timer)
schedthread.start()

############# ENV VAR PARSING ###############

#load_dotenv()
DISCORD_API_TOKEN = 'NzMwMDg4MDk4ODAwNTk5MTMx.GxSlU2.JV4nhxHmy-1-8SFeP6eHn8voD4N1BZB-EEnEAw'
GSPREAD_ID = '1BEovJX4OQm-fQDBTDFyhPUqEqpMxZ1KQEGVtCh7aIa8'
GUILD_ID = 465931452085829643
VALID_CHANNELS = [739561983187222558,539671619677978634,740429361240604762]
VALID_USERS = [95665066250088448,120409761182253056,122959829856813056]
NITRO_VALID_CHANNELS= [585923852098469888]
LOG_CHANNEL= 740429361240604762



API_callcount=0

######### COMMAND PREFIX ##########

class Almabot(commands.Bot):

    async def on_ready(self):
        print('')

    async def setup_hook(self):
        print("Almabot i loading nitroparser...")
        await self.load_extension("nitroparser")

bot = Almabot(command_prefix = '.', intents=discord.Intents.default())

######### COMMANDS #########

@bot.command()
async def load(ctx, extension):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        bot.load_extension(f'cogs.{extension}')
        print(f'loading {extension}')

@bot.command()
async def unload(ctx, extension):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        bot.unload_extension(f'cogs.{extension}')
        print(f'unloading {extension}')

@bot.command()
async def reload(ctx, extension):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        print(f'reloading {extension}')

@bot.command()
async def validusers(ctx):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        print('List of bot enabled channels{')
        for i in VALID_USERS:
            n=bot.get_user(i)
            if n != None:
                print (f'{n} \ {n.display_name} \ {n.id}')
            else:
                print(i)
        print('}')

@bot.command()
async def validchannels(ctx):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        print('List of bot enabled channels{')
        for i in VALID_CHANNELS:
            n=bot.get_channel(i)
            print (f'{n.guild} \ {n.name} \ {n.id}')
        print('}')

@bot.command()
async def count(ctx):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        print(f'API_callcount is {API_callcount}')

@bot.command()
async def kill(ctx):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        try:
            await ctx.send('Goodbye cruel world! (logging out)')
        finally:
            await bot.logout()

#Bot command Channel Validation Function

async def channelvalid(ch):
    if ch.id in VALID_CHANNELS:
        return True
    else:
        return False

async def nitrochannelvalid(ch):
    if ch.id in NITRO_VALID_CHANNELS:
        return True
    else:
        return False

#User Validation Function

async def uservalid(member):
    if member.id in VALID_USERS:
        return True
    else:
        return False

async def A_uservalid(member):
    if member.id in VALID_USERS:
        return True
    else:
        return False
############ COG LOAD LOOP ###############

#for filename in os.listdir('./cogs'):
#    if filename.endswith('.py'):
#        try:
#            print(f'loading {filename}')
#            bot.load_extension(f'cogs.{filename[:-3]}')
#        except:
#            print(f'error loading {filename} on cog load')

# async def schedule_loop():
#     while True:
#         schedule.run_pending()
#         await asyncio.sleep(1)
#
#
# bot.loop.create_task(schedule_loop())

# bot.run(DISCORD_API_TOKEN)

def main():
    bot.run(DISCORD_API_TOKEN)

if __name__ == "__main__":
    main()