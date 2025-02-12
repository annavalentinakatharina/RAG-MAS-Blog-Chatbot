# Adaptation Manual
As one of the requirements of the project is that it can easily be adapted, here is a detailed instruction manual on how to adapt each part to a new use case/a new preference.
## Multi-Agent System Adaptation
To adapt the multi-agent system to a new use case, the files `agents.yaml`, `tasks.yaml` and `crew.py` need to be changed.
- Firstly, go to `agents.yaml` and replace the existing agents with the new ones, each including a role, a goal and a backstory.
- Secondly, go to `tasks.yaml` and replace the existing tasks with new ones, at least one per agent. Each should include a description, an expected_output and an agent.
- Thirdly, go to `crew.py` and change the functions that return either an agent or a task, like `researcher()`. Here, change the name of the function, the text of the logger message and the corresponding YAML agent or task. This has to be done until all tasks are mentioned in the `crew.py`.  
  Remove all unnecessary agent and task functions.

Now, the multi-agent system is adapted to your new use case!

## How to change the model
### Change to a different Ollama model
#### Change the LLM
- Firstly, download the new Ollama model:
```bash
ollama pull {new_model}
```
- Next, go to `config.yaml`.  
- Here, first go to the line `llm: ollama/llama3.1:8b-instruct-q8_0`. Here, replace `llama3.1:8b-instruct-q8_0` with your model of choice, e.g. `llama3.2`.  
- Next, go to the line `name: llama3.1:8b-instruct-q8_0`. Here, again replace `llama3.1:8b-instruct-q8_0` with your model of choice, e.g. `llama3.2`.
#### Change the embedding model
- First, download the new embedding model:
```bash
ollama pull {new_model}
```
- Next, go to the file `configs.yaml`.  
- Go to the line `name: mxbai-embed-large`. Here, replace `mxbai-embed-large` with your embedding model of choice.  

### Change to a non-Ollama model

- Firstly, change the same lines as when changing to a Ollama LLM, but also change the `provider` and remove the `url` attribute.  
- Secondly, go to all the agents in `crew.py` and change the `llm` attribute, where the `base_url` needs to be removed.  
- Thirdly, go to `chatbot.py`, and go to the functions `addWebsite()`, `addPDF()`, `addDOCX()` and `addTxt()`. Here, go to the most indented part, where the attributes `model` and `url` are situated, and remove the `url` attribute.  
- Next, if an API key is necessary to access the model, go to the `.env` file in the root folder, and add `OPENAI_API_KEY={key}` as a third line and add your key instead of `{key}`.

## RAG Adaptation
To adapt the RAG part to a new input type, a new tool adding function needs to be implemented in the `chatbot.py`. To see all possible input types, please go to the Tools list on https://docs.crewai.com/introduction and decide on one.  
To now explain how to add a new input type in detail, let's copy the function `addWebsite(url)`, paste it to the end of the file and adapt it to `addCSV(csv)`, which can be used to add a `CSVSearchTool`.  
Start by looking at the online documentation, and find out what additional input variable is necessary for this tool. In the case of `CSVSearchTool`, it is `csv='path/to/your/csvfile.csv`.  
Now, change the following lines in the pasted function `addCSV(csv)`:
- Line 1: Rename the function to `addCSV` and the `url` to `csv`.
- Line 3: Replace `WebsiteSearchTool` with `CSVSearchTool`.
- Line 4: Replace `website` with `csv`, and `url` with `csv`.
- Line 23: In the log message, replace `Website` with `CSV`, and `{url}` with `{csv}`.  

Additionally, the function that receives the input also needs to be changed. To do this, go to the `VALID_MIME_TYPES` and add the new mime type.  
Now, go to the function `document()`, and extend the match-case to your new mime type, with the new tool being added as a consequence.


## Telegram Chatbot Adaptation
To adapt the telegram chatbot to a new use case, the conversation needs to be changed. To do this, please do the following steps in `chatbot.py`:
- First, go to line 15, remove all unwanted states and add all new states, and change the number at the end to the new amount of states.
- Next, decide on an order the questions should be asked in. When creating the functions in the next task, always ask for the next state at the end and return the next state.
- Next, for all new functions, let's look at the way a function should be changed by first copying `tone()` and pasting it below. Now, change the following lines:
  -	Line 1: Change the function name to the new function name, e.g. `confidentiality()`
  - Line 2: Change the commented description to the new state
  - Line 7: Change the first word in the log message from `tone` to the new function name
  - Line 9: Change `tone` to the new state, e.g. `confidentiality`
  - Line 10: Change the response to asking for the new state in the chosen order, e.g. additional information.
  - Line 12: Change the first word in the log message from `tone` to the new function name
  - Line 13: Change `WEBSITE` to the new next state, e.g.`ADDITIONAL` (information)
  - Line 15: Change the first word in the log message from `tone` to the new function name
  - Line 16: Change `tone` to the new state
  - Line 17: Change the response to asking for the new state in the chosen order, e.g. additional information.
  - Line 19: Change the first word in the log message from `tone` to the new function name
  - Line 20: Change `WEBSITE` to the new next state, e.g. `ADDITIONAL` (information)
  - Line 23: Change `tone` to the new state
  - Line 24: Change the first word in the log message from `tone` to the new function name
  - Line 25: Change `TONE` to the new state, e.g. `CONFIDENTIALITY`
- Do this for all new functions and remove the ones that you don't want anymore, but please refrain from changing the logic of `website()`, `document()`, `no_document()`, `start_configuration()` and `confirm()`, as they are essential for chatbot functionality.
- Next, check the order everywhere and make sure that all functions return the correct next state, especially `start_configuration()`, where the first state needs to be called, and `confirm()`, which should be the last state.
- Now, adapt the function `start_bot`, where the `ConversationHandler` should include just the new states and their corresponding function.  

To adapt the fallback functions, change the individual functions, and if you want to add or remove any, change the `fallbacks` in the `ConversationHandler`.