from datetime import datetime

def removeall(s: str, cs: str):
    for c in cs:
        s = s.replace(c, '')
    return s

log_salt = removeall(str(datetime.now()), ' -:.')
LOG_FNAME = f'logs/debug_{log_salt}.txt'
print(f'Saving logs to {LOG_FNAME}')

def debug_log(msg):
    with open(LOG_FNAME, 'a+') as f:
        f.write(str(msg) + '\n')