import logging

from bootstrap.scheduler import create_scheduler

scheduler = create_scheduler()

if __name__ == "__main__":
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler will shutdown...")
        scheduler.shutdown()
