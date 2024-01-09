import logging

from huey import SqliteHuey

run = SqliteHuey(filename="D:\\Code\\UCI_Class_Watcher\\app\\huey.db")

logging.getLogger("huey").setLevel(logging.DEBUG)


""" def load_tasks():
    from tasks import run_program

    _ = [run_program]


load_tasks() """