import datetime

def timeToMilliseconds(time_str):
    """Get seconds from time."""
    t = time_str.split('.')
    secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(t[0].split(':'))))
    return secs * 1000 + int(t[1])

def millisecondsToTime(milliseconds):
    secs = str(datetime.timedelta(milliseconds=milliseconds))
    if milliseconds < 36000000:
        secs = '0' + secs
    if not '.' in secs:
        secs = secs + '.000000'
    secs = secs.replace('.', ',')
    return secs[:-3]
