import logging

logger = logging.getLogger('cloudfunctions.googleapis.com%2Fcloud-functions')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
