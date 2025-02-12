# BaRagmasChatbot Crew

Welcome to the BaRagmasChatbot bachelor thesis project! The goal of this project is to provide a local, open-source, multi-agent tool that can be easily adapted to a new use case. 
For the Multi-Agent System and RAG, it uses the framework [crewAI](https://crewai.com) and as a user interface, the [python-telegram-bot](https://python-telegram-bot.org).

## Installation
This is a tutorial for running it on a Mac. If you are using it on a Windows, please adjust the commands accordingly.  

Prerequisites:
- Python >=3.10 <=3.13
- Pip and virtual environment support

This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, but also offers a requirements.txt for dependency installation.

First, clone this git repository:

```bash
git clone https://github.com/annavalentinakatharina/RAG-MAS-Blog-Chatbot.git
cd RAG-MAS-Blog-Chatbot
```

Secondly, create your .venv and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Next, navigate to your project directory and install the dependencies:
```bash
pip install -r requirements.txt
```
Now, download the ollama cli tool and run it. After running serve, wait a few seconds and then press enter: 
```bash
brew install ollama
```
```bash
ollama serve &
```
The next step is downloading the ollama model and the embedding model (If you want to use a different model, go to *How to change your model*)
```bash
ollama pull llama3.1:8b-instruct-q8_0
```
```bash
ollama pull mxbai-embed-large
```

### Basic Customizing

Add your telegram chatbot token into the `configs.yaml` file, replacing `{your_token}`.  
To receive your telegram chatbot token, you first need to register your chatbot using the BotFather-bot on telegram.  
This also shows you where you can access your chatbot once it is running.

## Running the Project

To kickstart the chatbot, run this from the root folder:

```bash
crewai run
```

This command starts the telegram chatbot, which can then be accessed via Telegram and used to start the multi-agent-RAG system.  
To stop the running chatbot, use `Ctrl+C` in the CLI.

