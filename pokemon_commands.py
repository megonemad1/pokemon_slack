from globals import *
from pokemon_events import EventType
from pokemon_list import legendery_pokemon, common_pokemon, resolve_damage
from collections import Counter
import pickle
import random
import re   
import os.path

def command_(channel, userid, args):
    pass

def command_pokedex(channel, userid, args):
        dex=pokedex.get(userid)
        if dex:
            rval ="===Pokedex==="
            for k,v in dex.items():
                rval+= "\n#{} :{}: caught: {}".format(k.poke_id, k.name, v)
            if len(dex.items())==len(common_pokemon)+len(legendery_pokemon):
                rval+="\nyou are a pokemon master"
            else:
                rval+="\n {0} caught".format(sum(dex.values()))
            return rval
        return "no pokemon registered"

def add_pokemon(_pokemon, userid):
    global legendery_pokemon
    dex_message = "new entry into the pokedex\n"
    dex = pokedex.get(userid)
    if dex:
        if dex.get(_pokemon):
            dex[_pokemon]+=1
            dex_message = ""
        else:
            dex.update({_pokemon: 1})
    else:
        pokedex.update({userid: {_pokemon: 1}})
    legendery_pokemon = [(0 if x == _pokemon else i, x) for i, x in legendery_pokemon]
    return (dex_message, _pokemon.name)

def command_catch(channel, userid, args):
    global current_events
    if current_events.get(channel) and current_events.get(channel).event_type == EventType.pokemon:    
        c_event = current_events[channel].event_type
        cap, _pokemon = current_events[channel].data
        print(cap)
        print(args)
    	if len(args) >=1 and cap == args[0].upper():
                current_events[channel] = None
                return "{1}:{2}: was caught by {0}".format(get_user_name(userid), *add_pokemon(_pokemon, userid))
        else:
            return "capture dosnt match"
    return "no pokemon to catch"


def command_grab(channel, userid, args):
    global player_eggs, egg_steps
    if current_events.get(channel):    
        c_event = current_events[channel].event_type
        thing = current_events[channel].data
        if c_event == EventType.egg:
            player_egg = player_eggs.get(userid)
            if player_egg:
                return "you cant hold more than one egg"
            else:
                steps = egg_steps.get(userid)
                if steps:
                    thing.steps += steps
                player_eggs[userid] = thing
                current_events[channel] = None
                return "{} picked up the egg".format(get_user_name(userid))
        else:
            return "you cant grab that!"
    else:
        return "there is nothing to grab!"


    return "no pokemon to catch"
def command_steps(channel, userid, args):
    global local_lock, player_eggs, egg_steps
    try:
        steps, lock = args
        if local_lock is lock:
            if userid in egg_steps.keys():
                egg_steps[userid]+=steps
            else:
                egg_steps[userid]=steps
            player_steps = egg_steps.get(userid)
            egg = player_eggs.get(userid)
            if egg and player_steps:
                if egg.steps < player_steps:
                    _pokemon = egg.pokemon
                    player_eggs[userid] = None
                    return "{1}:{2}: Hatched From {0}'s egg".format(get_user_name(userid), *add_pokemon(_pokemon, userid))
    except Exception:
        steps= egg_steps.get(userid)
        if steps:
            return "total: {}".format(steps)

def command_add(channel, userid, args):
    if channel not in alowed_channel:
        alowed_channel.append(channel)
        current_events[channel] = None
        return "putting out poke'blocks"
    else:
        return "the pokemon are here what more do you want from me!"

def command_remove(channel, userid, args):
    alowed_channel.remove(channel)
    current_events[channel] = None
    return "spraying repels"

def command_info(channel, userid, args):
    return "prefix the folowing command s with *\n"+"\n".join(commands.keys())

def command_trade(channel, userid, args):
    global pokedex, player_trade_requests
    if len(args)==3:
        my_dex=pokedex.get(userid)
        offer, person, request = args
        offer = re.findall(r":(.*?):",offer)
        request = re.findall(r":(.*?):", request)
        poke_offers = []
        if my_dex:
            for p,v in my_dex.items():
                if p.name in offer and v > 0:
                    poke_offers.append(p)
            print(poke_offers)
            print(offer)
            if len(poke_offers) != len(offer):   
                return "you do not have the pokemon to offer"
            print(person)
            person = re.findall(r"<@(.*?)>", person)
            if person:
                person = get_user_id(person[0])
                print(person)
                print(pokedex.keys())
                other_dex=pokedex.get(person)
                if other_dex:
                    poke_request = []
                    for p,v in other_dex.items():
                        if p.name in request and v > 0:
                            poke_request.append(p)
                    if len(poke_request) != len(offer):  
                        return "they do not have the pokemon to offer"
                    other_requests = player_trade_requests.get(person)
                    if other_requests:
                        other_requests[userid] = (poke_offers,userid,poke_request)
                    else:
                        player_trade_requests[person]={userid:(poke_offers,userid,poke_request)}
                    return "making trade offer"
                else:
                    return "other person does not have any pokemon"
    else:
        return "incorrect trade offer, expected: trade {offered} @person {request}"


