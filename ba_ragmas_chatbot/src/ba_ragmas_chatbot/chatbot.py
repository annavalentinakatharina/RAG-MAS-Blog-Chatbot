import os

from crewai_tools.tools import DOCXSearchTool, PDFSearchTool, TXTSearchTool, WebsiteSearchTool
from telegram import ForceReply, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext, ConversationHandler
from langchain_ollama import OllamaLLM
from src.ba_ragmas_chatbot.crew import BaRagmasChatbot


class TelegramBot:
    CHAT, TOPIC, TASK, TOPIC_OR_TASK, WEBSITE, DOCUMENT, LENGTH, LANGUAGE_LEVEL, INFORMATION, LANGUAGE, TONE, CONFIRM = range(12)
    VALID_MIME_TYPES = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]
    tools = []
    ai = OllamaLLM(model="llama3.1:8b-instruct-q8_0")

    async def chat(self, update: Update, context: CallbackContext):
        """Interaction with the second not-RAG-MAS llm when the blog article configuration is deactivated"""
        try:
            if update.message.text.lower() == "start configuration":
                await update.message.reply_text(
                    "Great, you want to start the blog article configuration! First, what topic should the blog article be about? Or what task should the blog article fulfil? If you have a topic please respond with 'topic', if you have a separate task please respond with 'task'.")
                return self.TOPIC_OR_TASK
            context.user_data['history'] = context.user_data.get('history', []) + [update.message.text]
            history = "\n".join(context.user_data['history'])
            response = str(self.ai.invoke(history))
            await update.message.reply_html(response)
            context.user_data['history'].append(response)
            print(history)
            return self.CHAT
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}")
            return self.CHAT

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        try:
            user = update.effective_user
            await update.message.reply_html(
                rf"Hi {user.mention_html()}! This is a chatbot for creating blog articles using RAG and MAS systems! You have two ways of using this chatbot: Either by chatting with a LLM model, or by using the configuring your blog article and generating it using RAG and MAS. When you are ready to start configuration, type in 'start configuration'. ")
            context.user_data['history'] = []
            return self.CHAT
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}")
            return self.CHAT

    async def topic_or_task(self, update: Update, context: CallbackContext):
        """Manages if the system should write an article on a topic or if it should do a task"""
        try:
            if update.message.text == "topic":
                await update.message.reply_text(
                    "Okay, topic it is! What topic should the blog article be about?")
                return self.TOPIC
            if update.message.text == "task":
                await update.message.reply_text(
                    "Okay, task it is! What task should the blog article fulfil?")
                return self.TASK
            else:
                await update.message.reply_text(
                    "Not valid, please respond with either 'topic' or 'task'.")
                return self.TOPIC_OR_TASK
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease answer with 'topic' or 'task' again.")
            return self.TOPIC_OR_TASK

    async def topic(self, update: Update, context: CallbackContext):
        """Saves the topic in the user data"""
        try:
            context.user_data['topic'] = update.message.text
            await update.message.reply_text(
                "Great! Do you have a link to a website with information you want to have included? If yes, please reply with the link, if not, please just send 'no'.")
            return self.WEBSITE
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your topic.")
            return self.TOPIC

    async def task(self, update: Update, context: CallbackContext):
        """Saves the task in the user data"""
        try:
            context.user_data['topic'] = "fulfilling task " + update.message.text
            await update.message.reply_text(
                "Great! Do you have a link to a website with information you want to have included? If yes, please reply with the link, if not, please just send 'no'.")
            return self.WEBSITE
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your task.")
            return self.TASK

    async def website(self, update: Update, context: CallbackContext):
        """Saves a website link in the user data if one is sent"""
        try:
            if update.message.text.lower() != "no":
                self.tools.append(self.addWebsite(update.message.text))
            await update.message.reply_text(
                "Great! Do you have a document with information you want to have included? If yes, please reply with the document, if not, please just send 'no'."),
            return self.DOCUMENT
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your link or 'no'.")
            return self.WEBSITE

    async def document(self, update: Update, context: CallbackContext):
        """Saves a document in the 'documents' folder and the storage link in the user data if one is sent"""
        try:
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
                file_id = document.file_id
                file = await context.bot.get_file(file_id)
                await file.download_to_drive(file_path)
                match document.mime_type:
                    case "application/pdf":
                        self.addPDF(file_path)
                    case "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        self.addDOCX(file_path)
                    case "text/plain":
                        self.addTxt(file_path)
            await update.message.reply_text("How long should the blog article be? (e.g. Short, Medium, Long)"),
            return self.LENGTH
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your document or 'no'.")
            return self.DOCUMENT

    async def no_document(self, update: Update, context: CallbackContext):
        """Manages what happens when no document is sent"""
        try:
            if update.message.text.lower() != "no":
                await update.message.reply_text("Not valid, please respond with either a document or 'no'.")
                return self.DOCUMENT
            await update.message.reply_text(
                "How long should the blog article be? (e.g. Short, Medium, Long)"),
            return self.LENGTH
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your document or 'no'.")
            return self.DOCUMENT

    async def length(self, update: Update, context: CallbackContext):
        """Saves the configured length in the user data"""
        try:
            context.user_data['length'] = update.message.text
            await update.message.reply_text(
                "Great! What language level should it be? (e.g. Beginner, Intermediate, Advanced)")
            return self.LANGUAGE_LEVEL
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your preferred article length.")
            return self.LENGTH

    async def language_level(self, update: Update, context: CallbackContext):
        """Saves the configured language level in the user data"""
        try:
            context.user_data['language_level'] = update.message.text
            await update.message.reply_text(
                "Great! What information level should it be? (e.g. High, Intermediate, Low)")
            return self.INFORMATION
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your preferred article language level.")
            return self.LANGUAGE_LEVEL

    async def information(self, update: Update, context: CallbackContext):
        """Saves the configured information level in the user data"""
        try:
            context.user_data['information'] = update.message.text
            await update.message.reply_text(
                "Great! What language should it be? (e.g. English, German, Spanish)")
            return self.LANGUAGE
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your preferred article information level.")
            return self.INFORMATION

    async def language(self, update: Update, context: CallbackContext):
        """Saves the configured language in the user data"""
        try:
            context.user_data['language'] = update.message.text
            await update.message.reply_text(
                "Great! What tone should it be? (e.g. Professional, Casual, Friendly)")
            return self.TONE
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your preferred article language.")
            return self.LANGUAGE

    async def tone(self, update: Update, context: CallbackContext):
        """Saves the configured tone in the user data and asks """
        try:
            context.user_data['tone'] = update.message.text
            user_data = context.user_data
            await update.message.reply_text(
                f"Thanks! Here's what I got:\n"
                f"- Length: {user_data['length']}\n"
                f"- Topic or Task: {user_data['topic']}\n"
                f"- Language Level: {user_data['language_level']}\n"
                f"- Information Level: {user_data['information']}\n"
                f"- Language: {user_data['language']}\n"
                f"- Tone: {user_data['tone']}\n"
                f"Type 'yes' to confirm or 'no' to restart."
            )
            return self.CONFIRM
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend your preferred article tone.")
            return self.TONE

    async def confirm(self, update: Update, context: CallbackContext):
        """Starts the blog article generation and returns the finished article if answer is yes, else restart the whole process"""
        try:
            if update.message.text.lower() == 'yes':
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
                context.user_data['history'] = context.user_data.get('history', []) + [str(inputs)]
                history = "\n".join(context.user_data['history'])
                filtered_tools = [tool for tool in self.tools if tool is not None]
                bot = BaRagmasChatbot(filtered_tools)
                print(history)
                response = str(bot.crew().kickoff(inputs=inputs))
                response = await update.message.reply_text(response)
                context.user_data["history"].append(response)
                print(history)
                return self.CHAT
            else:
                await update.message.reply_text("Let's start over!")
                return self.start(update, context)
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nPlease resend if you want to confirm the inputs or not.")
            return self.CONFIRM

    async def cancel(self, update: Update, context: CallbackContext):
        """The fallout function, leaves the conversation"""
        try:
            await update.message.reply_text("Conversation canceled. Type /start to begin again.")
            return ConversationHandler.END
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}. \nConversation canceled. Type /start to begin again.")
            return ConversationHandler.END

    def start_bot(self) -> None:
        """Start the bot."""
        application = Application.builder().token("7727696877:AAEo2aSGPDj0QgBXhk97UWQP8urrgaXuLFw").build()

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
