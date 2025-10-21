from time import sleep
import random

MIN_SLEEP_TIME = 0.05
MAX_SLEEP_TIME = 0.2

def wait_some_time(min_sleep=MIN_SLEEP_TIME, max_sleep=MAX_SLEEP_TIME):
    sleep(random.uniform(min_sleep, max_sleep))