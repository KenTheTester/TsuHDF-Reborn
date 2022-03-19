import re
import random

from server import database
from server.constants import TargetType
from server.exceptions import ClientError, ServerError, ArgumentError

from . import mod_only

__all__ = [
    'ooc_cmd_doc',
    'ooc_cmd_cleardoc',
    'ooc_cmd_evidence_mod',
    'ooc_cmd_evi_swap',
    'ooc_cmd_cmdj',
    'ooc_cmd_cm',
    'ooc_cmd_uncm',
    'ooc_cmd_clear_cm',
    'ooc_cmd_setcase',
    'ooc_cmd_anncase',
    'ooc_cmd_blockwtce',
    'ooc_cmd_unblockwtce',
    'ooc_cmd_judgelog',
    'ooc_cmd_evidlog',
    'ooc_cmd_afk',
    'ooc_cmd_prompt',
    'ooc_cmd_case',
    'ooc_cmd_asspull',
    'ooc_cmd_keywords',
    'ooc_cmd_testimony',
    'ooc_cmd_cleartesti',
    'ooc_cmd_afk',
    'ooc_cmd_format'
]


def ooc_cmd_doc(client, arg):
    """
    Show or change the link for the current case document.
    Usage: /doc [url]
    """
    if len(arg) == 0:
        client.send_ooc(f'Document: {client.area.doc}')
        database.log_room('doc.request', client, client.area)
    else:
        client.area.change_doc(arg)
        client.area.broadcast_ooc('{} changed the doc link.'.format(
            client.char_name))
        database.log_room('doc.change', client, client.area, message=arg)


def ooc_cmd_cleardoc(client, arg):
    """
    Clear the link for the current case document.
    Usage: /cleardoc
    """
    if len(arg) != 0:
        raise ArgumentError('This command has no arguments.')
    client.area.change_doc()
    client.area.broadcast_ooc('{} cleared the doc link.'.format(
        client.char_name))
    database.log_room('doc.clear', client, client.area)


@mod_only()
def ooc_cmd_evidence_mod(client, arg):
    """
    Change the evidence privilege mode. Refer to the documentation
    for more information on the function of each mode.
    Usage: /evidence_mod <FFA|Mods|CM|HiddenCM>
    """
    if not arg or arg == client.area.evidence_mod:
        client.send_ooc(
            f'current evidence mod: {client.area.evidence_mod}')
    elif arg in ['FFA', 'Mods', 'CM', 'HiddenCM']:
        if client.area.evidence_mod == 'HiddenCM':
            for i in range(len(client.area.evi_list.evidences)):
                client.area.evi_list.evidences[i].pos = 'all'
        client.area.evidence_mod = arg
        client.send_ooc(
            f'current evidence mod: {client.area.evidence_mod}')
        database.log_room('evidence_mod', client, client.area, message=arg)
    else:
        raise ArgumentError(
            'Wrong Argument. Use /evidence_mod <MOD>. Possible values: FFA, CM, Mods, HiddenCM'
        )


def ooc_cmd_evi_swap(client, arg):
    """
    Swap the positions of two evidence items on the evidence list.
    Usage: /evi_swap <id> <id>
    """
    args = list(arg.split(' '))
    if len(args) != 2:
        raise ClientError("you must specify 2 numbers")
    try:
        client.area.evi_list.evidence_swap(client, int(args[0]), int(args[1]))
        client.area.broadcast_evidence_list()
    except:
        raise ClientError("you must specify 2 numbers")

@mod_only()
def ooc_cmd_cmdj(client, arg):
    """
    Add a CM for the current room, as well as giving access to looping /play.
    DJ can only be given by mod.
    Usage: /cmdj <id>
    """
    if len(arg) > 0:
        try:
            targets = client.server.client_manager.get_targets(
            client, TargetType.ID, int(arg), False)
        except:
            raise ArgumentError('You must specify a target. Use /cmdj <id>.')
        if targets:
            for c in targets:
                ooc_cmd_cm(client, arg)
                if c in client.area.DJs:
                    client.send_ooc(
                        '{} [{}] is already a DJ here.'.format(
                            c.char_name, c.id))
                else:
                    database.log_room('cmdj.add', client, client.area, target=c)
                    client.area.DJs.append(c)
                    client.area.broadcast_ooc(
                        '{} [{}] is DJ in this area now.'.format(
                            c.char_name, c.id))
        else:
            client.send_ooc('No targets found.')
    else:
        raise ArgumentError("You must specify a target. Use /cmdj <id>.")

