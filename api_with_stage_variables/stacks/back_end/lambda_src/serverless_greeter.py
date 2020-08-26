# -*- coding: utf-8 -*-


import datetime
import json
import logging
import os
import random
import time


class GlobalArgs:
    """ Global statics """
    OWNER = "Mystique"
    ENVIRONMENT = "production"
    MODULE_NAME = "greeter_lambda"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    RANDOM_SLEEP_ENABLED = os.getenv("RANDOM_SLEEP_ENABLED", False)
    RANDOM_SLEEP_SECS = int(os.getenv("RANDOM_SLEEP_SECS", 2))
    ANDON_CORD_PULLED = os.getenv("ANDON_CORD_PULLED", False)


def set_logging(lv=GlobalArgs.LOG_LEVEL):
    """ Helper to enable logging """
    logging.basicConfig(level=lv)
    logger = logging.getLogger()
    logger.setLevel(lv)
    return logger


# Initial some defaults in global context to reduce lambda start time, when re-using container
logger = set_logging()


def random_sleep(max_seconds=10):
    if bool(random.getrandbits(1)):
        logger.info(f"sleep_start_time:{str(datetime.datetime.now())}")
        time.sleep(random.randint(0, max_seconds))
        logger.info(f"sleep_end_time:{str(datetime.datetime.now())}")


def lambda_handler(event, context):

    logger.info(f"rcvd_evnt:{event}")
    stg_name = "NO-STAGE-VARIABLE-DEFINED"
    greetings_msg = "Hello from Miztiikal World, How is it going?"
    # greetings_msg = "Hello from Modernized Miztiikal World, How is it going?"

    if event.get("stageVariables"):
        stg_name = event.get("stageVariables").get("lambdaAlias")

    # random_sleep(GlobalArgs.RANDOM_SLEEP_SECS)
    return {
        "statusCode": 200,
        "body": (
            f'{{"message": "{greetings_msg}",'
            f'"api_stage":"{stg_name}",'
            f'"lambda_version":"{context.function_version}",'
            f'"ts": "{str(datetime.datetime.now())}"'
            f'}}'
        )
    }
