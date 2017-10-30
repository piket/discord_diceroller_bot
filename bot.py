# By Timon Pike
# Discord bot for rolling dice for a variety of RPG systems

import discord, os
from discord.ext import commands
import re
from diceroller import *

description = """
    A bot that can handle a large variety of simple and complex roll commands for Role-Playing Games.
    """

help_text = """
    The base command to use this bot is !roll or !!roll (for quiet mode) followed by a roll command
    XdA: rolls X A-sided dice. Ex: !roll 4d6
    XdAs#: rolls X A-sided dice and calculates the number of successes equal to or greater than #. Ex: !roll 7d10s8
    XdA<# or XdA>#: an alternate verson to 's' the < or > denotes a less than or equal to or greater than of equal to for determining successes.
    XdA!#eN: rolls X A-sided dice, then for every result equal to or greater than #, it rolls N more dice. By leaving off eN, it defaults to 1 extra die and leaving off the # defaults to the maximum result. Ex: !roll 7d10!9e2
    XdAk#: rolls X A-sided dice, then keeps only the highest # of results. You can instead keep the lowest by appending 'l'. Ex: 5d6k4 or 5d6k4l
    XdAd#: rolls X A-sided dice, then drops the lowest # results. You can instead drop the highest by appending 'h'. Ex: 5d6d1 or 5d6d1h
    XdA+C: rolls X A-sided dice, then adds C to the result. If C is another roll command, that string is calculated before added to the toal. Ex: 4d6+3 or 4d6+1d4

    You can combine all of these different modifiers into complex roll commands. Ex: 7d10s8!9+2 - calculates successes at 8 or higher, explodes 9s and 10s and adds 2 successes.
    """
bot = commands.Bot(command_prefix='!', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('--------------')

@bot.command()
async def doc():
    await bot.say(help_text)
    return

@bot.command()
async def roll(message : str):
    await bot.say(parse_roll(message))
    return

def parse_roll(message):
    try:
        print('Message received:',message)
        commands = command_parser(clean_message(message))

        roll_data = make_roll(commands)
        print(roll_data)
        roll_string = format_rolls(roll_data['rolls'], roll_data['base'])
        print(roll_string)
        return "**Total Result: {0}**\nRolls: {1}".format(roll_data['total'], roll_string)
    except Exception as e:
        print('Exception: {0}'.format(e))
        return "There was an error with your command, please refer to !doc and try again."

def format_rolls(rolls, base):
    string = '['
    for r in base:
        if string != '[':
            string += ', '
        try:
            i = rolls.index(r)
            rolls.remove(i)
            string += '{0}'.format(r)
        except ValueError:
            string += '~~{0}~~'.format(r)
    return string + ']'

def clean_message(msg):
    '''
        strips all characters except alpha-numeric, -, +, !, >, and <
    '''
    msg = re.sub(r"[^a-zA-Z-+!><#0-9]+",'',msg)
    return msg.lower()

def command_parser(msg):
    regex = """
        (?P<x>[0-9]+)?d(?P<a>[0-9]+)
        (?P<success>[><s](?P<s_target>[0-9]+)?)?
        (?P<explode>!(?P<e_target>[0-9]+)?(?P<e_num>[en][0-9]+)?)?
        (?P<keep>k(?P<k_num>[0-9]+)?(?P<k_type>[hl])?)?
        (?P<drop>d(?P<d_num>[0-9]+)?(?P<d_type>[hl])?)?
        (?P<modifier>[-+].*)?
        """
    pattern = re.compile(re.sub(r"\s+", '', regex))
    match = pattern.search(msg)
    return match

def make_roll(match):
    x = int(match.group('x')) if(match.group('x')) else 1
    a = int(match.group('a'))

    success = match.group('success') != None
    success_higher = success and match.group('success')[0] != '<'
    s_target = int(match.group('s_target')) if match.group('s_target') != None else a

    explode = match.group('explode') != None
    e_target = int(match.group('e_target')) if explode and match.group('e_target') else a
    e_num = int(match.group('e_num')[1:]) if explode and match.group('e_num') else 1

    keep = match.group('keep') != None
    k_num = int(match.group('k_num')) if match.group('k_num') != None else x
    keep_higher = False if match.group('k_type') != None and match.group('k_type') == 'l' else True

    drop = match.group('drop') != None
    d_num = int(match.group('d_num')) if match.group('d_num') != None else 0
    drop_highest = False if match.group('d_type') != None and match.group('d_type') == 'h' else True

    modifier = match.group('modifier')

    rolls, base_rolls = roll_with_options(x, a, success, s_target, explode, e_target, e_num, keep, k_num, keep_higher, drop, d_num, drop_highest)
    if(modifier != None):
        add = modifier[0] == '+'
        if(re.match('^[-+][0-9]+$', modifier)):
            return {'total': total_rolls(rolls, int(modifier[1:]), add), 'rolls': rolls, 'base': base_rolls}
        mod_dict = make_roll(command_parser(modifier[1:]))
        total = total_rolls(rolls, mod_dict['total'], add)
        return {'total': total, 'rolls': rolls + mod_dict['rolls'], 'base': base_rolls + mod_dict['base']}
    return {'total': total_rolls(rolls), 'rolls': rolls, 'base': base_rolls}

bot.run(os.environ.get('DICEROLLER_BOT_TOKEN'))