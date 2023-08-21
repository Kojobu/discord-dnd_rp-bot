# bot.py
import os
import numpy as np
import discord
from discord.ext import commands
import pickle
from bs4 import BeautifulSoup
import requests
import time
from matplotlib import pyplot as plt
import matplotlib
import datetime as dt
import lxml

TOKEN = ''
GUILD = 'DISCORD_GUILD'

intents = discord.Intents.default()
intents.message_content = True

class characters:
    def __init__(self):
        if os.path.isfile('chars.lib') == True:
            with open('chars.lib', 'rb') as f:
                self.chars = dict(pickle.load(f))
        else:
            self.chars = dict()

    def add(self, name, attributes):
        
        self.chars[name] = np.asarray(attributes, dtype = int)
        self.save()

    def rem(self, name):
        del self.chars[name.lower()]
        self.save()

    def save(self):
        with open('chars.lib', 'wb') as f:
            pickle.dump(self.chars,f)
    
    def give(self, name):
        return seslf.chars[name.lower()]

    def throw(self):
        return self.chars

    def pos(self, name, ability):
        name = name.lower()
        scores = self.give(name)
        if ability.capitalize() in nabil_scor:
            pos = np.where(ability.capitalize() == np.array(nabil_scor))[0][0]
        elif ability in snabil_scor:
            pos = np.where(ability == np.array(snabil_scor))[0][0]
        else:
            pos = None
        return pos, scores

    def modify(self, name, pos, value):
        self.chars[name.lower()][pos] += value
        self.save()

bot = commands.Bot(intents=intents , command_prefix='!' , description='Gustav - The roleplay assistant')

chars = characters()

nabil_scor = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
snabil_scor = ['str', 'dex', 'con', 'int', 'wis', 'cha']

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def add_char(ctx, points=20 ,random=0): #arg1 - assign points freely, arg2 - give value and Gustav assigns the ability points random
    random, points = int(random), int(points)
    ability_scores = points
    await ctx.send("Please give your character a name:")

    def check(m):
        return bot.user != m.author

    msg = await bot.wait_for("message", check=check)
    name = msg.content.lower()

    if random == 1:
        await ctx.send('Creating random character ...')
        ab_sc = np.full(6,0)
        while ability_scores > 0:
            pos = np.random.randint(0,6)
            ab_sc[pos] += 1
            ability_scores -= 1

    else: 
        await ctx.send(f"Your character's name is {msg.content}.\nYou can assign {ability_scores} to your character. The ordering of the scores is\nStrength, Dexterity, Constitution, Intelligence, Wisdom, Charisma")
        ab_sc = np.full(6,-1)
        for i,scor in enumerate(nabil_scor):
            await ctx.send(f'Current score: {scor}. Points left: {ability_scores}\nStr\tDex\tCon\tInt\tWis\tCha\n{ab_sc[0]}\t\t{ab_sc[1]}\t\t{ab_sc[2]}\t\t{ab_sc[3]}\t\t{ab_sc[4]}\t\t{ab_sc[5]}')
            msg = await bot.wait_for("message", check=check)
            num = int(msg.content)
            ability_scores -= num
            if type(num) != int:
                await ctx.send(f'Input dtype is not integer.')
                return
            if ability_scores < 0:
                await ctx.send(f'{ability_scores=}<0, I better stop here.')
                return
            ab_sc[i] = num
    chars.add(name, ab_sc)
    await ctx.send(f'Character {name.capitalize()} successfully created.')

@bot.command()
async def show_char(ctx, name):
    scores = chars.give(name)
    await ctx.send(f"###\t{name.capitalize()}\t###\nStr\tDex\tCon\tInt\tWis\tCha\n{scores[0]}\t\t{scores[1]}\t\t{scores[2]}\t\t{scores[3]}\t\t{scores[4]}\t\t{scores[5]}")

@bot.command()
async def del_char(ctx, name):
    chars.rem(name)
    await ctx.send(f"{name.capitalize()} was deleted.")

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def list_chars(ctx):
    for name in chars.throw().keys():
        scores = chars.give(name)
        await ctx.send(f"###\t{name.capitalize()}\t###\nStr\tDex\tCon\tInt\tWis\tCha\n{scores[0]}\t\t{scores[1]}\t\t{scores[2]}\t\t{scores[3]}\t\t{scores[4]}\t\t{scores[5]}")

@bot.command()
async def stat(ctx, arg):
    pass

