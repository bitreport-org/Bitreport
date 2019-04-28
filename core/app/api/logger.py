from flask import request, g
import colors
import time


def create_msg(response):
    if request.path == '/favicon.ico':
        return colors.color('/favicon.ico', 'yellow')
    elif request.path.startswith('/static'):
        return colors.color('/static', 'yellow')

    now = time.time()
    duration = round(now - g.start, 2)
    args = dict(request.args)

    query = "/ "
    if args:
        query = "?"
        for k, v in args.items():
            query += f'{k}={v}&'

    query = query[:-1]
    msg = f'{request.method} {request.path}{query} {response.status_code} {duration}s'

    if response.status_code < 300:
        return colors.color(msg, 'green')
    elif response.status_code < 400:
        return colors.color(msg, 'purple')
    elif response.status_code < 500:
        return colors.color(msg, 'yellow')
    else:
        return colors.color(msg, 'red')

