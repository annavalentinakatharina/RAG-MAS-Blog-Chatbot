import os
import shutil

from crewai_tools.tools import DOCXSearchTool, PDFSearchTool, TXTSearchTool, WebsiteSearchTool
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext, ConversationHandler
from langchain_ollama import OllamaLLM
from src.ba_ragmas_chatbot import logger_config
from src.ba_ragmas_chatbot.crew import BaRagmasChatbot
from dotenv import load_dotenv

class TelegramBot:
    CHAT, TOPIC, TASK, TOPIC_OR_TASK, WEBSITE, DOCUMENT, LENGTH, LANGUAGE_LEVEL, INFORMATION, LANGUAGE, TONE, CONFIRM, ADDITIONAL = range(13)
    VALID_MIME_TYPES = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]
    load_dotenv()
    token = os.getenv("CHATBOT_TOKEN")
    llm_name = os.getenv("MODEL_NAME")
    llm_provider = os.getenv("MODEL_PROVIDER")
    llm_url = os.getenv("API_BASE")
    embed_model_name = os.getenv("EMBEDDING_MODEL")
    embed_model_provider = os.getenv("EMBEDDING_MODEL_PROVIDER")
    embed_model_url = os.getenv("API_BASE")
    tools = []
    ai = OllamaLLM(model=llm_name)
    logger = logger_config.get_logger('telegram bot')
    retry = False

    def clear_db(self):
        """Deletes all database files related to ChromaDB."""
        db_folder = "./db"
        if os.path.exists(db_folder):
            shutil.rmtree(db_folder)
        os.makedirs(db_folder)

    async def chat(self, update: Update, context: CallbackContext):
        """Interaction with the second not-RAG-MAS llm when the blog article configuration is deactivated"""
        response = ""
        try:
            self.logger.debug(f"chat: Function successfully called with message {str(update.message.text)}")
            context.user_data['history'] = context.user_data.get('history', []) + [update.message.text]
            history = "\n".join(context.user_data['history'])
            response = str(self.ai.invoke(history))
            await update.message.reply_html(response)
            self.logger.debug(f"chat: Query successfully answered with {str(response)}")
            context.user_data['history'].append(str(response))
            return self.CHAT

        except BadRequest as b:
            if b.message == "Message is too long":
                responses = response.split("\n\n")
                self.logger.warn(f"confirm: Message is too long, split up into small packets by double line.")
                for response in responses:
                    await update.message.reply_text(response)
            return self.CHAT

        except Exception as e:
            await update.message.reply_text(f"chat: An error occurred: {str(e)}")
            return self.CHAT

    async def clear(self, update: Update, context: CallbackContext):
        """Clears the conversation and user history, and returns to chat."""
        try:
            context.user_data.clear()
            context.user_data['history'] = []
            self.tools.clear()
            self.logger.info(f"clear: Conversation successfully cleared.")
            await update.message.reply_text("Conversation successfully cleared! Your conversation was restarted, so please either restart your configuration or chat with the LLM!")
            return self.CHAT

        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. To re-clear the conversation, please send /clear again.")
            self.logger.error(f"clear: Tried to clear conversation, but an exception occurred: {str(e)}")
            return self.CHAT

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        try:
            user = update.effective_user
            self.logger.info(f"start: Conversation successfully started with user {str(user.mention_html())}. ")
            response = f"Hi {user.mention_html()}! This is a chatbot for creating blog articles using RAG and MAS systems! You have two ways of using this chatbot: Either by chatting with a LLM model, or by using the configuring your blog article and generating it using Reality-Augmented Generation and Multi-Agent Systems. When you are ready to start configuration, use /start_configuration. \n\nAfter starting the configuration, you are asked for: \n- topic or a task \n- website \n- document \n- length \n- language level \n- information level \n- language \n- tone \n- additional information \nFinally, you are asked to confirm the configuration and have a chance to change things."
            await update.message.reply_html(response)
            context.user_data['history'] = []
            self.logger.debug(f"start: Response message successfully sent. Message: {str(response)}")
            return self.CHAT

        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}")
            self.logger.error(f"start: Tried to start conversation, but an exception occurred: {str(e)}")
            return self.CHAT

    async def start_configuration(self, update:Update, context: ContextTypes.DEFAULT_TYPE):
        """Starts the article configuration"""
        try:
            await update.message.reply_text(
                "Great, you want to start the blog article configuration! First, what topic should the blog article be about? Or what task should the blog article fulfil? If you have a topic please respond with 'topic', if you have a separate task please respond with 'task'.")
            self.logger.debug("start_configuration: Blog article configuration started.")
            return self.TOPIC_OR_TASK

        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. To restart the configuration, please send /start_configuration again.")
            self.logger.error(f"start_configuration: Tried to start configuration, but an exception occurred: {str(e)}")
            return self.CHAT

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await update.message.reply_text(
                f"Welcome to the RAG-MAS-Blog-Article-Generator Bot! Here's how to get started:\n"
                f"1. /start - Restart the conversation.\n"
                f"2. /start_configuration - Start the blog article configuration.\n"
                f"3. /chat - Chat with a Llama LLM.\n"
                f"4. /clear - Clear the conversation and user history.\n"
                f"5. /cancel - End the conversation.\n"
                f"Just type a command to get started!")
            self.logger.debug("help: help sent.")
            return self.CHAT

        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. To get help, please send /help again.")
            self.logger.error(f"help: Tried to respond with help, but an exception occurred: {str(e)}")
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

            if update.message.text == "no" and self.retry == True:
                # a second route for when the user wants to reconfigure their data
                response = f"Okay, you want to keep your topic or task! Next, do you want to add another link to a website? If yes, please respond with the new link, if not, please respond with 'no'."
                await update.message.reply_text(response)
                self.logger.debug(f"topic_or_task: Reconfiguration response successfully sent. Message: {str(response)}")
                return self.WEBSITE

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
            context.user_data['topic'] = update.message.text
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
            if update.message.text == "no" and self.retry == True:
                # a second route for when the user wants to reconfigure their data
                response = "Okay, what about a document? If yes, please reply with the document, if not, please respond with 'no'."
                await update.message.reply_text(response)
                self.logger.debug(f"website: Response message successfully sent. Message: {str(response)}")
                return self.DOCUMENT

            if update.message.text != "no" and self.retry == True:
                # a second route for when the user wants to reconfigure their data
                response = "Okay, do you have a another link to a website? If yes, please reply with the website, if not, please respond with 'no'."
                self.tools.append(self.addWebsite(update.message.text))
                await update.message.reply_text(response)
                self.logger.debug(f"website: Response message successfully sent. Message: {str(response)}")
                return self.WEBSITE

            if update.message.text.lower() != "no":
                self.tools.append(self.addWebsite(update.message.text))
                response = "Okay, do you have another link to a website with information you want to have included? If yes, please reply with the link, if not, please just send 'no'."
                await update.message.reply_text(response)
                self.logger.debug(f"website: Response message successfully sent. Message: {str(response)}")
                return self.WEBSITE

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
                    return self.DOCUMENT

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
            response = "Do you have another document you want to upload? If yes, please reply with the document, if not, please just send 'no'."
            if self.retry:
                # a second route for when the user wants to reconfigure their data
                response = "Do you have another document you want to upload? If yes, please reply with the document, if not, please respond with 'no'."
            await update.message.reply_text(response)
            self.logger.debug(f"document: Response message successfully sent. Message: {str(response)}")
            return self.DOCUMENT

        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your document or 'no'.")
            self.logger.error(f"document: An exception occurred: {str(e)}")
            return self.DOCUMENT

    async def no_document(self, update: Update, context: CallbackContext):
        """Manages what happens when no document is sent"""
        try:
            self.logger.debug(f"no_document: Function successfully called with message {str(update.message.text)}")
            if update.message.text == "no" and self.retry == True:
                # a second route for when the user wants to reconfigure their data
                response = "Next, do you want to change your blog article length? If yes, please reply with the new length, if not, please respond with 'no'."
                await update.message.reply_text(response)
                self.logger.debug(f"no_document: Response message successfully sent. Message: {str(response)}")
                return self.LENGTH

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
            if self.retry:
                #a second route for when the user wants to reconfigure their data
                self.logger.debug(
                    f"length: Function successfully called with message {str(update.message.text)}")
                if update.message.text != "no":
                    context.user_data['length'] = update.message.text
                response = "Next, do you want to change your blog article language level? If yes, please reply with the new language level, if not, please respond with 'no'."
                await update.message.reply_text(response)
                self.logger.debug(f"length: Response message successfully sent. Message: {str(response)}")
                return self.LANGUAGE_LEVEL

            self.logger.debug(f"length: Function successfully called with message {str(update.message.text)}")
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
            if self.retry:
                # a second route for when the user wants to reconfigure their data
                self.logger.debug(
                    f"language level: Function successfully called with message {str(update.message.text)}")
                if update.message.text != "no":
                    context.user_data['language_level'] = update.message.text
                response = "Next, do you want to change your blog article information level? If yes, please reply with the new information level, if not, please respond with 'no'."
                await update.message.reply_text(response)
                self.logger.debug(f"language_level: Response message successfully sent. Message: {str(response)}")
                return self.INFORMATION

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
            if self.retry:
                # a second route for when the user wants to reconfigure their data
                self.logger.debug(
                    f"information: Function successfully called with message {str(update.message.text)}")
                if update.message.text != "no":
                    context.user_data['information'] = update.message.text
                response = "Next, do you want to change your blog article language? If yes, please reply with the new language, if not, please respond with 'no'."
                await update.message.reply_text(response)
                self.logger.debug(f"information: Response message successfully sent. Message: {str(response)}")
                return self.LANGUAGE

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
            if self.retry:
                # a second route for when the user wants to reconfigure their data
                self.logger.debug(
                    f"language: Function successfully called with message {str(update.message.text)}")
                if update.message.text != "no":
                    context.user_data['language'] = update.message.text
                response = "Next, do you want to change your blog article tone? If yes, please reply with the new tone, if not, please respond with 'no'."
                await update.message.reply_text(response)
                self.logger.debug(f"language: Response message successfully sent. Message: {str(response)}")
                return self.TONE

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
            if self.retry:
                # a second route for when the user wants to reconfigure their data
                self.logger.debug(
                    f"tone: Function successfully called with message {str(update.message.text)}")
                if update.message.text != "no":
                    context.user_data['tone'] = update.message.text
                response = "Next, do you want to change your blog additional information? If yes, please reply with the new additional information, if not, please respond with 'no'."
                await update.message.reply_text(response)
                self.logger.debug(f"tone: Response message successfully sent. Message: {str(response)}")
                return self.ADDITIONAL

            self.logger.debug(f"tone: Function successfully called with message {str(update.message.text)}")
            context.user_data['tone'] = update.message.text
            response =("Great! Now, do you have any additional information you want to have included? If not, please respond with 'no'.")
            await update.message.reply_text(response)
            self.logger.debug(f"tone: Response message successfully sent. Message: {str(response)}")
            return self.ADDITIONAL

        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your preferred article tone.")
            self.logger.error(f"tone: An exception occurred: {str(e)}")
            return self.TONE

    async def additional(self, update: Update, context: CallbackContext):
        try:
            # a second route for when the user wants to reconfigure their data
            if self.retry and update.message.text != "no":
                    context.user_data['additional_information'] = update.message.text
            self.logger.debug(f"additional_information: Function successfully called with message {str(update.message.text)}")
            context.user_data['additional_information'] = ""
            if update.message.text != "no":
                context.user_data['additional_information'] = update.message.text

            user_data = context.user_data
            response =(f"Thanks! Here's what I got:\n"
                f"- Length: {user_data['length']}\n"
                f"- Topic or Task: {user_data['topic']}\n"
                f"- Language Level: {user_data['language_level']}\n"
                f"- Information Level: {user_data['information']}\n"
                f"- Language: {user_data['language']}\n"
                f"- Tone: {user_data['tone']}\n"
                f"- Additional Information: {user_data['additional_information']}\n"
                f"Type 'yes' to confirm or 'no' to restart."
                f"\n\nIf you type 'no', your configuration will be saved. Then, you will be asked all questions again and can just respond 'no' if you want your answer to remain the same."
                f"\nSo, please only respond to a question if you want to change your answer.")
            await update.message.reply_text(response)
            self.logger.debug(f"additional: Response message successfully sent. Message: {str(response)}")
            return self.CONFIRM

        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your additional information.")
            self.logger.error(f"tone: An exception occurred: {str(e)}")
            return self.ADDITIONAL

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
                    'additional_information': user_data['additional_information'],
                    'history': user_data['history'],
                }
                self.logger.debug(f"confirm: Inputs: {str(inputs)}")
                context.user_data['history'] = context.user_data.get('history', []) + [str(inputs)]
                history = "\n".join(context.user_data['history'])

                filtered_tools = [tool for tool in self.tools if tool is not None]
                self.logger.debug(f"confirm: Tools registered: {str(filtered_tools)}")
                bot = BaRagmasChatbot(filtered_tools)
                self.logger.debug(f"confirm: BaRagmasChatbot started.")
                await update.message.reply_text("Processing...")

                response = str(bot.crew().kickoff(inputs=inputs))
                self.logger.debug(f"confirm: Crew kicked off and response successfully created.")
                await update.message.reply_text(response)
                self.logger.debug(f"confirm: Response message successfully sent. Message: {str(response)}")
                context.user_data["history"].append(str(response))
                return self.CHAT

            else:
                await update.message.reply_text("Okay, let's reconfigure! Remember to please respond with 'no' if you want to keep your answer, so only respond if you want to change it. \n First, do you want to change you topic or task? If yes, please respond with 'topic' or 'task', if not, please respond with 'no'.")
                self.logger.debug(f"confirm: Configuration restarted.")
                self.retry = True
                return self.TOPIC_OR_TASK

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
        self.clear_db()
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
                self.ADDITIONAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.additional)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel),
                       CommandHandler("clear", self.clear),
                       CommandHandler("start_configuration", self.start_configuration),
                       CommandHandler("help", self.help),
                       CommandHandler("chat", self.chat)
                       ],
        )

        application.add_handler(conv_handler)
        application.run_polling()

    def addWebsite(self, url):
        self.tools.append(
            WebsiteSearchTool(
                website=url,
                config=dict(
                    llm=dict(
                        provider=self.llm_provider,
                        config=dict(
                            model=self.llm_name,
                            base_url=self.llm_url,
                        ),
                    ),
                    embedder=dict(
                        provider=self.embed_model_provider,
                        config=dict(
                            model=self.embed_model_name,
                            base_url=self.embed_model_url,
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
                        provider=self.llm_provider,
                        config=dict(
                            model=self.llm_name,
                            base_url=self.llm_url,
                        ),
                    ),
                    embedder=dict(
                        provider=self.embed_model_provider,
                        config=dict(
                            model=self.embed_model_name,
                            base_url=self.embed_model_url,
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
                        provider=self.llm_provider,
                        config=dict(
                            model=self.llm_name,
                            base_url=self.llm_url,
                        ),
                    ),
                    embedder=dict(
                        provider=self.embed_model_provider,
                        config=dict(
                            model=self.embed_model_name,
                            base_url=self.embed_model_url,
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
                        provider=self.llm_provider,
                        config=dict(
                            model=self.llm_name,
                            base_url=self.llm_url,
                        ),
                    ),
                    embedder=dict(
                        provider=self.embed_model_provider,
                        config=dict(
                            model=self.embed_model_name,
                            base_url=self.embed_model_url,
                        ),
                    ),
                )
            )
        )
        self.logger.info(f"TXT-RAG-Tool added: {location}")
