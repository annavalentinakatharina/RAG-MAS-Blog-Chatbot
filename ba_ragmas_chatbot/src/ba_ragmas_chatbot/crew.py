from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import WebsiteSearchTool, PDFSearchTool, DOCXSearchTool, TXTSearchTool

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
		return inputs  # You can return the inputs or modify them as needed

	@after_kickoff
	def after_kickoff_function(self, result):
		print(f"After kickoff function with result: {result}")
		return result  # You can return the result or modify it as needed

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def researcher(self) -> Agent:
		print("Researcher made")
		return Agent(
			config=self.agents_config['researcher'],
			llm=LLM(model="ollama/llama3.1:8b-instruct-q8_0", base_url="http://localhost:11434"),
			tools = self.tools,
			verbose=True
		)

	@agent
	def editor(self) -> Agent:
		return Agent(
			config=self.agents_config['editor'],
			llm=LLM(model="ollama/llama3.1:8b-instruct-q8_0", base_url="http://localhost:11434"),
			#tools=self.tools,
			verbose=True
		)

	@agent
	def writer(self) -> Agent:
		return Agent(
			config=self.agents_config['writer'],
			llm=LLM(model="ollama/llama3.1:8b-instruct-q8_0", base_url="http://localhost:11434"),
			#tools=self.tools,
			verbose=True
		)

	# @agent
	# def proofreader(self) -> Agent:
	# 	return Agent(
	# 		config=self.agents_config['proofreader'],
	# 		llm=LLM(model="ollama/llama3.1:8b-instruct-q8_0", base_url="http://localhost:11434"),
	# 		verbose=True
	# 	)

	@agent
	def factchecker(self) -> Agent:
		return Agent(
			config=self.agents_config['factchecker'],
			llm=LLM(model="ollama/llama3.1:8b-instruct-q8_0", base_url="http://localhost:11434"),
			#tools=self.tools,
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def editor_task(self) -> Task:
		return Task(
			config=self.tasks_config['editor_task'],
		)

	@task
	def writer_task(self) -> Task:
		return Task(
			config=self.tasks_config['writer_task'],
		)

	# @task
	# def proofreader_task(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['proofreader_task'],
	# 	)

	@task
	def factchecker_task(self) -> Task:
		return Task(
			config=self.tasks_config['factchecker_task'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the BaRagmasChatbot crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

	def addWebsite(self, url):
		self.tools.append(
			WebsiteSearchTool(
				website = url,
				config=dict(
					llm=dict(
						provider="ollama", # or google, openai, anthropic, llama2, ...
						config=dict(
							model="llama3.1:8b-instruct-q8_0",
							base_url="http://localhost:11434",
							# temperature=0.5,
							# top_p=1,
							# stream=true,
						),
					),
					embedder=dict(
						provider="ollama",  # or openai, ollama, ...
						config=dict(
							model="mxbai-embed-large",
							base_url="http://localhost:11434",
							# task_type="retrieval_document",
							# title="Embeddings",
						),
					),
				),
			)
		)

	def addPDF(self, location):
		self.tools.append(
			PDFSearchTool(
				pdf = location,
				config=dict(
					llm=dict(
						provider="ollama",  # or google, openai, anthropic, llama2, ...
						config=dict(
							model="llama3.1:8b-instruct-q8_0",
							base_url="http://localhost:11434",
							# temperature=0.5,
							# top_p=1,
							# stream=true,
						),
					),
					embedder=dict(
						provider="ollama",  # or openai, ollama, ...
						config=dict(
							model="mxbai-embed-large",
							base_url="http://localhost:11434",
							# task_type="retrieval_document",
							# title="Embeddings",
						),
					),
				)
			)
		)

	def addDOCX(self, location):
		self.tools.append(
			DOCXSearchTool(
				docx = location,
				config=dict(
					llm=dict(
						provider="ollama",
						config=dict(
							model="llama3.1:8b-instruct-q8_0",
							base_url="http://localhost:11434",
						),
					),
					embedder=dict(
						provider="ollama",
						config=dict(
							model="mxbai-embed-large",
							base_url="http://localhost:11434",
						),
					),
				)
			)
		)

	def addTxt(self, location):
		self.tools.append(
				TXTSearchTool(
				txt = location,
				config=dict(
					llm=dict(
						provider="ollama",
						config=dict(
							model="llama3.1:8b-instruct-q8_0",
							base_url="http://localhost:11434",
						),
					),
					embedder=dict(
						provider="ollama",
						config=dict(
							model="mxbai-embed-large",
							base_url="http://localhost:11434",
						),
					),
				)
			)
		)


