import datetime
import logging


def demo_job():
    print("demo_job")
    logging.info('[demo_job] running at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