def ooc_cmd_cm(client, arg):
    """
    Add a case manager for the current room.
    Usage: /cm <id>
    """
    if 'CM' not in client.area.evidence_mod and not client in client.area.owners and not client.is_mod:
        raise ClientError('You can\'t become a CM in this area')
    if len(client.area.owners) == 0 or client.is_mod:
        if len(arg) > 0:
            if client.is_mod:
                arg = arg.split(' ')
                for id in arg:
                    try:
                        id = int(id)
                        c = client.server.client_manager.get_targets(
                            client, TargetType.ID, id, False)[0]
                        if not c in client.area.clients:
                            raise ArgumentError(
                                'You can only \'nominate\' people to be CMs when they are in the area.'
                            )
                        elif c in client.area.owners:
                            client.send_ooc(
                                '{} [{}] is already a CM here.'.format(
                                    c.char_name, c.id))
                        else:
                            client.area.owners.append(c)
                            if client.area.evidence_mod == 'HiddenCM':
                                client.area.broadcast_evidence_list()
                            client.server.area_manager.send_arup_cms()
                            client.area.broadcast_ooc(
                                '{} [{}] is CM in this area now.'.format(
                                    c.char_name, c.id))
                            database.log_room('cm.add', client, client.area, target=c)
                    except:
                        client.send_ooc(
                            f'{id} does not look like a valid ID.')
            else:
                raise ClientError('You must be authorized to do that.')
        else:
            if client in client.area.owners:
                raise ArgumentError('You are already a CM in this area!')
            else:
                client.area.owners.append(client)
                if client.area.evidence_mod == 'HiddenCM':
                    client.area.broadcast_evidence_list()
                client.server.area_manager.send_arup_cms()
                client.area.broadcast_ooc('{} [{}] is CM in this area now.'.format(
                    client.char_name, client.id))
                database.log_room('cm.add', client, client.area, target=client, message='self-added')
    elif client in client.area.owners:
        if len(arg) > 0:
            arg = arg.split(' ')
        for id in arg:
            try:
                id = int(id)
                c = client.server.client_manager.get_targets(
                    client, TargetType.ID, id, False)[0]
                if not c in client.area.clients:
                    raise ArgumentError(
                        'You can only \'nominate\' people to be CMs when they are in the area.'
                    )
                elif c in client.area.owners:
                    client.send_ooc(
                        '{} [{}] is already a CM here.'.format(
                            c.char_name, c.id))
                else:
                    client.area.owners.append(c)
                    if client.area.evidence_mod == 'HiddenCM':
                        client.area.broadcast_evidence_list()
                    client.server.area_manager.send_arup_cms()
                    client.area.broadcast_ooc(
                        '{} [{}] is CM in this area now.'.format(
                            c.char_name, c.id))
                    database.log_room('cm.add', client, client.area, target=c)
            except:
                client.send_ooc(
                    f'{id} does not look like a valid ID.')
    else:
        raise ClientError('You must be authorized to do that.')


@mod_only(area_owners=True)
def ooc_cmd_uncm(client, arg):
    """
    Remove a case manager from the current area.
    Usage: /uncm <id>
    - "@" uncm's everyone on the server.
    """
    if client.is_mod:
        if arg == '@':
            for _, area in enumerate(client.server.area_manager.areas):
                if len(area.owners) > 0:
                    area.owners.clear()
                    area.DJs.clear()
            client.server.area_manager.send_arup_cms()
            client.area.broadcast_ooc("Server CMs cleared.")
            database.log_room('cm.clearAll', client, client.area, target=None)
            return
    
    if len(arg) > 0:
        arg = arg.split(' ')
    else:
        arg = [client.id]
    for id in arg:
        try:
            id = int(id)
            c = client.server.client_manager.get_targets(
                client, TargetType.ID, id, False)[0]
            if c in client.area.DJs:
                client.area.DJs.remove(c)
            if c in client.area.owners:
                client.area.owners.remove(c)
                client.server.area_manager.send_arup_cms()
                client.area.broadcast_ooc(
                    '{} [{}] is no longer CM in this area.'.format(
                        c.char_name, c.id))
                database.log_room('cm.remove', client, client.area, target=c)
            else:
                client.send_ooc(
                    'You cannot remove someone from CMing when they aren\'t a CM.'
                )
        except:
            client.send_ooc(
                f'{id} does not look like a valid ID.')

