import discord
import schedule
import os
from discord.ext import commands
import threading
import time
from dotenv import load_dotenv

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

load_dotenv()

API_callcount=0

######### COMMAND PREFIX ##########

class Almabot(commands.Bot):

    async def on_ready(self):
        print('Almabot is booting...')

    async def setup_hook(self):
        print("Almabot is loading nitroparser...")
        await self.load_extension("nitroparser")

intents = discord.Intents.all()
intents.message_content = True
bot = Almabot(command_prefix = '.', intents=intents)

######### COMMANDS #########

@bot.hybrid_command()
async def load(ctx, extension):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        bot.load_extension(f'cogs.{extension}')
        print(f'loading {extension}')

@bot.hybrid_command()
async def unload(ctx, extension):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        bot.unload_extension(f'cogs.{extension}')
        print(f'unloading {extension}')

@bot.hybrid_command()
async def reload(ctx, extension):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        print(f'reloading {extension}')

@bot.hybrid_command()
async def validusers(ctx):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        print('List of bot enabled channels{')
        for i in os.getenv("VALID_USERS"):
            n=bot.get_user(i)
            if n != None:
                print (f'{n} \ {n.display_name} \ {n.id}')
            else:
                print(i)
        print('}')

@bot.hybrid_command(name='validchannels', with_app_command=True)
async def validchannels(ctx):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        print('List of bot enabled channels{')
        for i in os.getenv("VALID_CHANNELS"):
            n=bot.get_channel(i)
            print (f'{n.guild} \ {n.name} \ {n.id}')
        print('}')

@bot.hybrid_command(name='count', with_app_command=True)
async def count(ctx):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        print(f'API_callcount is {API_callcount}')

@bot.hybrid_command(name='kill', with_app_command=True)
async def kill(ctx):
    if await uservalid(ctx.author) and await channelvalid(ctx.channel):
        try:
            await ctx.send('Goodbye cruel world! (logging out)')
        finally:
            await bot.logout()

#Bot command Channel Validation Function

async def channelvalid(ch):
    if str(ch.id) in os.getenv("VALID_CHANNELS"):
        return True
    else:
        return False

async def nitrochannelvalid(ch):
    if str(ch.id) in os.getenv("NITRO_VALID_CHANNELS"):
        return True
    else:
        return False

#User Validation Function

async def uservalid(member):
    if str(member.id) in os.getenv("VALID_USERS"):
        return True
    else:
        return False

async def A_uservalid(member):
    if str(member.id) in os.getenv("VALID_USERS"):
        return True
    else:
        return False

def main():
    bot.run(os.getenv("DISCORD_API_TOKEN"))

if __name__ == "__main__":
    main()