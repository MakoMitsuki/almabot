import discord
import gspread
import json
import threading
import asyncio
import schedule
import time
from datetime import datetime
import Almabot
from Almabot import client
from discord.ext import commands, tasks


class Nitro(commands.Cog):


    def __init__(self, client):
        self.client = client
        schedule.every().day.at("09:00").do(Almabot.event_starter, self.check_emoji)
        schedule.every().day.at("09:10").do(Almabot.event_starter, self.task_role_check)
        #schedule.every(1).minutes.do(Almabot.event_starter, self.check_emoji)
    ################################ EVENTS ###########################

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            print(f'Nitroparser loaded and connected to {self.client.get_guild(Almabot.GUILD_ID)}')
        except:
            print('Environmental variables failed to load.\n Not connected to any server.')
        try:
            print(f'Connected to Spreadsheet {Almabot.GSPREAD_ID} through Google Spreadsheet API')
        except:
            print('Failed to connect to Google API')
        Almabot.API_callcount=0
        print('API_callcount initialized to 0')
        await log('Almabot is online!')
        #schedule.every().day.at("09:48").do(check_emoji)
        await log('`Emoji_check` scheduled for 12:00pm EST.')
        await log('`Role_check` scheduled for 12:10pm EST.')


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guildid=Almabot.GUILD_ID

        if after.guild.id == guildid:
            if before.roles != after.roles:

                with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'r') as f:
                    nitrolist = json.load(f)

                if not str(after.id) in nitrolist and after.premium_since != None:
                    await add_nitrodata(nitrolist, after)

                elif str(after.id) in nitrolist and after.premium_since == None:
                    await inactivate_nitrodata(nitrolist, after)

                elif str(after.id) in nitrolist and str(nitrolist[str(after.id)]['Nitro Status'])[:8]=='Inactive':
                    await reactivate_nitrodata(nitrolist, after)

                with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'w') as f:
                    json.dump(nitrolist, f)

            elif before.display_name != after.display_name and after.premium_since != None:
                with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'r') as f:
                    nitrolist = json.load(f)

                await change_displayname_nitrodata(nitrolist, after)
                await change_name_nitrodata(nitrolist, after)

                with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'w') as f:
                    json.dump(nitrolist, f)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name and self.client.get_guild(Almabot.GUILD_ID).get_member(after.id).premium_since != None:
            with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'r') as f:
                nitrolist = json.load(f)

                await change_name_nitrodata(nitrolist, after)
                await log(f'<@{before.id}> has changed their `username` from {before} to {after}')

            with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'w') as f:
                json.dump(nitrolist, f)

    ############################ COMMANDS #####################################
    @commands.command()
    async def database_init(self, ctx):
        if await Almabot.nitrochannelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
            print('command in nitro channel list')
            #gc=gspread.service_account(filename='/home/mikapi/Desktop/almabot/client_secret.json')
            wks=[]
            #wks=gc.open_by_key(Almabot.GSPREAD_ID).sheet1

            with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'r') as f:
                nitrolist = json.load(f)

            for member in ctx.channel.members:
                if not str(member.id) in nitrolist and member.premium_since != None:
                    await init_add_nitrodata(nitrolist, member, wks)
                elif str(member.id) in nitrolist and str(nitrolist[str(member.id)]['Nitro Status'])[:8]=='Inactive':
                    await init_reactivate_nitrodata(nitrolist, member, wks)

            with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'w') as f:
                json.dump(nitrolist, f)

            await print_database_batch_gspread()

    # @commands.command()
    # async def database_print(self, ctx):
    #     # print(Almabot.validchannels(ctx.channel))
    #     # print(Almabot.uservalid(ctx.author))
    #     if await Almabot.channelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
    #         print('database_print function executed')
    #         gc=gspread.service_account(filename='/home/mikapi/Desktop/almabot/client_secret.json')
    #         wks=gc.open_by_key(Almabot.GSPREAD_ID).sheet1
    #
    #         with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'r') as f:
    #             nitrolist = json.load(f)
    #
    #         batch_data=[]
    #         for i in nitrolist:
    #             r=str(nitrolist[i]['gspread Index'])[1:]
    #             Name=nitrolist[i]['Name']
    #             Display_Name=nitrolist[i]['Display Name']
    #             Start=nitrolist[i]['Nitro Start']
    #             Status=nitrolist[i]['Nitro Status']
    #             v=[i,Name,Display_Name,Start,Status]
    #             batch_data.append({'range': f'{r}:{r}', 'values': [v]})
    #
    #         wks.batch_update(batch_data)
    #         print('printed batch_data to sheet')

    @commands.command()
    async def api_count_test(self, ctx):
        if await Almabot.channelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
            if api_free():
                print(f'The count is at {Almabot.API_callcount}')
            else:
                print('False over 5')

    @commands.command()
    async def api_stress_test(self, ctx):
        if await Almabot.nitrochannelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
            print('command in nitro channel list')
            #gc=gspread.service_account(filename='/home/mikapi/Desktop/almabot/client_secret.json')
            wks=[]
            #wks=gc.open_by_key(Almabot.GSPREAD_ID).sheet1

            with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'r') as f:
                nitrolist = json.load(f)

            for member in ctx.channel.members:
                if not str(member.id) in nitrolist and member.premium_since != None:
                    await add_nitrodata(nitrolist, member)
                elif str(member.id) in nitrolist and str(nitrolist[str(member.id)]['Nitro Status'])[:8]=='Inactive':
                    await reactivate_nitrodata(nitrolist, member)

            with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'w') as f:
                json.dump(nitrolist, f)

    # @commands.command()
    # async def datetest(self, ctx):
    #     if await Almabot.channelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
    #         gc=gspread.service_account(filename='/home/mikapi/Desktop/almabot/client_secret.json')
    #         wks=gc.open_by_key(Almabot.GSPREAD_ID).sheet1
    #         enddate=datetime.fromisoformat('2019-08-15').date()
    #         startdate=datetime.today().date()
    #         diff=(startdate-enddate).days
    #         print(enddate)
    #         print(startdate)
    #         print(type(diff))
    #         if diff <= 10:
    #             print('diff is less than 10')
    #         else:
    #             print('diff is greater than 10')
    #         v=wks.cell(4, 5).value[10:]
    #         print(v)
    #         print(type(v))
    #         Inactive: 2019-05-15
    #
    #         print(str((datetime.today().date()-datetime.date(ctx.author.premium_since)).days//30))
    #
    #         with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'r') as f:
    #             nitrolist = json.load(f)
    #
    #         i=nitrolist[str(ctx.author.id)]['Nitro Status'][10:]
    #         #
    #         enddate=datetime.fromisoformat(i).date()
    #         today=datetime.today().date()
    #         diff=(today-enddate).days
    #
    #
    #         nitrolist[str(member.id)]['Nitro Status']='Active'
    #
    #         if diff > 10:
    #             nitrolist[str(member.id)]['Nitro Start']=str(datetime.date(member.premium_since))
    #
    #         if api_free():
    #             await write_to_gspread(nitrolist, member)
    #         else:
    #             await add_to_queue(nitrolist, member)


    @commands.command()
    async def logtest(self, ctx):
        if await Almabot.channelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
            await log('test')

    #     @commands.command()
    #     async def emoji_init(self, ctx):
    #         if await Almabot.channelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
    #             with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'r') as f:
    #                 nitrolist = json.load(f)
    #
    #             for i in nitrolist:
    #                 nitrolist[i]['emoji']='1'
    #
    #             with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'w') as f:
    #                 json.dump(nitrolist, f)
    #
    #             await log('emoji_init completed')

    #     @commands.command()
    #     async def channeltest(self, ctx):
    #         if await Almabot.channelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
    #             art_channel=Almabot.client.get_channel(489201127125155850)
    #             await art_channel.send('<@&489196596257488897> This is a test. Sorry for the ping!')

    @commands.command()
    async def force_role_check(self, ctx):
        if await Almabot.channelvalid(ctx.channel) and await Almabot.uservalid(ctx.author):
            with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'r') as f:
                nitrolist = json.load(f)
            
            await log('Forcing server boost role checker...')
            await role_check_loop()

    ################### TASKS #######################################
    @tasks.loop(hours=24)
    async def check_emoji(self):
        print('emoji_check starting')
        #await log('Emoji_check starting')
        with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'r') as f:
            nitrolist = json.load(f)

        emoji_count=0

        for i in nitrolist:
            if nitrolist[i]['emoji']=='0':
                start=nitrolist[i]['Nitro Start']
                n=(datetime.today().date()-datetime.fromisoformat(start).date()).days//31
                if n >= 2:
                    emoji_count+=1
                    nitrolist[i]['emoji']='1'
                else:
                    pass
            else:
                pass
        if emoji_count > 0:
            try:
                art_channel=Almabot.client.get_channel(489201127125155850)
                await art_channel.send(f'<@&489196596257488897> {emoji_count} booster(s) are now eligble for emojis!')
                #await art_channel.send('this is a test!')
            finally:
                await log('Attempting to send Artist ping...')
                with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'w') as f:
                    json.dump(nitrolist, f)

        await log('scheduled emoji check complete')
    @check_emoji.before_loop
    async def before_check_emoji(self):
        await self.client.wait_until_ready()

    @tasks.loop(hours=24)
    async def task_role_check(self):
        await role_check_loop()
        
    @task_role_check.before_loop
    async def before_task_role_check(self):
        await self.client.wait_until_ready()
    ############################ FUNCTIONS #####################################

    async def add_nitrodata(nitrolist, member):
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
            await log(f'<@{member.id}> has boosted the server for the first time!')
            if api_free():
                await write_to_gspread(nitrolist, member)
            else:
                await add_to_queue(nitrolist, member)

    async def change_displayname_nitrodata(nitrolist, member):
        if str(member.id) in nitrolist and str(member.display_name) != nitrolist[str(member.id)]['Display Name']:
            nitrolist[str(member.id)]['Display Name']=str(member.display_name)
            await log(f'<@{member.id}> has changed their `display_name` to {member.display_name}')
            if api_free():
                await write_to_gspread(nitrolist, member)
            else:
                await add_to_queue(nitrolist, member)

    async def inactivate_nitrodata(nitrolist, member):
        if str(member.id) in nitrolist and nitrolist[str(member.id)]['Nitro Status'] == 'Active':
            i=int(nitrolist[str(member.id)]['Nitro Total'])
            d=nitrolist[str(member.id)]['Nitro Start']
            i+=(datetime.today().date()-datetime.fromisoformat(d).date()).days//30
            nitrolist[str(member.id)]['Nitro Total']=str(i)
            nitrolist[str(member.id)]['Nitro Status']='Inactive'
            nitrolist[str(member.id)]['Nitro End']=str(datetime.now().date())
            await log(f'<@{member.id}> has removed their server boost.')
            #do stuff here
            if api_free():
                await write_to_gspread(nitrolist, member)
            else:
                await add_to_queue(nitrolist, member)
            await role_check(nitrolist, member)

    async def reactivate_nitrodata(nitrolist, member):
        if str(member.id) in nitrolist and member.premium_since != None:
            i=nitrolist[str(member.id)]['Nitro End']
            d1=datetime.now().date()
            d2=datetime.fromisoformat(i).date()
            diff=(d1-d2).days
            if diff > 10:
                nitrolist[str(member.id)]['Nitro Start']=str(datetime.date(member.premium_since))
                nitrolist[str(member.id)]['Nitro Status']='Active'
                await log(f'<@{member.id}> has reboosted the server. Consecutive months have been reset!')
            else:
                nitrolist[str(member.id)]['Nitro Status']='Active'
                i=int(nitrolist[str(member.id)]['Nitro Total'])
                d=nitrolist[str(member.id)]['Nitro Start']
                c=nitrolist[str(member.id)]['Nitro End']
                i-=(datetime.fromisoformat(c).date()-datetime.fromisoformat(d).date()).days//30
                nitrolist[str(member.id)]['Nitro Total']=str(i)
                await log(f'<@{member.id}> has reboosted the server within 10 days.')
                await role_check(nitrolist, member)

            if api_free():
                await write_to_gspread(nitrolist, member)
            else:
                await add_to_queue(nitrolist, member)

    async def change_name_nitrodata(nitrolist, member):
        if str(member.id) in nitrolist and nitrolist[str(member.id)]['Name']!=str(member):
            nitrolist[str(member.id)]['Name']=str(member)
            if api_free():
                await write_to_gspread(nitrolist, member)
            else:
                await add_to_queue(nitrolist, member)

    async def write_to_gspread(nitrolist, member):
        gc=gspread.service_account(filename='/home/mikapi/Desktop/almabot/client_secret.json')
        wks=gc.open_by_key(Almabot.GSPREAD_ID).sheet1
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

    async def init_add_nitrodata(nitrolist, member, wks):
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

    async def init_reactivate_nitrodata(nitrolist, member, wks):
        if str(member.id) in nitrolist and member.premium_since != None:
            nitrolist[str(member.id)]['Nitro Start']=str(datetime.date(member.premium_since))
            nitrolist[str(member.id)]['Nitro Status']='Active'
            #await init_gspread(nitrolist, member, wks)

    # async def init_gspread(nitrolist, member, wks):
    #     wks.update(nitrolist[str(member.id)]['gspread Index'], [[nitrolist[str(member.id)]['Name'], nitrolist[str(member.id)]['Display Name'], nitrolist[str(member.id)]['Nitro Start'], nitrolist[str(member.id)]['Nitro Status'], str(member.id)]])
    #     wks.update('B1', [[str(())]]) #Last Updated Time

    async def add_to_queue(nitrolist, member):
        with open('/home/mikapi/Desktop/almabot/queued_data.json', 'r') as f:
            queued_data = json.load(f)

        queued_data[str(member.id)]=dict(nitrolist[str(member.id)])

        with open('/home/mikapi/Desktop/almabot/queued_data.json', 'w') as f:
            json.dump(queued_data, f)



    def api_free():
        if Almabot.API_callcount==0:
            Almabot.client.loop.create_task(callcount_reset())
        if Almabot.API_callcount<40:
            Almabot.API_callcount+=1
            print(f'API_callcount {Almabot.API_callcount}/40')
            return True
        else:
            return False

    async def callcount_reset():
        print('First change in interval triggered. Timer set for 120 seconds until reset')
        await asyncio.sleep(120)
        Almabot.API_callcount=0
        print('Count reset')
        print_queue_batch_gspread()


    def print_queue_batch_gspread():
        gc=gspread.service_account(filename='/home/mikapi/Desktop/almabot/client_secret.json')
        wks=gc.open_by_key(Almabot.GSPREAD_ID).sheet1

        with open('/home/mikapi/Desktop/almabot/queued_data.json', 'r') as f:
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

            with open('/home/mikapi/Desktop/almabot/queued_data.json', 'w') as f:
                json.dump(queued_data, f)
        else:
            print('queued_data is empty; interval reset')

    async def print_database_batch_gspread():
        print('database_print function executed')
        gc=gspread.service_account(filename='/home/mikapi/Desktop/almabot/client_secret.json')
        wks=gc.open_by_key(Almabot.GSPREAD_ID).sheet1

        with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'r') as f:
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

    async def log(message):
        try:
            ch=Almabot.client.get_channel(Almabot.LOG_CHANNEL)
            await ch.send(message)
        finally:
            pass


    async def role_check(nitrolist, member):
        #await log('1')
        g=Almabot.client.get_guild(int(Almabot.GUILD_ID))
        boost3=g.get_role(585924024484364289)
        boost5=g.get_role(615306345423306991)
        #await log(f'{boost5} {boost5.id}')
        #await log('2')
        if member.premium_since != None:
            #await log('3')
            s=nitrolist[str(member.id)]['Nitro Start']
            #await log(f'{s}')
            i=(datetime.today().date()-datetime.fromisoformat(s).date()).days//30
            #await log(f'i = {i}')
    #         if i >= 5 and boost5 in member.roles:
    #             await member.remove_roles(boost3, reason='Member now 5 month booster')
            if i >= 5 and boost5 not in member.roles:
                #await log('5')
                await member.add_roles(boost5, reason='5 months of consecutive boosting')
                await member.remove_roles(boost3, reason='Member now 5 month booster')
                await log(f'<@{member.id}> is now a 5 month booster!')
            elif i < 5 and i >= 3 and boost3 not in member.roles:
                await member.add_roles(boost3, reason='3 months of consecutive boosting')
                await log(f'<@{member.id}> is now a 3 month booster!')
            else:
                pass
        elif boost3 in member.roles or boost5 in member.roles:
            #await log('4')
            await member.remove_roles(boost3,boost5, reason='Member has removed their server boost.')
            await log(f'<@{member.id}> has lost their consecutive booster roles')
        #await log('test completed')
            
    async def role_check_loop():
        with open('/home/mikapi/Desktop/almabot/nitro_data.json', 'r') as f:
            nitrolist = json.load(f)
        g=Almabot.client.get_guild(int(Almabot.GUILD_ID))
        booster=g.get_role(585574101750644787)
        boost3=g.get_role(585924024484364289)
        boost5=g.get_role(615306345423306991)
        await log('`role_checker` start')
        for i in booster.members:
            await role_check(nitrolist, i)
        await log('secondary checks start')
        #await log(f'list: {[u for u in boost3.members if u not in booster.members]}')
        #if [u for u in boost3.members if u not in booster.members] != []:
        for x in [u for u in boost3.members if u not in booster.members]:
            await role_check(nitrolist, x)
        await log('tertiary checks start')
        #if [u for u in boost5.members if u not in booster.members] != []:
        for z in [u for u in boost5.members if u not in booster.members]:
            await role_check(nitrolist, z)
        await log('scheduled role check complete.')

def setup(client):
    client.add_cog(Nitro(client))

