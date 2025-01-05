from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class BaRagmasChatbot():
	"""BaRagmasChatbot crew"""

	def __init__(self, tools):
		print("Intializing BaRagmasChatbot")
		self.tools = tools

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	tools = []

	@before_kickoff
	def before_kickoff_function(self, inputs):
		print(f"Before kickoff function with inputs: {inputs}")
		return inputs

	@after_kickoff
	def after_kickoff_function(self, result):
		print(f"After kickoff function with result: {result}")
		return result

	@agent
	def researcher(self) -> Agent:
		"""The researcher agent which corresponds to the researcher specified in the agents.yaml."""
		return Agent(
			config=self.agents_config['researcher'],
			llm=LLM(model="ollama/llama3.1:8b-instruct-q8_0", base_url="http://localhost:11434"),
			tools = self.tools,
			verbose=True
		)

	@agent
	def editor(self) -> Agent:
		"""The editor agent which corresponds to the editor specified in the agents.yaml."""
		return Agent(
			config=self.agents_config['editor'],
			llm=LLM(model="ollama/llama3.1:8b-instruct-q8_0", base_url="http://localhost:11434"),
			verbose=True
		)

	@agent
	def writer(self) -> Agent:
		"""The writer agent which corresponds to the writer specified in the agents.yaml."""
		return Agent(
			config=self.agents_config['writer'],
			llm=LLM(model="ollama/llama3.1:8b-instruct-q8_0", base_url="http://localhost:11434"),
			verbose=True
		)

	@agent
	def proofreader(self) -> Agent:
		"""The proofreader agent which corresponds to the proofreader specified in the agents.yaml."""
		return Agent(
			config=self.agents_config['proofreader'],
			llm=LLM(model="ollama/llama3.1:8b-instruct-q8_0", base_url="http://localhost:11434"),
			verbose=True
		)

	# @agent
	# def factchecker(self) -> Agent:
	#"""The factchecker agent which corresponds to the factchecker specified in the agents.yaml."""
	# 	return Agent(
	# 		config=self.agents_config['factchecker'],
	# 		llm=LLM(model="ollama/llama3.1:8b-instruct-q8_0", base_url="http://localhost:11434"),
	# 		#tools=self.tools,
	# 		verbose=True
	# 	)

	@task
	def research_task(self) -> Task:
		"""The research task which corresponds to the research task specified in the tasks.yaml."""
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def editor_task(self) -> Task:
		"""The editor task which corresponds to the editor task specified in the tasks.yaml."""
		return Task(
			config=self.tasks_config['editor_task'],
		)

	@task
	def writer_task(self) -> Task:
		"""The writer task which corresponds to the writer task specified in the tasks.yaml."""
		return Task(
			config=self.tasks_config['writer_task'],
		)

	@task
	def proofreader_task(self) -> Task:
		"""The proofreader task which corresponds to the proofreader task specified in the tasks.yaml."""
		return Task(
			config=self.tasks_config['proofreader_task'],
		)

	# @task
	# def factchecker_task(self) -> Task:
	#	"""The factchecker task which corresponds to the factchecker task specified in the tasks.yaml."""
	# 	return Task(
	# 		config=self.tasks_config['factchecker_task'],
	# 	)

	@crew
	def crew(self) -> Crew:
		"""Creates the BaRagmasChatbot crew"""

		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)