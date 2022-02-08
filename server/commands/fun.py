from multiprocessing.connection import Client
import asyncio
from server import database
from server.constants import TargetType
from server.exceptions import ClientError, ArgumentError

from . import mod_only

__all__ = [
    'ooc_cmd_disemvowel',
    'ooc_cmd_undisemvowel',
    'ooc_cmd_shake',
    'ooc_cmd_unshake',
    'ooc_cmd_gimp',
    'ooc_cmd_ungimp',
    'ooc_cmd_washhands',
    'ooc_cmd_autosteno',
    'ooc_cmd_lupacoin',
    'ooc_cmd_givecoin',
    'ooc_cmd_lupabuy'
]


@mod_only()
def ooc_cmd_disemvowel(client, arg):
    """
    Remove all vowels from a user's IC chat.
    Usage: /disemvowel <id>
    """
    if len(arg) == 0:
        raise ArgumentError('You must specify a target.')
    try:
        targets = client.server.client_manager.get_targets(
            client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must specify a target. Use /disemvowel <id>.')
    if targets:
        for c in targets:
            database.log_room('disemvowel', client, client.area, target=c)
            c.disemvowel = True
        client.send_ooc(f'Disemvowelled {len(targets)} existing client(s).')
    else:
        client.send_ooc('No targets found.')


@mod_only()
def ooc_cmd_undisemvowel(client, arg):
    """
    Give back the freedom of vowels to a user.
    Usage: /undisemvowel <id>
    """
    if len(arg) == 0:
        raise ArgumentError('You must specify a target.')
    try:
        targets = client.server.client_manager.get_targets(
            client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError(
            'You must specify a target. Use /undisemvowel <id>.')
    if targets:
        for c in targets:
            database.log_room('undisemvowel', client, client.area, target=c)
            c.disemvowel = False
        client.send_ooc(f'Undisemvowelled {len(targets)} existing client(s).')
    else:
        client.send_ooc('No targets found.')


@mod_only()
def ooc_cmd_shake(client, arg):
    """
    Scramble the words in a user's IC chat.
    Usage: /shake <id>
    """
    if len(arg) == 0:
        raise ArgumentError('You must specify a target.')
    try:
        targets = client.server.client_manager.get_targets(
            client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must specify a target. Use /shake <id>.')
    if targets:
        for c in targets:
            database.log_room('shake', client, client.area, target=c)
            c.shaken = True
        client.send_ooc(f'Shook {len(targets)} existing client(s).')
    else:
        client.send_ooc('No targets found.')


@mod_only()
def ooc_cmd_unshake(client, arg):
    """
    Give back the freedom of coherent grammar to a user.
    Usage: /unshake <id>
    """
    if len(arg) == 0:
        raise ArgumentError('You must specify a target.')
    try:
        targets = client.server.client_manager.get_targets(
            client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must specify a target. Use /unshake <id>.')
    if targets:
        for c in targets:
            database.log_room('unshake', client, client.area, target=c)
            c.shaken = False
        client.send_ooc(f'Unshook {len(targets)} existing client(s).')
    else:
        client.send_ooc('No targets found.')


@mod_only()
def ooc_cmd_gimp(client, arg):
    """
    Replace a user's message with a random message from a list.
    Usage: /gimp <id>
    """
    if len(arg) == 0:
        raise ArgumentError('You must specify a target ID.')
    try:
        targets = client.server.client_manager.get_targets(
            client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must specify a target. Use /gimp <id>.')
    if targets:
        for c in targets:
            database.log_misc('gimp', client, target=c, data=client.area.abbreviation)
            c.gimp = True
        client.send_ooc(f'Gimped {len(targets)} existing client(s).')
    else:
        client.send_ooc('No targets found.')


@mod_only()
def ooc_cmd_ungimp(client, arg):
    """
    Allow the user to send their own messages again.
    Usage: /ungimp <id>
    """
    if len(arg) == 0:
        raise ArgumentError('You must specify a target ID.')
    try:
        targets = client.server.client_manager.get_targets(
            client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must specify a target. Use /ungimp <id>.')
    if targets:
        for c in targets:
            database.log_misc('ungimp', client, target=c, data=client.area.abbreviation)
            c.gimp = False
        client.send_ooc(f'Ungimped {len(targets)} existing client(s).')
    else:
        client.send_ooc('No targets found.')


def ooc_cmd_washhands(client, arg):
    """
    Stay safe!
    Usage: /washhands
    """
    client.send_ooc('You washed your hands!')

def ooc_cmd_autosteno(client, arg):
    """
    Activate auto-steno.
    Usage: /autosteno
    """
    client.send_ooc('Just take notes.')


#APRIL MEMES
def ooc_cmd_lupacoin(client, arg):
    """
    Create a new Lupacoin account or check balance.
    Usage: /lupacoin
    """
    lupabank_list = client.server.bank_data
    account = client.hdid
    if account in lupabank_list:
        coin = load_coin(client)
        #client.send_ooc('You currently have {} Lupacoins.'.format(client.server.bank_data[account]))
        client.send_ooc(f'You currently have {coin} Lupacoins.')
    else:
        client.send_ooc('Creating your Lupabank account...')
        client.server.bank_data[account] = 50
        client.server.save_bankdata()
        client.send_ooc('Account created! We gave you 50 Lupacoins to start with!')

def load_coin(client):
    coin = client.server.bank_data[client.hdid]
    return coin

def save_coin(client, coin):
    client.server.bank_data[client.hdid] = coin
    client.server.save_bankdata()

@mod_only()
def ooc_cmd_givecoin(client, arg):
    """
    Give a user some Lupacoins.
    Usage: /givecoin [id] [amount]
    """
    coin = load_coin(client)
    coin += 1000
    save_coin(client, coin)
    client.send_ooc(f"You have gained Lupacoins! You now have {coin} Lupacoins.")


def ooc_cmd_lupabuy(client, arg):
    """
    See items in the Lupashop and buy them.
    Usage: /lupabuy [item] [text]
    """
    items = {
        "basic": "gimp",
        "average": "announce",
        "premium": "popup"
    }
    try:
        coin = load_coin(client)
        #backup
        client.lupacoin = coin
    except:
        raise ClientError("You don't have a Lupacoin account! Use /lupacoin first!")

    if len(arg) == 0:
        client.send_ooc(f"You have {coin} Lupacoins.")
        client.send_ooc(f'All Lupashop items:\n100LC: {items["basic"]}\n500LC: {items["average"]}\n1000LC: {items["premium"]}')
        client.send_ooc("Use /lupabuy [item] [text] to purchase.")
    else:
        args = arg.split(' ')
        args[0] = args[0].lower()
        choice = args[0]
        if choice in items['basic']:
            if coin >= 100:
                coin -= 100
                save_coin(client, coin)
                client.gimp = True
                client.send_ooc(f'You have gimped yourself for 30 seconds!\nYou have {coin} Lupacoin remaining.')
            else:
                raise ClientError("You do not have enough Lupacoins to buy this!")
        elif choice in items['average']:
            if coin >= 500:
                if len(args) < 2:
                    raise ArgumentError("Cannot send an empty announcement.")
                else:
                    coin -= 500
                    save_coin(client, coin)
                    client.send_ooc(f'You bought {choice.capitalize()}.\nYou have {coin} Lupacoin remaining.')
                    msg = ' '.join(args[1:])
                    client.server.send_all_cmd_pred(
                        'CT', '{}'.format(client.server.config['hostname']),
                        f'=== Announcement ===\r\n{msg}\r\n==================', '1')
            else:
                raise ClientError("You do not have enough Lupacoins to buy this!")
        elif choice in items['premium']:
            if coin >= 1000:
                if len(args) < 2:
                    raise ArgumentError("Cannot send an empty popup message.")
                else:
                    coin -= 1000
                    save_coin(client, coin)
                    client.send_ooc(f'You bought {choice.capitalize()}.\nYou have {coin} Lupacoin remaining.')
                    targets = [c for c in client.area.clients]
                    reason = ' '.join(args[1:])
                    for c in targets:
                        c.send_command('BB', 'You have received a message:\n' + reason)
            else:
                raise ClientError("You do not have enough Lupacoins to buy this!")