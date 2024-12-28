import os

from crewai_tools.tools import DOCXSearchTool, PDFSearchTool, TXTSearchTool, WebsiteSearchTool
from telegram import ForceReply, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext, ConversationHandler

from src.ba_ragmas_chatbot.crew import BaRagmasChatbot


class TelegramBot:
    TOPIC, TASK, TOPIC_OR_TASK, WEBSITE, DOCUMENT, LENGTH, LANGUAGE_LEVEL, INFORMATION, LANGUAGE, TONE, CONFIRM = range(11)
    VALID_MIME_TYPES = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]
    tools = []
    #ai =

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}! This is a chatbot for creating blog articles using RAG and MAS systems! First, what topic should the blog article be about? Or what task should the blog article fulfil? If you have a topic please respond with 'topic', if you have a separate task please respond with 'task'.",
        )
        return self.TOPIC_OR_TASK

    async def topic_or_task(self, update: Update, context: CallbackContext):
        if update.message.text == "topic":
            await update.message.reply_text("Okay, topic it is! What topic should the blog article be about?")
            return self.TOPIC
        if update.message.text == "task":
            await update.message.reply_text("Okay, task it is! What task should the blog article fulfil?")
            return self.TASK
        else:
            await update.message.reply_text("Not valid, please respond with either 'topic' or 'task'.")
            return self.TOPIC_OR_TASK

    async def topic(self, update: Update, context: CallbackContext):
        context.user_data['topic'] = update.message.text
        await update.message.reply_text("Great! Do you have a link to a website with information you want to have included? If yes, please reply with the link, if not, please just send 'no'.")
        return self.WEBSITE

    async def task(self, update: Update, context: CallbackContext):
        context.user_data['topic'] = "fulfilling task " + update.message.text
        await update.message.reply_text("Great! Do you have a link to a website with information you want to have included? If yes, please reply with the link, if not, please just send 'no'.")
        return self.WEBSITE

    async def website(self, update: Update, context: CallbackContext):
        if update.message.text != "no" and update.message.text != "No":
            self.tools.append(self.addWebsite(update.message.text))
        await update.message.reply_text(
            "Great! Do you have a document with information you want to have included? If yes, please reply with the document, if not, please just send 'no'."),
        return self.DOCUMENT

    async def document(self, update: Update, context: CallbackContext):
        document = update.message.document
        file_path = ""
        if document:
            if document.mime_type not in self.VALID_MIME_TYPES:
                    await update.message.reply_text(
                        f"Unsupported file type: {document.mime_type}. Please upload a valid document (PDF, Word, TXT)."
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

    async def no_document(self, update: Update, context: CallbackContext):
        if update.message.text != "no":
            await update.message.reply_text("Not valid, please respond with either a document or 'no'.")
            return self.DOCUMENT
        await update.message.reply_text(
            "How long should the blog article be? (e.g. Short, Medium, Long)"),
        return self.LENGTH

    async def length(self, update: Update, context: CallbackContext):
        context.user_data['length'] = update.message.text
        await update.message.reply_text(
            "Great! What language level should it be? (e.g. Beginner, Intermediate, Advanced)")
        return self.LANGUAGE_LEVEL

    async def language_level(self, update: Update, context: CallbackContext):
        context.user_data['language_level'] = update.message.text
        await update.message.reply_text(
            "Great! What information level should it be? (e.g. High, Intermediate, Low)")
        return self.INFORMATION

    async def information(self, update: Update, context: CallbackContext):
        context.user_data['information'] = update.message.text
        await update.message.reply_text(
            "Great! What language should it be? (e.g. English, German, Spanish)")
        return self.LANGUAGE

    async def language(self, update: Update, context: CallbackContext):
        context.user_data['language'] = update.message.text
        await update.message.reply_text(
            "Great! What tone should it be? (e.g. Professional, Casual, Friendly)")
        return self.TONE

    async def tone(self, update: Update, context: CallbackContext):
        context.user_data['tone'] = update.message.text
        # Confirm the selections
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

    async def confirm(self, update: Update, context: CallbackContext):
        if update.message.text.lower() == 'yes':
            # Generate response based on inputs
            user_data = context.user_data
            inputs = {
                'topic': user_data['topic'],
                'length': user_data['length'],
                'information_level': user_data['information'],
                'language_level': user_data['language_level'],
                'tone': user_data['tone'],
                'language': user_data['language'],
            }
            filtered_tools = [tool for tool in self.tools if tool is not None]
            bot = BaRagmasChatbot(filtered_tools)
            response = str(bot.crew().kickoff(inputs=inputs))
            response = await update.message.reply_text(response)
            return ConversationHandler.END
        else:
            await update.message.reply_text("Let's start over!")
            return self.start(update, context)

    async def cancel(self, update: Update, context: CallbackContext):
        await update.message.reply_text("Conversation canceled. Type /start to begin again.")
        return ConversationHandler.END

    def start_bot(self) -> None:
        """Start the bot."""
        # Create the Application and pass it your bot's token.
        application = Application.builder().token("7727696877:AAEo2aSGPDj0QgBXhk97UWQP8urrgaXuLFw").build()

        # on different commands - answer in Telegram
        #application.add_handler(CommandHandler("help", self.help_command))

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
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
        # on non command i.e message - echo the message on Telegram
        #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.question))

        # Run the bot until the user presses Ctrl-C

        application.add_handler(conv_handler)
        application.run_polling()

    def addWebsite(self, url):
        self.tools.append(
            WebsiteSearchTool(
                website=url,
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
                ),
            )
        )

    def addPDF(self, location):
        self.tools.append(
            PDFSearchTool(
                pdf=location,
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
