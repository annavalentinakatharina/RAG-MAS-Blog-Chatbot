# BaRagmasChatbot Crew

Welcome to the BaRagmasChatbot bachelor thesis project! The goal of this project is to provide a local, open-source, multi-agent tool that can be easily adapted to a new use case. 
For the Multi-Agent System and RAG, it uses the framework [crewAI](https://crewai.com) and as a user interface, the [python-telegram-bot](https://python-telegram-bot.org).

## Installation

Prerequisites:
- Python >=3.10 <=3.13
- Pip and virtual environment support

This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, but also offers a requirements.txt for .venv creation.

First, clone this git repository:

```bash
git clone https://github.com/annavalentinakatharina/RAG-MAS-Blog-Chatbot.git
cd RAG-MAS-Blog-Chatbot
```

Secondly, create your .venv and activate it:

```bash
python -m venv venv
source venv/bin/activate
```

Thirdly, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:
```bash
pip install -r requirements.txt
```

The next step is downloading the ollama model and the embedding model (If you want to use a different model, go to *How to change your model*)
```bash
ollama pull llama-3.1:8B-instruct-q8_0
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

This command starts the telegram chatbot, which can then be accessed via telegram and used to start the multi-agent-RAG system.