@mod_only()
def ooc_cmd_clear_cm(client, arg):
    """
    Removes all case managers from the current area.
    Usage: /clear_cm
    """
    client.area.owners = []
    client.area.DJs = []
    client.server.area_manager.send_arup_cms()
    client.area.broadcast_ooc("Area CMs cleared.")
    database.log_room('cm.clear', client, client.area, target=client)

# LEGACY
def ooc_cmd_setcase(client, arg):
    """
    Set the positions you are interested in taking for a case.
    (This command is used internally by the 2.6 client.)
    """
    args = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', arg)
    if len(args) == 0:
        raise ArgumentError('Please do not call this command manually!')
    else:
        client.casing_cases = args[0]
        client.casing_cm = args[1] == "1"
        client.casing_def = args[2] == "1"
        client.casing_pro = args[3] == "1"
        client.casing_jud = args[4] == "1"
        client.casing_jur = args[5] == "1"
        client.casing_steno = args[6] == "1"


# LEGACY
def ooc_cmd_anncase(client, arg):
    """
    Announce that a case is currently taking place in this area,
    needing a certain list of positions to be filled up.
    Usage: /anncase <message> <def> <pro> <jud> <jur> <steno>
    """
    # XXX: Merge with aoprotocol.net_cmd_casea
    if client in client.area.owners:
        if not client.can_call_case():
            raise ClientError(
                'Please wait 60 seconds between case announcements!')
        args = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', arg)
        if len(args) == 0:
            raise ArgumentError('Please do not call this command manually!')
        elif len(args) == 1:
            raise ArgumentError(
                'You should probably announce the case to at least one person.'
            )
        else:
            if not args[1] == "1" and not args[2] == "1" and not args[
                    3] == "1" and not args[4] == "1" and not args[5] == "1":
                raise ArgumentError(
                    'You should probably announce the case to at least one person.'
                )
            msg = '=== Case Announcement ===\r\n{} [{}] is hosting {}, looking for '.format(
                client.char_name, client.id, args[0])

            lookingfor = [p for p, q in
                zip(['defense', 'prosecutor', 'judge', 'juror', 'stenographer'], args[1:])
                if q == '1']

            msg += ', '.join(lookingfor) + '.\r\n=================='

            client.server.send_all_cmd_pred('CASEA', msg, args[1], args[2],
                                            args[3], args[4], args[5], '1')

            client.set_case_call_delay()

            log_data = {k: v for k, v in
                zip(('message', 'def', 'pro', 'jud', 'jur', 'steno'), args)}
            database.log_room('case', client, client.area, message=log_data)
    else:
        raise ClientError(
            'You cannot announce a case in an area where you are not a CM!')


