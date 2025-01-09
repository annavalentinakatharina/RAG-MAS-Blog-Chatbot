import os

import yaml
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff

from src.ba_ragmas_chatbot import logger_config


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class BaRagmasChatbot():
	"""BaRagmasChatbot crew"""

	def __init__(self, tools):
		self.tools = tools
		self.logger = logger_config.get_logger("crew ai")

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	tools = []
	current_dir = os.path.dirname(os.path.abspath(__file__))
	yaml_file = os.path.join(current_dir, "config", "configs.yaml")
	with open(yaml_file, 'r') as file:
		config = yaml.safe_load(file)
	llm= config['agents']['llm']
	url= config['agents']['url']

	@before_kickoff
	def before_kickoff_function(self, inputs):
		"""What happens before the crew is started"""
		print(f"Before kickoff function with inputs: {inputs}")
		self.logger.info(f"before_kickoff_function: Called with inputs: {inputs}")
		return inputs

	@after_kickoff
	def after_kickoff_function(self, result):
		"""What happens after the crew is finished"""
		print(f"After kickoff function with result: {result}")
		self.logger.info(f"after_kickoff_function: Called with result: {result}")
		return result

	@agent
	def researcher(self) -> Agent:
		"""The researcher agent which corresponds to the researcher specified in the agents.yaml."""
		self.logger.info("researcher: Researcher Agent created based on agents.yaml[researcher] with llm ollama/llama3.1:8b-instruct-q8_0.")
		return Agent(
			config=self.agents_config['researcher'],
			llm=LLM(model=self.llm, base_url=self.url),
			tools = self.tools,
			max_retry_limit = 2,
			verbose=True
		)

	@agent
	def editor(self) -> Agent:
		"""The editor agent which corresponds to the editor specified in the agents.yaml."""
		self.logger.info("editor: Editor Agent created based on agents.yaml[editor] with llm ollama/llama3.1:8b-instruct-q8_0.")
		return Agent(
			config=self.agents_config['editor'],
			llm=LLM(model=self.llm, base_url=self.url),
			max_retry_limit=2,
			verbose=True
		)

	@agent
	def writer(self) -> Agent:
		"""The writer agent which corresponds to the writer specified in the agents.yaml."""
		self.logger.info("writer: Writer Agent created based on agents.yaml[writer] with llm ollama/llama3.1:8b-instruct-q8_0.")
		return Agent(
			config=self.agents_config['writer'],
			llm=LLM(model=self.llm, base_url=self.url),
			max_retry_limit=2,
			verbose=True
		)

	@agent
	def proofreader(self) -> Agent:
		"""The proofreader agent which corresponds to the proofreader specified in the agents.yaml."""
		self.logger.info("proofreader: Proofreader Agent created based on agents.yaml[proofreader] with llm ollama/llama3.1:8b-instruct-q8_0.")
		return Agent(
			config=self.agents_config['proofreader'],
			llm=LLM(model=self.llm, base_url=self.url),
			max_retry_limit=2,
			verbose=True
		)

	# @agent
	# def factchecker(self) -> Agent:
	#"""The factchecker agent which corresponds to the factchecker specified in the agents.yaml."""
	#	self.logger.info("factchecker: Factchecker Agent created based on agents.yaml[factchecker] with llm ollama/llama3.1:8b-instruct-q8_0.")
	# 	return Agent(
	# 		config=self.agents_config['factchecker'],
	# 		llm=LLM(model="ollama/llama3.1:8b-instruct-q8_0", base_url="http://localhost:11434"),
	# 		#tools=self.tools,
	# 		verbose=True
	# 	)

	@task
	def research_task(self) -> Task:
		"""The research task which corresponds to the research task specified in the tasks.yaml."""
		self.logger.info("research_task: Research task created based on tasks.yaml[research_task].")
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def editor_task(self) -> Task:
		"""The editor task which corresponds to the editor task specified in the tasks.yaml."""
		self.logger.info("editor_task: Editor task created based on tasks.yaml[editor_task].")
		return Task(
			config=self.tasks_config['editor_task'],
		)

	@task
	def writer_task(self) -> Task:
		"""The writer task which corresponds to the writer task specified in the tasks.yaml."""
		self.logger.info("writer_task: Writer task created based on tasks.yaml[writer_task].")
		return Task(
			config=self.tasks_config['writer_task'],
		)

	@task
	def proofreader_task(self) -> Task:
		"""The proofreader task which corresponds to the proofreader task specified in the tasks.yaml."""
		self.logger.info("proofreader_task: Proofreader task created based on tasks.yaml[proofreader_task].")
		return Task(
			config=self.tasks_config['proofreader_task'],
		)

	# @task
	# def factchecker_task(self) -> Task:
	#	"""The factchecker task which corresponds to the factchecker task specified in the tasks.yaml."""
	#	self.logger.info("factchecker_task: Factchecker task created based on tasks.yaml[factchecker_task].")
	# 	return Task(
	# 		config=self.tasks_config['factchecker_task'],
	# 	)

	@crew
	def crew(self) -> Crew:
		"""Creates the BaRagmasChatbot crew"""
		self.logger.info(f"crew: Crew is created with agents: {str(self.agents)} \nand tasks: {str(self.tasks)}")
		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
		)