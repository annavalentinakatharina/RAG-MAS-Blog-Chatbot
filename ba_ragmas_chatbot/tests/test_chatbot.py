import os
from unittest.mock import MagicMock, AsyncMock

import pytest
from telegram import Message, Update
from telegram.ext import CallbackContext

from src.ba_ragmas_chatbot.chatbot import TelegramBot


@pytest.mark.asyncio
async def test_chat_startConfiguration():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "start configuration"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.chat(mock_update, mock_context)

    mock_message.reply_text.assert_called_once_with(
        "Great, you want to start the blog article configuration! First, what topic should the blog article be about? Or what task should the blog article fulfil? If you have a topic please respond with 'topic', if you have a separate task please respond with 'task'."
    )
    #assert
    assert result == 3

@pytest.mark.asyncio
async def test_chat_anyOtherText():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "Hello how are you?"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.chat(mock_update, mock_context)

    #assert
    assert result == 0

@pytest.mark.asyncio
async def test_topic_or_task_task():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "task"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.topic_or_task(mock_update, mock_context)
    #assert
    mock_message.reply_text.assert_called_once_with(
        "Okay, task it is! What task should the blog article fulfil?"
    )
    assert result == 2

@pytest.mark.asyncio
async def test_topic_or_task_topic():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "topic"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.topic_or_task(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_called_once_with(
        "Okay, topic it is! What topic should the blog article be about?"
    )
    assert result == 1

@pytest.mark.asyncio
async def test_topic_or_task_none():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "nothing"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.topic_or_task(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_called_once_with(
        "Not valid, please respond with either 'topic' or 'task'."
    )
    assert result == 3

@pytest.mark.asyncio
async def test_topic_or_task_throw_error():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "nothing"
    mock_message.reply_text = AsyncMock(side_effect=[
        Exception("Simulated error in topic_or_task"),
        None
    ])
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.topic_or_task(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_any_call(
        "An error occurred: Simulated error in topic_or_task. \nPlease answer with 'topic' or 'task' again.")


@pytest.mark.asyncio
async def test_topic():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "Dogs"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.topic(mock_update, mock_context)
    #assert
    mock_message.reply_text.assert_called_once_with(
        "Great! Do you have a link to a website with information you want to have included? If yes, please reply with the link, if not, please just send 'no'."
    )
    assert result == 4

@pytest.mark.asyncio
async def test_topic_throw_error():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "nothing"
    mock_message.reply_text = AsyncMock(side_effect=[
        Exception("Simulated error in topic"),
        None
    ])
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.topic(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_any_call(
        "An error occurred: Simulated error in topic. \nPlease resend your topic.")


@pytest.mark.asyncio
async def test_task():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "Write an article about dogs"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.task(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_called_once_with(
        "Great! Do you have a link to a website with information you want to have included? If yes, please reply with the link, if not, please just send 'no'."
    )
    assert result == 4

@pytest.mark.asyncio
async def test_task_throw_error():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "nothing"
    mock_message.reply_text = AsyncMock(side_effect=[
        Exception("Simulated error in task"),
        None
    ])
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.task(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_any_call(
        "An error occurred: Simulated error in task. \nPlease resend your task.")


@pytest.mark.asyncio
async def test_website_no():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "no"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.website(mock_update, mock_context)
    #assert
    mock_message.reply_text.assert_called_once_with(
        "Great! Do you have a document with information you want to have included? If yes, please reply with the document, if not, please just send 'no'."
    )
    assert result == 5

@pytest.mark.asyncio
async def test_website_website():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "https://en.wikipedia.org/wiki/Dog"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.website(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_called_once_with(
                        "Great! Do you have a document with information you want to have included? If yes, please reply with the document, if not, please just send 'no'."
    )
    assert result == 5

@pytest.mark.asyncio
async def test_website_throw_error():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "nothing"
    mock_message.reply_text = AsyncMock(side_effect=[
        Exception("Simulated error in website"),
        None
    ])
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.website(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_any_call(
        "An error occurred: Simulated error in website. \nPlease resend your link or 'no'.")


@pytest.mark.asyncio
async def test_no_documents_no():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "no"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.no_document(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_called_once_with(
                        "How long should the blog article be? (e.g. Short, Medium, Long)"
    )
    assert result == 6

@pytest.mark.asyncio
async def test_no_documents_not_no():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "nothing"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.no_document(mock_update, mock_context)

    #assert
    assert result == 5

@pytest.mark.asyncio
async def test_no_document_throw_error():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "nothing"
    mock_message.reply_text = AsyncMock(side_effect=[
        Exception("Simulated error in no_document"),
        None
    ])
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.no_document(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_any_call(
        "An error occurred: Simulated error in no_document. \nPlease resend your document or 'no'.")


@pytest.mark.asyncio
async def test_documents_throw_error():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.document = MagicMock()
    mock_message.document.mime_type = "application/pdf"
    mock_message.document.file_name = "test_document.pdf"
    mock_message.document.file_id = "file_id_mock"
    mock_message.reply_text = AsyncMock()

    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    mock_context.bot.get_file.side_effect = Exception("Simulated download error")
    bot = TelegramBot()

    #act
    result = await bot.document(mock_update, mock_context)

    assert result == 5

@pytest.mark.asyncio
async def test_documents_document():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.document = MagicMock()
    mock_message.document.mime_type = "application/pdf"
    mock_message.document.file_name = "RAG_PDF.pdf"
    mock_message.document.file_id = "file_id_mock"
    mock_message.reply_text = AsyncMock()

    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    mock_context.bot.get_file = AsyncMock()

    base_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(base_dir)
    test_file_path = os.path.join(root_dir, "src", "ba_ragmas_chatbot", "documents", "RAG_PDF.pdf")

    mock_file = MagicMock()
    mock_file.download_to_drive = AsyncMock(return_value=None)  # No-op for download
    mock_context.bot.get_file.return_value = mock_file


    bot = TelegramBot()

    #act
    result = await bot.document(mock_update, mock_context)
    mock_file.download_to_drive.assert_called_once_with(
        '/Users/avkh/Desktop/Studium/Bachelorarbeit/Git/RAG-MAS-Blog-Chatbot/ba_ragmas_chatbot/src/ba_ragmas_chatbot/documents/RAG_PDF.pdf'
    )

    mock_file.download_to_drive.assert_called_once_with(test_file_path)

    assert result == 6

@pytest.mark.asyncio
async def test_length():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "Short"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.length(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_called_once_with(
        "Great! What language level should it be? (e.g. Beginner, Intermediate, Advanced)"
    )
    assert result == 7

@pytest.mark.asyncio
async def test_length_throw_error():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "nothing"
    mock_message.reply_text = AsyncMock(side_effect=[
        Exception("Simulated error in length"),
        None
    ])
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.length(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_any_call(
        "An error occurred: Simulated error in length. \nPlease resend your preferred article length.")


@pytest.mark.asyncio
async def test_language_level():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "Advanced"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.language_level(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_called_once_with(
        "Great! What information level should it be? (e.g. High, Intermediate, Low)"
    )
    assert result == 8

@pytest.mark.asyncio
async def test_language_level_throw_error():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "nothing"
    mock_message.reply_text = AsyncMock(side_effect=[
        Exception("Simulated error in language_level"),
        None
    ])
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.language_level(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_any_call(
        "An error occurred: Simulated error in language_level. \nPlease resend your preferred article language level.")


@pytest.mark.asyncio
async def test_information():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "High"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.information(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_called_once_with(
        "Great! What language should it be? (e.g. English, German, Spanish)"
    )
    assert result == 9

@pytest.mark.asyncio
async def test_information_throw_error():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "nothing"
    mock_message.reply_text = AsyncMock(side_effect=[
        Exception("Simulated error in information"),
        None
    ])
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.information(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_any_call(
        "An error occurred: Simulated error in information. \nPlease resend your preferred article information level.")


@pytest.mark.asyncio
async def test_language():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "English"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.language(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_called_once_with(
        "Great! What tone should it be? (e.g. Professional, Casual, Friendly)"
    )
    assert result == 10

@pytest.mark.asyncio
async def test_language_throw_error():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "nothing"
    mock_message.reply_text = AsyncMock(side_effect=[
        Exception("Simulated error in language"),
        None
    ])
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.language(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_any_call(
        "An error occurred: Simulated error in language. \nPlease resend your preferred article language.")


@pytest.mark.asyncio
async def test_tone():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "Professional"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.tone(mock_update, mock_context)

    #assert
    assert result == 11

@pytest.mark.asyncio
async def test_tone_throw_error():
    #arrange
    mock_message = MagicMock(spec=Message)
    mock_message.text = "nothing"
    mock_message.reply_text = AsyncMock(side_effect=[
        Exception("Simulated error in tone"),
        None
    ])
    mock_update = MagicMock(spec=Update)
    mock_update.message = mock_message

    mock_context = MagicMock(spec=CallbackContext)
    bot = TelegramBot()

    #act
    result = await bot.tone(mock_update, mock_context)

    #assert
    mock_message.reply_text.assert_any_call(
        "An error occurred: Simulated error in tone. \nPlease resend your preferred article tone.")