@bot.command()
async def mod_char(ctx, name, ability, value):
    value = int(value)
    pos, _ = chars.pos(name, ability)
    chars.modify(name, pos, value)
    word = "added to" if value>=0 else "subtracted from"
    await ctx.send(f"{abs(value)} points were successfully " + word + f""" {name.capitalize()}'s {nabil_scor[pos]}.""")

@bot.command()
async def roll(ctx, name, ability):

    pos, scores = chars.pos(name, ability)
    
    randint = np.random.randint(1,21)
    if scores[pos] >= randint:
        if randint == 20:
            await ctx.send(f'### {nabil_scor[pos]} check was a critical success! ({randint} / {scores[pos]}) ###')
        else:
            await ctx.send(f'{nabil_scor[pos]} check successful! ({randint} / {scores[pos]})')
    else:
        if randint == 1:
            await ctx.send(f'### {nabil_scor[pos]} check was a critical failure! ({randint} / {scores[pos]}) ###')
        else:
            await ctx.send(f'{nabil_scor[pos]} check failed! ({randint} / {scores[pos]})')

@bot.command()
async def info(ctx):
    await ctx.send("""Gustav rp-bot v1.0\n
    Code by Tom Schlenker\n
    https://github.com/Kojobu/discord-dnd_rp-bot
    """)

@bot.command()
async def helpme(ctx):
    await ctx.send("""A command must start with "!", "{}" denotes optional arguments
    ```!add_char {#POINTS} {RANDOM?}``` - Adds a character with {#POINTS} ability points (base value is 20 if not given). If {RANDOM?} flag is set 1, ability score will be assigned randomly. 
    ```!del_char NAME``` - Removes the character from the database
    ```!show_char NAME``` - Returns the ability scores of the given character
    ```!list_char``` - Returns a list of all saved characters with the corresponing ability scores
    ```!roll NAME SCORE``` - Check character's ability score (d20 roll, (rolled / character's ability))
    ```!mod_char NAME SCORE VALUE``` - Adds / subtracts given amount of ability points to character's score
    ```!test WORD``` - Returns WORD (for debug purposes only)
    ```!stat``` - Returns statistics about rolls and probabilities (not yet implemented)
    ```!info``` - Gives info about Gustav
    """)
    
@bot.slash_command(name="first_slash") #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def first_slash(ctx): 
    await ctx.respond("You executed the slash command!")

@bot.slash_command(name="ozon") #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def ozon(ctx): 
    '''Returns current ozon concentration in Heidelberg'''
    url = "https://weather.com/forecast/air-quality/l/464ff4f67462799509e60caea6f814062d58eb77833cfa81b374cb8be899dc07"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    ozon_val = soup.find_all('main')[0].find_all('section')[1].find_all('span')[7].contents
    await ctx.respond(f'Current ozon concentration is: {ozon_val[0]}')

@bot.slash_command(name="mensa") #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def mensa(ctx): 
    """Print the mensa food for Zentralmensa HD"""
    url = 'https://www.studentenwerk.uni-heidelberg.de/de/speiseplan_neu'
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'lxml')
    food_bs4 = soup.find_all('table')[9:11]
    food = """Today's food is:\n"""
    food += str(food_bs4[0].find_all('td')[15])[4:-5]
    food += """\n\nTomorrow's food is:\n"""
    food += str(food_bs4[1].find_all('td')[15])[4:-5]
    await ctx.respond(food)

@bot.slash_command(name='shutdown')
@commands.is_owner()
async def stop(ctx):
    await ctx.respond('Goodbye!')
    exit()

@bot.slash_command(name='plot')
async def plot(ctx, data):
    '''Enter a list of datapoint, seperated by ',', and I'll plot it for you'''
    y = np.asarray(data.split(","),dtype=float)
    plt.plot(y)
    plt.savefig('temp.jpg')
    await ctx.send(f"Your plot is ready!", file=discord.File("temp.jpg"))


@bot.slash_command(name='b-field')
async def bfield(ctx):
    '''Plot the local B-field of my room'''
    with open('/home/berry-potato/Documents/mag/sensorsave.dat') as f:
        raw = np.loadtxt(f)
    mes = raw[0::2]
    t = raw[1::2]
    timestamps = [dt.datetime.fromtimestamp(ts) for ts in t]
    mes /= mes.mean()
    fig, ax = plt.subplots()
    ax.plot(timestamps, mes)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d-%m-%Y %H:%M:%S'))
    plt.xticks(rotation=25)
    plt.xlabel('Time')
    plt.ylabel('Relative, Absolute Field Strength')
    plt.title('Relative Magnetic Field vs Time')
    fig.tight_layout()
    plt.savefig('./mag.png')
    await ctx.send(file=discord.File('mag.png'))

bot.run(TOKEN)
