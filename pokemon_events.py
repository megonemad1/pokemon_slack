from globals import *
from enum import Enum
from pokemon_list import PokemonEgg, get_random_pokemon
import random
import string

class EventType(Enum):
    pokemon = 0
    egg = 1


class EventData(object):
    def __init__(self, event_type, data):
        self.event_type = event_type
        self.data = data
def get_cap(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

def event_wild_pokemon():
    global current_events
    if alowed_channel:
        channel = random.choice(alowed_channel)
        current_event = current_events.get(channel)
        if current_event:
                print(current_event.__dict__)
                if current_event.event_type == EventType.pokemon:
                    c, poke = current_event.data
                    send_message(channel, "wild :{0}: ran away".format(poke.name))
                    current_events[channel] = None
                else:
                    print("not a poke_event")

        else:
            poke = get_random_pokemon()
            cap = get_cap(5)
            send_message(channel, "wild pokemon appeared :{0}: capture code {1}".format(poke.name,cap))
            current_events[channel] = EventData(EventType.pokemon,(cap, poke))
    else:
        print("no channels")

def event_find_egg():
    global current_events
    if alowed_channel:
        channel = random.choice(alowed_channel)
        current_event = current_events.get(channel)
        if current_event:
            if current_event.event_type == EventType.egg:
                send_message(channel, "you leave the egg behind")
                current_events[channel] = None
            else:
                print("not a egg_event")
        else:
            send_message(channel, "you see an egg on the floor")
            current_events[channel] = EventData(EventType.egg, PokemonEgg(get_random_pokemon(),random.randint(50,100)))
    else:
        print("no channels")


events = [(0.5, event_wild_pokemon), (0.1, event_find_egg)]

