from globals import *
from pokemon_list import common_pokemon, common_pokemon_pd, legendery_pokemon_chance, legendery_pokemon
from pokemon_commands import commands
from pokemon_events import events
from numpy.random import choice
import collections
import time
import random
import re








def handle_command(userid, command_and_args, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    command = command_and_args[0]
    args = command_and_args[1:]
    if command in commands.keys():
        print(command)
        response = commands.get(command)(channel, userid, args)
        if response is not None:
            send_message(channel, response)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    global local_lock
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        rval = []
        for output in output_list:
            text = output.get('text')
            user = output.get('user')
            channel = output.get('channel')
            if output and text:
                steps = len(text)
                if user and str(user) != BOT_ID:
                    rval.append((user, ["steps", steps, local_lock], channel))
                if cmdkey == text.strip()[:len(cmdkey)]:
                    rval.append((user,
                            re.findall(r'(?:"[^"]*"|[^\s"])+',  text[len(cmdkey):].strip().lower()),
                            channel))
        return rval
    return []


def random_events():
    if random.random() < random_event_chance:
        probability_distribution, list_of_candidates = map(list, zip(*events))
        total_p = sum(probability_distribution)
        probability_distribution = [float(x)/total_p for x in probability_distribution]
        draw = choice(
            list_of_candidates,
            1,
            p=probability_distribution,
            replace=False
        )
        draw[0]()


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    load = commands.get("load")
    if load:
        load(None, None, None)
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        try:
            while True:
                for user, command, channel in parse_slack_output(slack_client.rtm_read()):
                    if command and channel:
                        handle_command(user, command, channel)
                random_events()
                time.sleep(READ_WEBSOCKET_DELAY)
        except Exception as e:
            save = commands.get("save")
            if save:
                save(None, None, None)
            raise e

    else:
        print("Connection failed. Invalid Slack token or bot ID?")