def command_resolve_trade(channel, userid, args):
    global pokedex, player_trade_requests
    try:
        if len(args) == 2:
            my_dex=pokedex.get(userid)
            person, result = args
            try:
                person = get_user_id(person)
            except ValueError:
                return "{} is not a person".format(person)
            requests = player_trade_requests.get(userid)  
            if result == "accept":
                print("accept")
                print(player_trade_requests)
                print(person)
                if requests:
                    request = requests.get(person)
                    if request:
                        print(request)
                        poke_offer,other_userid,poke_request = request
                        other_dex = pokedex.get(other_userid)
                        poke_offers_bag = Counter(poke_offer)
                        poke_request_bag = Counter(poke_request)
                        if other_dex:
                            for o,c in poke_offers_bag.items():
                                p = other_dex.get(o)
                                if not p or p<c:
                                    return "the trade is no longer valid"
                        my_dex = pokedex.get(userid)
                        if my_dex:
                            for o,c in poke_request_bag.items():
                                p = my_dex.get(o)
                                if not p or p<c:
                                    return "the trade is no longer valid"
                        for o,c in poke_offers_bag.items():
                            other_dex[o]-=c
                            if o in my_dex.keys():
                                my_dex[o] += c
                            else:
                                my_dex[o] = c
                        for o,c in poke_request_bag.items():
                            my_dex[o]-=c
                            if o in other_dex.keys():
                                other_dex[o] += c
                            else:
                                other_dex[o] = c
                        return "trade complete"
            elif result == "decline":
                requests[userid] = None
    except Exception:
        return "usage: *trade @person [accept/decline]"
                
def command_save(channel, userid, args):
    with open('userlist.pickle', 'w') as f:
        pickle.dump(userlist, f)

    with open('alowed_channel.pickle', 'w') as f:
        pickle.dump(alowed_channel, f)

    with open('value_set.pickle', 'w') as f:
        pickle.dump(value_set, f)

    with open('current_events.pickle', 'w') as f:
        pickle.dump(current_events, f)

    with open('pokedex.pickle', 'w') as f:
        pickle.dump(pokedex, f)

    with open('egg_steps.pickle', 'w') as f:
        pickle.dump(egg_steps, f)
 
    with open('player_eggs.pickle', 'w') as f:
        pickle.dump(player_eggs, f) 

    with open('player_trade_requests.pickle', 'w') as f:
        pickle.dump(player_trade_requests, f)

    with open('player_combattents.pickle', 'w') as f:
        pickle.dump(player_combattents, f)
      
    with open('murder_meater.pickle', 'w') as f:
        pickle.dump(murder_meater, f)
        
    print("saved")

