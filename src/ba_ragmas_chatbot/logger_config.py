import logging

logging.basicConfig(
    level=logging.WARN,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        #logging.StreamHandler()
    ]
)

def get_logger(name):
    return logging.getLogger(name)

def shutdown():
    logging.shutdown()
