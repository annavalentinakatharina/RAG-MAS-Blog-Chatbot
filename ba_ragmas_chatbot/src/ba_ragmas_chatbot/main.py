#!/usr/bin/env python
import sys
import warnings

from ba_ragmas_chatbot.crew import BaRagmasChatbot
from ba_ragmas_chatbot.chatbot import TelegramBot

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    telegram_bot = TelegramBot()
    telegram_bot.start_bot()
    # topic = input("What should the blog article be about?\n")
    # length = input("What length should the blog article be about?\n")
    # information_level = input("What information level should the blog article be about?\n")
    # language_level = input("What language level should the blog article be about?\n")
    # tone = input("What tone should the blog article have?\n")
    # language = input("What language should the blog article be about?\n")
    # bot = BaRagmasChatbot()
    # bot.addWebsite(input("Give me a link to the topic!"))
    # inputs = {
    #     'topic': topic,
    #     'length': length,
    #     'information_level': information_level,
    #     'language_level': language_level,
    #     'tone': tone,
    #     'language': language
    # }
    # bot.crew().kickoff(inputs=inputs)


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
