from slackclient import SlackClient
import os
import json

# starterbot's ID as an environment variable

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">:"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
local_lock = object()
cmdkey = "*"
userlist = {}
alowed_channel = []
value_set ={"random_event_chance": 0.005}
current_events = {}
pokedex = {}
egg_steps = {}
player_eggs = {}
player_combattents = {}
player_trade_requests = {}

class ConnectionError(Exception):
    pass

def send_message(channel, message):
    while True:
        try:
            slack_client.api_call("chat.postMessage", channel=channel,
                                          text=message, as_user=True)
            break
        except Exception, e:
            print(e)
        



                    

def get_user_name(userid):
    if str(userid) in userlist.keys():
        return userlist.get(str(userid))
    else:
        api_call = slack_client.api_call("users.list")
        #    print(api_call)
        if api_call.get('ok'):
            users = api_call.get('members')
            for user in users:
                if 'id' in user:
                    userlist[str(user["id"])] = str(user["name"])
            if userid in userlist.keys():
                return userlist.get(userid)
            else:
                raise ValueError("incorrect id user {} not found in {}".format(userid,userlist.keys()))
        else:
            raise ConnectionError(api_call)

def get_user_id(name):
    if str(name) in userlist.keys():
        return userlist.get(str(name))
    else:
        api_call = slack_client.api_call("users.list")
        #    print(api_call)
        if api_call.get('ok'):
            users = api_call.get('members')
            for user in users:
                if 'id' in user:
                    userlist[str(user["name"])] = str(user["id"])
            for _id in userlist.keys():
                if str(_id) in name or str(_id).upper() in name:
                    return userlist.get(_id)
            raise ValueError("incorrect id user {} not found in {}".format(name,userlist.keys()))
        else:
            raise ConnectionError(api_call)
