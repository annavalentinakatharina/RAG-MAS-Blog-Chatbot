import sys
import warnings

from ba_ragmas_chatbot.crew import BaRagmasChatbot
from ba_ragmas_chatbot.chatbot import TelegramBot
from telegram.error import NetworkError

from src.ba_ragmas_chatbot import logger_config

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    try:
        logger = logger_config.get_logger("main")
        telegram_bot = TelegramBot()
        logger.info("run: Telegram bot created.")
        telegram_bot.start_bot()
        logger.info("run: Telegram bot started and shut down.")
        logger_config.shutdown()
    except NetworkError as e:
        print("No internet connection, please connect your device to a network and restart the program.")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        BaRagmasChatbot().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        BaRagmasChatbot().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        BaRagmasChatbot().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
