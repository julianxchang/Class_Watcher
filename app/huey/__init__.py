import logging

from huey import SqliteHuey

run = SqliteHuey(filename="C:\\Users\\julia\\Documents\\testapp\\app\\huey.db")

logging.getLogger("huey").setLevel(logging.DEBUG)


""" def load_tasks():
    from tasks import run_program

    _ = [run_program]


load_tasks() """