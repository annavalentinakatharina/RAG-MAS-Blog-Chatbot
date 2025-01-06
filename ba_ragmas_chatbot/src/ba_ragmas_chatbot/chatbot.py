import os
import yaml

from crewai_tools.tools import DOCXSearchTool, PDFSearchTool, TXTSearchTool, WebsiteSearchTool
from telegram import ForceReply, Update, ReplyKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext, ConversationHandler
from langchain_ollama import OllamaLLM

from src.ba_ragmas_chatbot import logger_config
from src.ba_ragmas_chatbot.crew import BaRagmasChatbot


class TelegramBot:
    CHAT, TOPIC, TASK, TOPIC_OR_TASK, WEBSITE, DOCUMENT, LENGTH, LANGUAGE_LEVEL, INFORMATION, LANGUAGE, TONE, CONFIRM = range(12)
    VALID_MIME_TYPES = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_file = os.path.join(current_dir, "config", "configs.yaml")
    with open(yaml_file, 'r') as file:
        config = yaml.safe_load(file)
    token = config['chatbot_token']['token']
    tools = []
    ai = OllamaLLM(model="llama3.1:8b-instruct-q8_0")
    logger = logger_config.get_logger('telegram bot')

    async def chat(self, update: Update, context: CallbackContext):
        """Interaction with the second not-RAG-MAS llm when the blog article configuration is deactivated"""
        try:
            self.logger.debug(f"chat: Function successfully called with message {str(update.message.text)}")
            if update.message.text.lower() == "start configuration":
                await update.message.reply_text(
                    "Great, you want to start the blog article configuration! First, what topic should the blog article be about? Or what task should the blog article fulfil? If you have a topic please respond with 'topic', if you have a separate task please respond with 'task'.")
                self.logger.debug("chat: Blog article configuration started.")
                return self.TOPIC_OR_TASK
            context.user_data['history'] = context.user_data.get('history', []) + [update.message.text]
            history = "\n".join(context.user_data['history'])
            response = str(self.ai.invoke(history))
            await update.message.reply_html(response)
            self.logger.debug(f"chat: Query successfully answered with {str(response)}")
            context.user_data['history'].append(str(response))
            return self.CHAT
        except Exception as e:
            await update.message.reply_text(f"chat: An error occurred: {str(e)}")
            return self.CHAT

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        try:
            user = update.effective_user
            self.logger.info(f"start: Conversation successfully started with user {str(user.mention_html())}. ")
            response = rf"Hi {user.mention_html()}! This is a chatbot for creating blog articles using RAG and MAS systems! You have two ways of using this chatbot: Either by chatting with a LLM model, or by using the configuring your blog article and generating it using RAG and MAS. When you are ready to start configuration, type in 'start configuration'. "
            await update.message.reply_html(response)
            context.user_data['history'] = []
            self.logger.debug(f"start: Response message successfully sent. Message: {str(response)}")
            return self.CHAT
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}")
            self.logger.error(f"start: Tried to start conversation, but an exception occurred: {str(e)}")
            return self.CHAT

    async def topic_or_task(self, update: Update, context: CallbackContext):
        """Manages if the system should write an article on a topic or if it should do a task"""
        try:
            self.logger.debug(f"topic_or_task: Function successfully called with message {str(update.message.text)}")
            if update.message.text == "topic":
                response = "Okay, topic it is! What topic should the blog article be about?"
                await update.message.reply_text(response)
                self.logger.debug(f"topic_or_task: Response message successfully sent. Message: {str(response)}")
                return self.TOPIC
            if update.message.text == "task":
                response = "Okay, task it is! What task should the blog article fulfil?"
                await update.message.reply_text(response)
                self.logger.debug(f"topic_or_task: Response message successfully sent. Message: {str(response)}")
                return self.TASK
            else:
                response = "Not valid, please respond with either 'topic' or 'task'."
                await update.message.reply_text(response)
                self.logger.debug(f"topic_or_task: Response message successfully sent. Message: {str(response)}")
                return self.TOPIC_OR_TASK
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease answer with 'topic' or 'task' again.")
            self.logger.error(f"topic_or_task: An exception occurred: {str(e)}")
            return self.TOPIC_OR_TASK

    async def topic(self, update: Update, context: CallbackContext):
        """Saves the topic in the user data"""
        try:
            self.logger.debug(f"topic: Function successfully called with message {str(update.message.text)}")
            context.user_data['topic'] = update.message.text
            response = "Great! Do you have a link to a website with information you want to have included? If yes, please reply with the link, if not, please just send 'no'."
            await update.message.reply_text(response)
            self.logger.debug(f"topic: Response message successfully sent. Message: {str(response)}")
            return self.WEBSITE
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your topic.")
            self.logger.error(f"topic: An exception occurred: {str(e)}")
            return self.TOPIC

    async def task(self, update: Update, context: CallbackContext):
        """Saves the task in the user data"""
        try:
            self.logger.debug(f"task: Function successfully called with message {str(update.message.text)}")
            context.user_data['topic'] = "fulfilling task " + update.message.text
            response = "Great! Do you have a link to a website with information you want to have included? If yes, please reply with the link, if not, please just send 'no'."
            await update.message.reply_text(response)
            self.logger.debug(f"task: Response message successfully sent. Message: {str(response)}")
            return self.WEBSITE
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your task.")
            self.logger.error(f"task: An exception occurred: {str(e)}")
            return self.TASK

    async def website(self, update: Update, context: CallbackContext):
        """Saves a website link in the user data if one is sent"""
        try:
            self.logger.debug(f"website: Function successfully called with message {str(update.message.text)}")
            if update.message.text.lower() != "no":
                self.tools.append(self.addWebsite(update.message.text))
            response = "Great! Do you have a document with information you want to have included? If yes, please reply with the document, if not, please just send 'no'."
            await update.message.reply_text(response)
            self.logger.debug(f"website: Response message successfully sent. Message: {str(response)}")
            return self.DOCUMENT
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your link or 'no'.")
            self.logger.error(f"website: An exception occurred: {str(e)}")
            return self.WEBSITE

    async def document(self, update: Update, context: CallbackContext):
        """Saves a document in the 'documents' folder and the storage link in the user data if one is sent"""
        try:
            self.logger.debug(f"document: Function successfully called.")
            document = update.message.document
            file_path = ""
            if document:
                if document.mime_type not in self.VALID_MIME_TYPES:
                        await update.message.reply_text(
                            f"Unsupported file type: {document.mime_type}. \nPlease upload a valid document (PDF, Word, TXT)."
                        )
                        return
                base_dir = os.path.dirname(__file__)
                file_path = os.path.join(base_dir, "documents", document.file_name)
                self.logger.debug(f"document: File saved at: {str(file_path)}")
                file_id = document.file_id
                self.logger.debug(f"document: File_id: {str(file_id)}")
                file = await context.bot.get_file(file_id)
                await file.download_to_drive(file_path)
                match document.mime_type:
                    case "application/pdf":
                        self.addPDF(file_path)
                    case "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        self.addDOCX(file_path)
                    case "text/plain":
                        self.addTxt(file_path)
                    case _:
                        await update.message.reply_text("Invalid file type, only acceptable file endings are: PDF, TXT and DOXC. Please convert and send your document again.")
                        self.logger.warn(f"document: Invalid file type sent: {str(document.mime_type)}")
                        return self.DOCUMENT
                self.logger.debug(f"document: File Mime Type: {str(document.mime_type)}")
            response = "How long should the blog article be? (e.g. Short, Medium, Long)"
            await update.message.reply_text(response)
            self.logger.debug(f"document: Response message successfully sent. Message: {str(response)}")
            return self.LENGTH
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your document or 'no'.")
            self.logger.error(f"document: An exception occurred: {str(e)}")
            return self.DOCUMENT

    async def no_document(self, update: Update, context: CallbackContext):
        """Manages what happens when no document is sent"""
        try:
            self.logger.debug(f"no_document: Function successfully called with message {str(update.message.text)}")
            if update.message.text.lower() != "no":
                response = "Not valid, please respond with either a document or 'no'."
                await update.message.reply_text(response)
                self.logger.debug(f"no_document: Response message successfully sent. Message: {str(response)}")
                return self.DOCUMENT
            response = "How long should the blog article be? (e.g. Short, Medium, Long)"
            await update.message.reply_text(response)
            self.logger.debug(f"no_document: Response message successfully sent. Message: {str(response)}")
            return self.LENGTH
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your document or 'no'.")
            self.logger.error(f"no_document: An exception occurred: {str(e)}")
            return self.DOCUMENT

    async def length(self, update: Update, context: CallbackContext):
        """Saves the configured length in the user data"""
        try:
            self.logger.debug(f"length: Function length successfully called with message {str(update.message.text)}")
            context.user_data['length'] = update.message.text
            response = "Great! What language level should it be? (e.g. Beginner, Intermediate, Advanced)"
            await update.message.reply_text(response)
            self.logger.debug(f"length: Response message successfully sent. Message: {str(response)}")
            return self.LANGUAGE_LEVEL
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your preferred article length.")
            self.logger.error(f"length: An exception occurred: {str(e)}")
            return self.LENGTH

    async def language_level(self, update: Update, context: CallbackContext):
        """Saves the configured language level in the user data"""
        try:
            self.logger.debug(f"language_level: Function successfully called with message {str(update.message.text)}")
            context.user_data['language_level'] = update.message.text
            response = "Great! What information level should it be? (e.g. High, Intermediate, Low)"
            await update.message.reply_text(response)
            self.logger.debug(f"language_level: Response message successfully sent. Message: {str(response)}")
            return self.INFORMATION
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your preferred article language level.")
            self.logger.error(f"language_level: An exception occurred: {str(e)}")
            return self.LANGUAGE_LEVEL

    async def information(self, update: Update, context: CallbackContext):
        """Saves the configured information level in the user data"""
        try:
            self.logger.debug(f"information: Function successfully called with message {str(update.message.text)}")
            context.user_data['information'] = update.message.text
            response = "Great! What language should it be? (e.g. English, German, Spanish)"
            await update.message.reply_text(response)
            self.logger.debug(f"information: Response message successfully sent. Message: {str(response)}")
            return self.LANGUAGE
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your preferred article information level.")
            self.logger.error(f"information: An exception occurred: {str(e)}")
            return self.INFORMATION

    async def language(self, update: Update, context: CallbackContext):
        """Saves the configured language in the user data"""
        try:
            self.logger.debug(f"language: Function successfully called with message {str(update.message.text)}")
            context.user_data['language'] = update.message.text
            response = "Great! What tone should it be? (e.g. Professional, Casual, Friendly)"
            await update.message.reply_text(response)
            self.logger.debug(f"language: Response message successfully sent. Message: {str(response)}")
            return self.TONE
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your preferred article language.")
            self.logger.error(f"language: An exception occurred: {str(e)}")
            return self.LANGUAGE

    async def tone(self, update: Update, context: CallbackContext):
        """Saves the configured tone in the user data and asks """
        try:
            self.logger.debug(f"tone: Function successfully called with message {str(update.message.text)}")
            context.user_data['tone'] = update.message.text
            user_data = context.user_data
            response =(f"Thanks! Here's what I got:\n"
                f"- Length: {user_data['length']}\n"
                f"- Topic or Task: {user_data['topic']}\n"
                f"- Language Level: {user_data['language_level']}\n"
                f"- Information Level: {user_data['information']}\n"
                f"- Language: {user_data['language']}\n"
                f"- Tone: {user_data['tone']}\n"
                f"Type 'yes' to confirm or 'no' to restart.")
            await update.message.reply_text(response)
            self.logger.debug(f"tone: Response message successfully sent. Message: {str(response)}")
            return self.CONFIRM
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your preferred article tone.")
            self.logger.error(f"tone: An exception occurred: {str(e)}")
            return self.TONE

    async def confirm(self, update: Update, context: CallbackContext):
        """Starts the blog article generation and returns the finished article if answer is yes, else restart the whole process"""
        response = ""
        try:
            self.logger.debug(f"confirm: Function successfully called with message {str(update.message.text)}")
            if update.message.text.lower() == 'yes':
                self.logger.debug(f"confirm: Configuration confirmed, process started.")
                user_data = context.user_data
                inputs = {
                    'topic': user_data['topic'],
                    'length': user_data['length'],
                    'information_level': user_data['information'],
                    'language_level': user_data['language_level'],
                    'tone': user_data['tone'],
                    'language': user_data['language'],
                    'history': user_data['history'],
                }
                self.logger.debug(f"confirm: Inputs: {str(inputs)}")
                context.user_data['history'] = context.user_data.get('history', []) + [str(inputs)]
                history = "\n".join(context.user_data['history'])
                filtered_tools = [tool for tool in self.tools if tool is not None]
                self.logger.debug(f"confirm: Tools registered: {str(filtered_tools)}")
                bot = BaRagmasChatbot(filtered_tools)
                self.logger.debug(f"confirm: BaRagmasChatbot started.")
                response = str(bot.crew().kickoff(inputs=inputs))
                self.logger.debug(f"confirm: Crew kicked off and response successfully created.")
                await update.message.reply_text(response)
                self.logger.debug(f"confirm: Response message successfully sent. Message: {str(response)}")
                context.user_data["history"].append(str(response))
                return self.CHAT
            else:
                await update.message.reply_text("Let's start over!")
                self.logger.debug(f"confirm: Configuration restarted.")
                return self.start(update, context)
        except BadRequest as b:
            if b.message == "Message is too long":
                responses = response.split("\n\n")
                self.logger.warn(f"confirm: Message is too long, split up into small packets by double line.")
                for response in responses:
                    await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend if you want to confirm the inputs or not.")
            self.logger.error(f"confirm: An exception occurred:{str(e)}")
            return self.CONFIRM

    async def cancel(self, update: Update, context: CallbackContext):
        """The fallout function, leaves the conversation"""
        try:
            self.logger.debug(f"cancel: Function successfully called with message {str(update.message.text)}")
            response = "Conversation canceled. Type /start to begin again."
            await update.message.reply_text(response)
            self.logger.debug(f"cancel: Response message successfully sent. Message: {str(response)}")
            return ConversationHandler.END
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nConversation canceled. Type /start to begin again.")
            self.logger.error(f"cancel: An exception occurred: {str(e)}")
            return ConversationHandler.END

    def start_bot(self) -> None:
        """Start the bot."""
        application = Application.builder().token(self.token).build()
        self.logger.info("Telegram Bot successfully started.")

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                self.CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.chat)],
                self.TOPIC_OR_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.topic_or_task)],
                self.TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.topic)],
                self.TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.task)],
                self.WEBSITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.website)],
                self.DOCUMENT: [MessageHandler(filters.Document.ALL, self.document), MessageHandler(filters.TEXT & ~filters.COMMAND, self.no_document)],
                self.LENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.length)],
                self.LANGUAGE_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.language_level)],
                self.INFORMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.information)],
                self.LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.language)],
                self.TONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.tone)],
                self.CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.confirm)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

        application.add_handler(conv_handler)
        application.run_polling()

    def addWebsite(self, url):
        self.tools.append(
            WebsiteSearchTool(
                website=url,
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
                ),
            )
        )
        self.logger.info(f"Website-RAG-Tool added: {url}")

    def addPDF(self, location):
        self.tools.append(
            PDFSearchTool(
                pdf=location,
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
        self.logger.info(f"PDF-RAG-Tool added: {location}")


    def addDOCX(self, location):
        self.tools.append(
            DOCXSearchTool(
                docx=location,
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
        self.logger.info(f"DOCX-RAG-Tool added: {location}")

    def addTxt(self, location):
        self.tools.append(
            TXTSearchTool(
                txt=location,
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
        self.logger.info(f"TXT-RAG-Tool added: {location}")
