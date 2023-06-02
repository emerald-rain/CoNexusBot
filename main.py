import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

bot = Bot(token="YOUR_BOT_TOKEN")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
API_KEY = "YOUR_API_KEY"

my_prompt = "Now we are going to play a game. Your goal is to choose among options. You only need to choose the answer that will potentially lead to victory. Use the style of play that is most likely to lead to victory. The goal of the game is to get to a spaceship called Inception Ark. You will receive messages of this type: *History* Options Step** Option Option Option Option. Make a short answer, no more than 200 characters, in the form Option. This is the best option because..."

author_button = KeyboardButton("Author✍️")
how_to_button = KeyboardButton("How to👋")
explore_button = KeyboardButton("Explore the Multiverse🗺️")
finish_button = KeyboardButton("Finish the game🏁")

main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(how_to_button, author_button).add(explore_button)

@dp.message_handler(commands=["start"])
async def handle_start(message: types.Message):
    message_text = 'Hi, this is a 🤖 that will play CoNexus with you. You can use him as an assistant, i.e. you can listen to the bot, but still decide what to do yourself. Or, you can use him as a full bot to win the game for you.'
    await bot.send_message(message.chat.id, message_text, reply_markup=main_menu_keyboard, parse_mode="HTML")

    message_text = 'To play with him you need to copy the questions together with the answer choices, so that the bot could choose the best one in his opinion and explain why.'
    await bot.send_message(message.chat.id, message_text, reply_markup=main_menu_keyboard, parse_mode="HTML")

@dp.message_handler(lambda message: message.text == "Author✍️")
async def handle_button_settings(message: types.Message):
    await bot.send_message(message.chat.id, "Created by @AlbertMalysh with inspiration from @kusamaximalist💚.", parse_mode="HTML")

@dp.message_handler(lambda message: message.text == "How to👋")
async def handle_button_how_to(message: types.Message):
    message_text = '''<b>Where do you get your story and options from?</b> - <a href="https://degenerousdao.com/CoNexus/">CoNexus</a>.
<b>I can't start the game.</b> - You most likely <a href="https://raresama.com/collections/2109/0x1acb10dbd319da52d941dfec478f1aa2d118d7f7">need to buy Inception Ark</a>.

<b>How do I use the helper correctly?</b>
1. Click on "Explore the Multiverse"🗺️.
2. Start the game and start copying from the beginning of the story to the end of the last answer choice. <a href="https://snipboard.io/KnfZkC.jpg">Example.👋</a>
3. Send it as a normal message. <a href="https://snipboard.io/V4wFsU.jpg">Example.👋</a>
4. After you finish the game, click "Finish the game"🏁.'''
    await bot.send_message(message.chat.id, message_text, parse_mode="HTML")

conversation_state = []
exploration_started = False

@dp.message_handler(lambda message: message.text == "Explore the Multiverse🗺️" and not exploration_started)
async def handle_button_start(message: types.Message):
    global conversation_state, exploration_started
    conversation_state = []
    exploration_started = True

    message_text = '🤖 Start the game at <a href="https://degenerousdao.com/conexus">CoNexus Webpage</a> and send your story and character choices here for the best AI recommendations.'
    await bot.send_message(message.chat.id, message_text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(finish_button), parse_mode="HTML")

@dp.message_handler(lambda message: exploration_started and message.text != "Finish the game🏁")
async def handle_user_message(message: types.Message):
    global conversation_state

    conversation_state.append({"role": "user", "content": message.text})

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": my_prompt}] + conversation_state,
        "max_tokens": 1000
    }
    response = requests.post(API_ENDPOINT, headers=headers, json=payload)
    data = response.json()

    reply = data["choices"][0]["message"]["content"]
    conversation_state.append({"role": "assistant", "content": reply})
    await bot.send_message(message.chat.id, reply)

@dp.message_handler(lambda message: message.text == "Finish the game🏁")
async def handle_button_finish(message: types.Message):
    global conversation_state, exploration_started
    conversation_state = []
    exploration_started = False

    await bot.send_message(message.chat.id, "The game has been finished. You can start a new game by clicking on 'Explore the Multiverse🗺️'.", reply_markup=main_menu_keyboard)

if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)