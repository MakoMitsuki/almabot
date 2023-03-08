import discord
import gspread
import json
import threading
import asyncio
import schedule
import time
from datetime import datetime
import Almabot
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os

load_dotenv()

class Nitro(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        schedule.every().day.at("09:48").do(Almabot.event_starter, self.check_emoji)

    async def logToChannel(self, message):
        try:
            await self.bot.get_channel(int(os.getenv("LOG_CHANNEL"))).send(message)
        finally:
            pass
    
    async def api_free(self):
        if Almabot.API_callcount==0:
            print(f'API_callcount is at {Almabot.API_callcount}')
        if Almabot.API_callcount<40:
            Almabot.API_callcount+=1
            print(f'API_callcount {Almabot.API_callcount}/40')
            return True
        else:
            return False
        
    ############################ FUNCTIONS #####################################
    
    async def write_to_gspread(self, nitrolist, member):
        gc=gspread.service_account(filename='./client_secret.json')
        wks=gc.open_by_key(os.getenv("GSPREAD_ID")).sheet1
        name=nitrolist[str(member.id)]['Name']
        display_name=nitrolist[str(member.id)]['Display Name']
        start=nitrolist[str(member.id)]['Nitro Start']
        end=nitrolist[str(member.id)]['Nitro End']
        status=nitrolist[str(member.id)]['Nitro Status']
        total=nitrolist[str(member.id)]['Nitro Total']
        id=str(member.id)
        v=[id,name,display_name,start,end,status,total]
        wks.update(nitrolist[str(member.id)]['gspread Index'], [v], value_input_option='USER_ENTERED')
        wks.update('B1', [[str(datetime.now())]], value_input_option='USER_ENTERED') #Last Updated Time
        
    async def add_to_queue(self, nitrolist, member):
        with open('./queued_data.json', 'r') as f:
            queued_data = json.load(f)

        queued_data[str(member.id)]=dict(nitrolist[str(member.id)])

        with open('./queued_data.json', 'w') as f:
            json.dump(queued_data, f)

    async def add_nitrodata(self, nitrolist, member):
        if not str(member.id) in nitrolist:
            nitrolist[str(member.id)]={}
            nitrolist[str(member.id)]['Name']=str(member)
            nitrolist[str(member.id)]['Display Name']=str(member.display_name)
            nitrolist[str(member.id)]['Nitro Start']=str(datetime.date(member.premium_since))
            nitrolist[str(member.id)]['Nitro End']=''
            nitrolist[str(member.id)]['Nitro Status']='Active'
            nitrolist[str(member.id)]['Nitro Total']='0'#str((datetime.today().date()-datetime.date(member.premium_since)).days//30)
            nitrolist[str(member.id)]['gspread Index']='A'+str(len(nitrolist)+3) #int = spreadsheet vertical offset
            nitrolist[str(member.id)]['emoji']='0'
            await self.logToChannel(f'{member} has boosted the server for the first time!')
            isFree = await self.api_free()
            if isFree:
                await self.write_to_gspread(nitrolist, member)
            else:
                await self.add_to_queue(nitrolist, member)

    async def change_displayname_nitrodata(self, nitrolist, member):
        if str(member.id) in nitrolist and str(member.display_name) != nitrolist[str(member.id)]['Display Name']:
            nitrolist[str(member.id)]['Display Name']=str(member.display_name)
            await self.logToChannel(f'{member} has changed their `display_name` to {member.display_name}')
            isFree = await self.api_free()
            if isFree:
                await self.write_to_gspread(nitrolist, member)
            else:
                await self.add_to_queue(nitrolist, member)

    async def inactivate_nitrodata(self, nitrolist, member):
        if str(member.id) in nitrolist and nitrolist[str(member.id)]['Nitro Status'] == 'Active':
            i=int(nitrolist[str(member.id)]['Nitro Total'])
            d=nitrolist[str(member.id)]['Nitro Start']
            i+=(datetime.today().date()-datetime.fromisoformat(d).date()).days//30
            nitrolist[str(member.id)]['Nitro Total']=str(i)
            nitrolist[str(member.id)]['Nitro Status']='Inactive'
            nitrolist[str(member.id)]['Nitro End']=str(datetime.now().date())
            await self.logToChannel(f'{member} has removed their server boost.')
            #do stuff here
            isFree = await self.api_free()
            if isFree:
                await self.write_to_gspread(nitrolist, member)
            else:
                await self.add_to_queue(nitrolist, member)

    async def reactivate_nitrodata(self, nitrolist, member):
        if str(member.id) in nitrolist and member.premium_since != None:
            i=nitrolist[str(member.id)]['Nitro End']
            d1=datetime.now().date()
            d2=datetime.fromisoformat(i).date()
            diff=(d1-d2).days
            if diff > 10:
                nitrolist[str(member.id)]['Nitro Start']=str(datetime.date(member.premium_since))
                nitrolist[str(member.id)]['Nitro Status']='Active'
                await self.logToChannel(f'{member} has reboosted the server. Consecutive months have been reset!')
            else:
                nitrolist[str(member.id)]['Nitro Status']='Active'
                i=int(nitrolist[str(member.id)]['Nitro Total'])
                d=nitrolist[str(member.id)]['Nitro Start']
                c=nitrolist[str(member.id)]['Nitro End']
                i-=(datetime.fromisoformat(c).date()-datetime.fromisoformat(d).date()).days//30
                nitrolist[str(member.id)]['Nitro Total']=str(i)
                await self.logToChannel(f'{member} has reboosted the server within 10 days.')

            isFree = await self.api_free()
            if isFree:
                await self.write_to_gspread(nitrolist, member)
            else:
                await self.add_to_queue(nitrolist, member)

    async def change_name_nitrodata(self, nitrolist, member):
        if str(member.id) in nitrolist and nitrolist[str(member.id)]['Name']!=str(member):
            nitrolist[str(member.id)]['Name']=str(member)
            
            isFree = await self.api_free()
            if isFree:
                await self.write_to_gspread(nitrolist, member)
            else:
                await self.add_to_queue(nitrolist, member)

    async def init_add_nitrodata(self, nitrolist, member, wks):
        if not str(member.id) in nitrolist:
            nitrolist[str(member.id)]={}
            nitrolist[str(member.id)]['Name']=str(member)
            nitrolist[str(member.id)]['Display Name']=str(member.display_name)
            nitrolist[str(member.id)]['Nitro Start']=str(datetime.date(member.premium_since))
            nitrolist[str(member.id)]['Nitro End']=''
            nitrolist[str(member.id)]['Nitro Status']='Active'
            nitrolist[str(member.id)]['Nitro Total']='0'#str((datetime.today().date()-datetime.date(member.premium_since)).days//30)
            nitrolist[str(member.id)]['gspread Index']='A'+str(len(nitrolist)+3) #int = spreadsheet vertical offset
            nitrolist[str(member.id)]['emoji']='0'
            #await init_gspread(nitrolist, member, wks)

    async def init_reactivate_nitrodata(self, nitrolist, member, wks):
        if str(member.id) in nitrolist and member.premium_since != None:
            nitrolist[str(member.id)]['Nitro Start']=str(datetime.date(member.premium_since))
            nitrolist[str(member.id)]['Nitro Status']='Active'
            #await init_gspread(nitrolist, member, wks)

    # async def init_gspread(self, nitrolist, member, wks):
    #     wks.update(nitrolist[str(member.id)]['gspread Index'], [[nitrolist[str(member.id)]['Name'], nitrolist[str(member.id)]['Display Name'], nitrolist[str(member.id)]['Nitro Start'], nitrolist[str(member.id)]['Nitro Status'], str(member.id)]])
    #     wks.update('B1', [[str(())]]) #Last Updated Time

    def print_queue_batch_gspread(self):
        gc=gspread.service_account(filename='./client_secret.json')
        wks=gc.open_by_key(os.getenv("GSPREAD_ID")).sheet1

        with open('./queued_data.json', 'r') as f:
            queued_data = json.load(f)

        if queued_data != {}:
            batch_data=[]
            for i in queued_data:
                r=str(queued_data[i]['gspread Index'])[1:]
                Name=queued_data[i]['Name']
                Display_Name=queued_data[i]['Display Name']
                Start=queued_data[i]['Nitro Start']
                end=queued_data[i]['Nitro End']
                Status=queued_data[i]['Nitro Status']
                total=queued_data[i]['Nitro Total']
                v=[i,Name,Display_Name,Start,end,Status,total]
                batch_data.append({'range': f'{r}:{r}', 'values': [v]})

            wks.batch_update(batch_data, value_input_option='USER_ENTERED')
            print('queued batch_data printed to sheet')
            #Reserved for adding check to see if data had changed during for loop
            queued_data = {}

            with open('./queued_data.json', 'w') as f:
                json.dump(queued_data, f)
        else:
            print('queued_data is empty; interval reset')
    
    async def print_database_batch_gspread(self):
        print('database_print function executed')
        gc=gspread.service_account(filename='./client_secret.json')
        wks=gc.open_by_key(os.getenv("GSPREAD_ID")).sheet1

        with open('./nitro_data.json', 'r') as f:
            nitrolist = json.load(f)

        batch_data=[]
        for i in nitrolist:
            r=str(nitrolist[i]['gspread Index'])[1:]
            Name=nitrolist[i]['Name']
            Display_Name=nitrolist[i]['Display Name']
            Start=nitrolist[i]['Nitro Start']
            end=nitrolist[i]['Nitro End']
            total=nitrolist[i]['Nitro Total']
            Status=nitrolist[i]['Nitro Status']
            v=[i,Name,Display_Name,Start,end,Status,total]
            batch_data.append({'range': f'{r}:{r}', 'values': [v]})

        wks.batch_update(batch_data, value_input_option='USER_ENTERED')
        print('printed batch_data to sheet')

    @tasks.loop(hours=24)
    async def check_emoji(self):
        print('emoji_check starting')
        await self.logToChannel('Emoji_check starting')
        with open('./nitro_data.json', 'r') as f:
            nitrolist = json.load(f)

        emoji_count=0

        for i in nitrolist:
            if nitrolist[i]['emoji']=='0':
                start=nitrolist[str(member.id)]['Nitro Start']
                n=(datetime.today().date()-datetime.fromisoformat(start).date()).days//30
                if n >= 2:
                    emoji_count+=1
                    nitrolist[i]['emoji']='1'
                else:
                    pass
            else:
                pass
        if emoji_count > 0:
            try:
                art_channel=self.bot.get_channel(489201127125155850)
                await art_channel.send(f'<!@&489196596257488897> {emoji_count} booster(s) are now eligble for emojis!')
            finally:

                with open('./nitro_data.json', 'w') as f:
                    json.dump(nitrolist, f)

        await self.log('scheduled emoji check complete')
    
    @check_emoji.before_loop
    async def before_check_emoji(self):
        await self.bot.wait_until_ready()
    
    ################################ EVENTS ###########################

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            print(f'Nitroparser loaded and connected to {self.bot.get_guild(int(os.getenv("GUILD_ID")))}')
        except:
            print('Environmental variables failed to load.\n Not connected to any server.')
        try:
            print(f'Connected to Spreadsheet {os.getenv("GSPREAD_ID")} through Google Spreadsheet API')
        except:
            print('Failed to connect to Google API')
        Almabot.API_callcount=0
        print('API_callcount initialized to 0')
        await self.logToChannel('Almabot is online!')
        schedule.every().day.at("09:48").do(self.check_emoji)
        await self.logToChannel('Emoji_check scheduled for 12:00pm EST.')


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guildid=int(os.getenv("GUILD_ID"))

        if after.guild.id == guildid:
            print('attempting member update check')
            if before.roles != after.roles:

                with open('./nitro_data.json', 'r') as f:
                    nitrolist = json.load(f)

                if not str(after.id) in nitrolist and after.premium_since != None:
                    await self.add_nitrodata(nitrolist, after)

                elif str(after.id) in nitrolist and after.premium_since == None:
                    await self.inactivate_nitrodata(nitrolist, after)

                elif str(after.id) in nitrolist and str(nitrolist[str(after.id)]['Nitro Status'])[:8]=='Inactive':
                    await self.reactivate_nitrodata(nitrolist, after)

                with open('./nitro_data.json', 'w') as f:
                    json.dump(nitrolist, f)

            elif before.display_name != after.display_name and after.premium_since != None:
                with open('./nitro_data.json', 'r') as f:
                    nitrolist = json.load(f)

                await self.change_displayname_nitrodata(nitrolist, after)
                await self.change_name_nitrodata(nitrolist, after)

                with open('./nitro_data.json', 'w') as f:
                    json.dump(nitrolist, f)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name and self.bot.get_guild(int(os.getenv("GUILD_ID"))).get_member(after.id).premium_since != None:
            with open('./nitro_data.json', 'r') as f:
                nitrolist = json.load(f)

                await self.change_name_nitrodata(nitrolist, after)
                await self.log(f'{before} has changed their `name` to {after}')

            with open('./nitro_data.json', 'w') as f:
                json.dump(nitrolist, f)

    ############################ COMMANDS #####################################
    @commands.hybrid_command()
    async def database_init(self, ctx):
        if await Almabot.nitrochannelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
            print('command in nitro channel list')
            #gc=gspread.service_account(filename='./client_secret.json')
            wks=[]
            #wks=gc.open_by_key(os.getenv("GSPREAD_ID")).sheet1

            with open('./nitro_data.json', 'r') as f:
                nitrolist = json.load(f)

            for member in ctx.channel.members:
                if not str(member.id) in nitrolist and member.premium_since != None:
                    await self.init_add_nitrodata(nitrolist, member, wks)
                elif str(member.id) in nitrolist and str(nitrolist[str(member.id)]['Nitro Status'])[:8]=='Inactive':
                    await self.init_reactivate_nitrodata(nitrolist, member, wks)

            with open('./nitro_data.json', 'w') as f:
                json.dump(nitrolist, f)

            await self.print_database_batch_gspread()

    @commands.hybrid_command(name='api_count_test', with_app_command=True)
    async def api_count_test(self, ctx):
        if await Almabot.channelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
            isFree = await self.api_free()
            if isFree:
                print(f'The count is at {Almabot.API_callcount}')
            else:
                print('False over 5')

    @commands.hybrid_command()
    async def api_stress_test(self, ctx):
        if await Almabot.nitrochannelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
            print('command in nitro channel list')
            #gc=gspread.service_account(filename='./client_secret.json')
            wks=[]
            #wks=gc.open_by_key(os.getenv("GSPREAD_ID")).sheet1

            with open('./nitro_data.json', 'r') as f:
                nitrolist = json.load(f)

            for member in ctx.channel.members:
                if not str(member.id) in nitrolist and member.premium_since != None:
                    await self.add_nitrodata(nitrolist, member)
                elif str(member.id) in nitrolist and str(nitrolist[str(member.id)]['Nitro Status'])[:8]=='Inactive':
                    await self.reactivate_nitrodata(nitrolist, member)

            with open('./nitro_data.json', 'w') as f:
                json.dump(nitrolist, f)

    @commands.hybrid_command(name='logtest', with_app_command=True)
    async def logtest(self, ctx):
        if await Almabot.channelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
            await self.logToChannel('test')




async def setup(bot):
    await bot.add_cog(Nitro(bot))
