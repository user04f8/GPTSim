from datetime import datetime
import importlib

from termcolor import cprint

import aioconsole

def removeall(s: str, cs: str):
    for c in cs:
        s = s.replace(c, '')
    return s

log_salt = removeall(str(datetime.now()), ' -:.')
LOG_FNAME = f'logs/debug_{log_salt}.txt'
print(f'Saving logs to {LOG_FNAME}')

def debug_log(msg):
    cprint(msg, "dark_grey")
    with open(LOG_FNAME, 'a+') as f:
        f.write(str(msg) + '\n')

def warn_log(msg):
    msg = 'WARN: ' + msg
    cprint(msg, "yellow")
    with open(LOG_FNAME, 'a+') as f:
        f.write(str(msg) + '\n')


def threadsafe_start_pygame_loop(init_env, *events):
    render = importlib.import_module('render')  # necessary since render.py imports pygame which is not threadsafe
    render.PygameView(init_env).loop(*events)


async def await_text_input():
    text = await aioconsole.ainput("> ")
    return text
