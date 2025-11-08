import telebot
from telebot import types
import json, os

TOKEN = "8291059047:AAEHgY7CPnuFS4V8DSwW1d_AGFWu3aqAIgc"
bot = telebot.TeleBot(TOKEN)

STORY_PATH = "data/stories"
current_story = {}

def load_story(name):
    path = os.path.join(STORY_PATH, f"{name}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🏚 Дом на краю леса (ужастик)", callback_data="story_horror"),
        types.InlineKeyboardButton("🗺 Потерянный остров (приключение)", callback_data="story_island")
    )
    bot.send_message(message.chat.id, "Привет! Добро пожаловать в *StoryHub* — бот-квест.\nВыбери историю:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("story_"))
def choose_story(call):
    story_id = call.data.split("_", 1)[1]
    current_story[call.message.chat.id] = load_story(story_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f"📖 История загружена: *{story_id}*\nНачинаем...", parse_mode="Markdown")
    show_scene(call.message.chat.id, "start")

def show_scene(chat_id, scene_id):
    story = current_story[chat_id]
    scene = story[scene_id]
    text = scene["text"]
    markup = types.InlineKeyboardMarkup()
    for opt in scene.get("options", []):
        markup.add(types.InlineKeyboardButton(text=opt["text"], callback_data=opt["next"]))
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_choice(call):
    story = current_story.get(call.message.chat.id)
    if not story:
        bot.send_message(call.message.chat.id, "Сначала выбери историю через /start.")
        return
    scene_id = call.data
    if scene_id not in story:
        bot.send_message(call.message.chat.id, "Сцена не найдена, конец истории.")
        return
    scene = story[scene_id]
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=scene["text"])
    if "options" in scene:
        markup = types.InlineKeyboardMarkup()
        for opt in scene["options"]:
            markup.add(types.InlineKeyboardButton(text=opt["text"], callback_data=opt["next"]))
        bot.send_message(call.message.chat.id, "Выбери действие:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "🏁 Конец истории.\nХочешь попробовать другую? /start")

print("🤖 Bot is running...")
bot.polling(none_stop=True)