def command_load(channel, userid, args):
    global value_set, player_trade_requests, player_eggs, egg_steps, pokedex, current_events, alowed_channel, userlist, player_combattents
    try:
        fname='userlist.pickle'
        if os.path.isfile(fname):
            with open(fname) as f:
                userlist.update(pickle.load(f))
        else:
            print("no file " + fname)
    except Exception as e:
        print(e)
        
    try:
        fname='murder_meater.pickle'
        if os.path.isfile(fname):
            with open(fname) as f:
                murder_meater.update(pickle.load(f))
        else:
            print("no file " + fname)
    except Exception as e:
        print(e)

    try:            
        fname='alowed_channel.pickle'
        if os.path.isfile(fname):
            with open(fname) as f:
                alowed_channel += [x for x in pickle.load(f) if x not in alowed_channel]
                print(alowed_channel)
        else:
            print("no file " + fname)
    except Exception as e:
        print(e)
        
    try:  
        fname='value_set.pickle'
        if os.path.isfile(fname):
            with open(fname) as f:
                value_set.update(pickle.load(f))
        else:
            print("no file " + fname)
    except Exception as e:
        print(e)
        
    try:  
        fname='current_events.pickle'
        if os.path.isfile(fname):
            with open(fname) as f:
                current_events.update(pickle.load(f))
        else:
            print("no file " + fname)
    except Exception as e:
        print(e)
        
    try:  
        fname='pokedex.pickle'
        if os.path.isfile(fname):
            with open(fname) as f:
                pokedex.update(pickle.load(f))
        else:
            print("no file " + fname)
    except Exception as e:
        print(e)
        
    try:  
        fname='egg_steps.pickle'
        if os.path.isfile(fname):
            with open(fname) as f:
                egg_steps.update(pickle.load(f))
        else:
            print("no file " + fname)
    except Exception as e:
        print(e)
        
    try:  
        fname='player_eggs.pickle'
        if os.path.isfile(fname):
            with open(fname) as f:
                player_eggs.update(pickle.load(f))
        else:
            print("no file " + fname)
    except Exception as e:
        print(e)
        
    try:  
        fname='player_trade_requests.pickle'
        if os.path.isfile(fname):
            with open(fname) as f:
                player_trade_requests.update(pickle.load(f))
        else:
            print("no file " + fname)
    except Exception as e:
        print(e)
        
    try:  
        fname = "player_combattents.pickle"
        if os.path.isfile(fname):
            with open(fname) as f:
                player_trade_requests.update(pickle.load(f))
        else:
            print("no file " + fname)
    except Exception as e:
        print(e)
    print("loaded")


def command_set_encounter(channel, userid, args):
    global value_set
    if len(args)>=1:
        try:
            newval=float(str(args[0]))
        except Exception as e:
            print(args)
            print(e)
            return "the new value should be 0<x<=1"
        if newval > 0 and newval <=1:
            oldval= value_set.get("random_event_chance")
            value_set["random_event_chance"]=newval 
            return "set encounter rate from {} to {}".format(oldval, newval)
    return "you need a float param"
    
def command_set_combattent(channel, userid, args):
    global player_combattents
    if len(args)>=1:
        my_dex = pokedex.get(userid)
        if my_dex:
            for k,v in my_dex.items():
                if k.name in args[0] and v>0:
                    combattent = k
                    return ":{}: is ready for battle".format(k.name)
                else:
                    return "you dont have that pokemon"

def command_challange(channel, userid, args):
    global player_combattents
    if len(args)>=1:
        try:
            oponent = get_user_id(args[0])
            oponent_pokemon = player_combattents.get(get_user_id(oponent))
        except ValueError:
            return "{} is not recognised".format(args[0])
        my_pokemon = player_combattents.get(userid)
        if oponent_pokemon and my_pokemon:
            my_health = 20
            oponent_helth = 20
            while my_health>0 and oponent_helth>0:
                oponent_helth -= resolve_damage(my_pokemon, oponent_pokemon)
                my_helth -= resolve_damage(oponent_pokemon, my_pokemon)
            if my_health<=0 and oponent_helth<=0:
                return "draw"
            else:
                if my_health<=0:
                    return "chalenger lost"
                if oponent_helth <=0:
                    return "chalenger won"
            print("err no one won")
        else:
            return "you both need to ready a pokemon"

def command_tackle(channel, userid, args):
    global current_events, murder_meater
    if current_events.get(channel) and current_events.get(channel).event_type == EventType.pokemon:    
        c_event = current_events[channel].event_type
        cap, _pokemon = current_events[channel].data
        if random.random() < 0.5:
            current_events[channel] = None
            if murder_meater.get(userid):
                murder_meater[userid] +=1
            else:
                murder_meater[userid] =1
            return "{0} used tackle :{1}: fainted".format(get_user_name(userid), _pokemon.name)
        else:
            return "{0} used tackle :{1}:, {0} missed".format(get_user_name(userid), _pokemon.name)
    return "no pokemon to tackle"

def command_kill_count(channel, userid, args):
    global murder_meater
    steps= murder_meater.get(userid)
    if steps:
        return "total: {}".format(steps)


commands = {"killcount": command_kill_count, "tackle":command_tackle, "ready":command_set_combattent,"challenge": command_challange,"set_encounter_rate": command_set_encounter, "save": command_save, "load": command_load, "trade": command_resolve_trade, "mktrade": command_trade, "grab": command_grab,"info": command_info, "add": command_add, "remove": command_remove, "steps": command_steps, "catch": command_catch, "pokedex":command_pokedex}