@mod_only()
def ooc_cmd_blockwtce(client, arg):
    """
    Prevent a user from using Witness Testimony/Cross Examination buttons
    as a judge.
    Usage: /blockwtce <id>
    """
    if len(arg) == 0:
        raise ArgumentError('You must specify a target. Use /blockwtce <id>.')
    try:
        targets = client.server.client_manager.get_targets(
            client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must enter a number. Use /blockwtce <id>.')
    if not targets:
        raise ArgumentError('Target not found. Use /blockwtce <id>.')
    for target in targets:
        target.can_wtce = False
        target.send_ooc(
            'A moderator blocked you from using judge signs.')
        database.log_room('blockwtce', client, client.area, target=target)
    client.send_ooc('blockwtce\'d {}.'.format(
        targets[0].char_name))


@mod_only()
def ooc_cmd_unblockwtce(client, arg):
    """
    Allow a user to use WT/CE again.
    Usage: /unblockwtce <id>
    """
    if len(arg) == 0:
        raise ArgumentError(
            'You must specify a target. Use /unblockwtce <id>.')
    try:
        targets = client.server.client_manager.get_targets(
            client, TargetType.ID, int(arg), False)
    except:
        raise ArgumentError('You must enter a number. Use /unblockwtce <id>.')
    if not targets:
        raise ArgumentError('Target not found. Use /unblockwtce <id>.')
    for target in targets:
        target.can_wtce = True
        target.send_ooc(
            'A moderator unblocked you from using judge signs.')
        database.log_room('unblockwtce', client, client.area, target=target)
    client.send_ooc('unblockwtce\'d {}.'.format(
        targets[0].char_name))


@mod_only()
def ooc_cmd_judgelog(client, arg):
    """
    List the last 10 uses of judge controls in the current area.
    Usage: /judgelog
    """
    if len(arg) != 0:
        raise ArgumentError('This command does not take any arguments.')
    jlog = client.area.judgelog
    if len(jlog) > 0:
        jlog_msg = '== Judge Log =='
        for x in jlog:
            jlog_msg += f'\r\n{x}'
        client.send_ooc(jlog_msg)
    else:
        raise ServerError(
            'There have been no judge actions in this area since start of session.'
        )


@mod_only()
def ooc_cmd_evidlog(client, arg):
    """
    List the last 10 uses of the evidence panel in the current area.
    Usage: /evidlog
    """
    if len(arg) != 0:
        raise ArgumentError('This command does not take any arguments.')
    elog = client.area.evidlog
    if len(elog) > 0:
        elog_msg = '== Evidence Log =='
        for x in elog:
            elog_msg += f'\r\n{x}'
        client.send_ooc(elog_msg)
    else:
        raise ServerError(
    'There have been no evidence changes in this area since start of session.'
    )


def ooc_cmd_afk(client, arg):
    client.server.client_manager.toggle_afk(client)


def ooc_cmd_format(client, arg):
    '''
    Prints the available IC markdown for text formatting, including colors, alignment and actions.
    Usage: /format <option>
    '''
    formats = {
        "colors": "`Green`, ~Red~, |Orange|, 🤷Gray🤷, _Blue_, ºYellowº, №Pink№, √Cyan√",
        "align": "~~Center, ~>Right align, \\n New line",
        "action": "\s Shake, \\f Flash, { Slower text, } Faster text"
    }

    option = ['colors', 'align', 'action']

    if len(arg) == 0:
        client.send_ooc(f'All IC formatting options:\n{formats["colors"]}\n {formats["align"]}\n {formats["action"]}')
    else:
        choice = arg.lower()
        if choice in option:
            client.send_ooc(f'{arg.capitalize()} formatting:\n {formats[choice]}')
        else:
            client.send_ooc(f'Formatting options include: {option}')


def ooc_cmd_prompt(client, arg):
    """
    Generate a random prompt using a keyword.
    The generated prompt is not publicly broadcasted.
    Usage: /prompt <keyword>
    """
    if len(arg) == 0:
        raise ArgumentError('You must specify a keyword. Use /prompt <keyword>.')
    try:
        prmt_msg = f"You generated the following prompt from {arg}:\n"
        prmt_msg += generate_prompt(arg,client.server.prompts)
        client.send_ooc(prmt_msg)
    except:
        raise ArgumentError('unknown error while generating prompt')

def ooc_cmd_case(client, arg):
    """
    Generate a random case premise.
    The generated case is not publicly broadcasted.
    Usage: /case
    """
    case_prompt = 'murder'
    if len(arg) != 0:
        raise ArgumentError('This command does not take any arguments.')
    case_msg = generate_prompt(case_prompt,client.server.prompts)
    client.send_ooc(case_msg)

def ooc_cmd_asspull(client, arg):
    """
    Generate a random number of asspulls (default 1, max 5).
    The generated asspulls is not publicly broadcasted.
    Usage: /asspull, /asspull <number>
    """
    asspull_prompt = 'asspull'
    if len(arg) == 0:
        amount = 1
    else:
        try:
            amount = int(arg)
        except:
            raise ArgumentError('You must enter a number. Use /asspull <num>')
    if (amount > 5 or amount < 1) :
        raise ArgumentError('Number must be between 1 and 5')
    asspull_msg = generate_prompt(asspull_prompt,client.server.prompts,0,amount, True)
    client.send_ooc(asspull_msg)


def select_prompt(items, amount = 1, allowRepeat = False):
    #if items isn't a list, turn it into a list with the required amount of entries
    if not isinstance(items,list) :
        placeHolder = []
        for x in range(amount) :
            placeHolder.append(items)
        items = placeHolder
    #if length of items is less than the amount required, allowRepeat is forced on
    if len(items) < amount :
        allowRepeat = True

    #the part where it actually selects an item. Declares the output as a string
    output = ''
    #repeats the process for the amount of times requested
    for x in range(amount) :
        #text stores the choice while stuff is applied to it
        text = random.choice(items)
        #if this is the first entry, add it as is
        if x == 0 :
            output += str(text)
        #if this is the last entry, preface it with " and " 
        elif x + 1 == amount :
            output += ' and ' + str(text)
        #if it's an entry inbetween, preface it with a comma separator
        else:
            output += ', ' + str(text)

        #if allowRepeat is disabled, remove the entry from items for future pulls
        #particular placement of element in list *shouldn't* matter, but it needs to be fixed if it does
        if not allowRepeat :
            items.remove(text)

    return output

def generate_prompt(keyword, choiceKey, layer = 0, numSelects = 1 , repeat = False):
    #declare wildcard format string, and any modifiers needed
    wildCardStart = '?{'
    wildCardEnd = '}'
    numMod = '|'
    repMod = '%'
    rangeMod = '-'
    
    #attempt to load up choices from keyword
    try :
        
        #throws exception if list goes too deep
        if layer > 5:
            raise Exception()
        #load up lists of prompts from keyword into choices
        choices = choiceKey[keyword].copy()

        #set output prompt to a random selection from choices
        output = select_prompt(choices, numSelects, repeat)

        #run this code as long as a wildcard is found in the output prompt
        #more specifically, it checks if the starting string exists first
        #then if the last example of the ending string is after the earliest starting string
        while (output.find(wildCardStart) > -1) and (output.rfind(wildCardEnd) > output.find(wildCardStart)) :
            #grabs the wildcard from its formatting
            wildCard = output[output.find(wildCardStart):output.find(wildCardEnd,
                                                                     output.find(wildCardStart)) + len(wildCardEnd)]
            wildCard = wildCard[len(wildCardStart):(0-len(wildCardEnd))]
            #tells the program to stick to default values
            useDefSel = True
            useDefRep = True
            
            #if the wildcard contains a modifier for number
            if numMod in wildCard :
                useDefSel = False
                #splits the wildcard by the numMod string
                sep = wildCard.split(numMod,1)
                wildCard = sep[0]
                if repMod in sep[1] : #checks for the repeat modifier in the wildcard
                #since the repeat option is useless outside of mulitple options,
                #it doesn't check unless the number of choices is modified
                    useDefRep = False
                    sep = sep[1].split(repMod,1)
                    select = sep[0]
                else:
                    select = sep[1]

                if rangeMod in select :
                    low = int(select.split(rangeMod)[0])
                    high = int(select.split(rangeMod)[1])
                    select = random.choice(range(low,high))

                select = int(select)

            #generates a new prompt using the given keyword by recursively running generate_prompt
            if (useDefSel and useDefRep) :
                newPrompt = generate_prompt(wildCard, choiceKey, layer+1)
                full = wildCardStart + wildCard + wildCardEnd
            elif (not useDefSel and useDefRep) :
                newPrompt = generate_prompt(wildCard, choiceKey, layer+1, select)
                full = wildCardStart + wildCard + numMod + sep[1] + wildCardEnd
            else :
                newPrompt = generate_prompt(wildCard, choiceKey, layer+1, select, True)
                full = wildCardStart + wildCard + numMod + sep[0] + repMod + wildCardEnd

            #replaces a single instance of the wildcard with the new prompt
            output = str(output).replace(full, newPrompt, 1)
            
    #if an error occurs, return the keyword in uppercase
    except Exception as F:
        output = str(keyword).upper()

    return output

def ooc_cmd_keywords(client, arg):
    '''
    Prints the current keywords in prompt.yaml
    Usage: /keywords
    '''
    if len(arg) != 0:
        raise ArgumentError('This command does not take any arguments.')
    key_msg = "These are the current valid keywords: "
    key_msg += ', '.join(client.server.prompts.keys())
    client.send_ooc(key_msg)
        
    
def ooc_cmd_testimony(client, arg):
    """
    List the current testimony in this area.
    Usage: /testimony
    """
    if len(arg) != 0:
        raise ArgumentError('This command does not take any arguments.')
    testi = list(client.area.testimony.statements)
    if len(testi) <= 1:
        raise ServerError('There is no testimony in this area.')
    else:
        testi.pop(0)
        testi_msg = 'Testimony: '+ client.area.testimony.title
        i = 1
        for x in testi:
            testi_msg += f'\r\n{i}: '
            testi_msg += x[4]
            i = i + 1
        client.send_ooc(testi_msg)

@mod_only(area_owners=True)
def ooc_cmd_cleartesti(client, arg):
    """
    Clears the testimony list, deleting all statements.
    Very handy, since otherwise you'd have to rewrite the testimony with
    a 1-statement new one and remove that statement manually.
    For mods and CM use only to prevent abuse.
    Usage: /cleartesti
    """
    if len(arg) != 0:
        raise ArgumentError('This command does not take any arguments.')
    testi = list(client.area.testimony.statements)
    if len(testi) <= 1:
        raise ServerError('There is no testimony in this area.')
    else:
        client.area.testimony.statements = []
        client.area.testimony.title = ''
        client.send_ooc('You have cleared the testimony.')
        
