import os
import json
import threading
from flask import Flask, request, render_template_string
from fbchat import Client
from fbchat.models import Message, ThreadType

app = Flask(__name__)
bot_client = None
admin_id = None
group_name_lock = None
nickname_lock = None
antiout_enabled = False
sticker_spam = False
loder_target = None
autoconvo_enabled = False

# Load HTML file
with open("index.html", "r") as f:
    HTML_PAGE = f.read()

class ShalenderBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        global group_name_lock, nickname_lock, antiout_enabled, sticker_spam, loder_target, autoconvo_enabled

        if author_id != admin_id:
            return

        msg = message_object.text
        if not msg:
            return

        # Help command
        if msg == "!help":
            help_text = """
Commands:
!help - Show all commands
!groupnamelock on <name> - Lock group name
!nicknamelock on <nickname> - Lock all nicknames
!tid - Get group ID
!uid - Get your ID
!uid @mention - Get mentioned user's ID
!info @mention - Get user information
!group info - Get group information
!pair - Pair two random members
!music <song name> - Play YouTube music
!antiout on/off - Toggle anti-out feature
!send sticker start/stop - Sticker spam
!autospam accept - Auto accept spam messages
!automessage accept - Auto accept message requests
!loder target on @user - Target a user
!loder stop - Stop targeting
autoconvo on/off - Toggle auto conversation
"""
            self.send(Message(text=help_text), thread_id=thread_id, thread_type=thread_type)

        elif msg.startswith("!tid"):
            self.send(Message(text=f"Group ID: {thread_id}"), thread_id=thread_id, thread_type=thread_type)

        elif msg.startswith("!uid"):
            self.send(Message(text=f"Your ID: {author_id}"), thread_id=thread_id, thread_type=thread_type)

        elif msg.startswith("!group info"):
            info = self.fetchThreadInfo(thread_id)[thread_id]
            self.send(Message(text=f"Group name: {info.name}, Members: {info.participants}"), thread_id=thread_id, thread_type=thread_type)

        elif msg.startswith("!antiout on"):
            antiout_enabled = True
            self.send(Message(text="✅ Anti-out enabled"), thread_id=thread_id, thread_type=thread_type)

        elif msg.startswith("!antiout off"):
            antiout_enabled = False
            self.send(Message(text="❌ Anti-out disabled"), thread_id=thread_id, thread_type=thread_type)

        elif msg.startswith("!send sticker start"):
            sticker_spam = True
            self.send(Message(text="Sticker spam started!"), thread_id=thread_id, thread_type=thread_type)

        elif msg.startswith("!send sticker stop"):
            sticker_spam = False
            self.send(Message(text="Sticker spam stopped!"), thread_id=thread_id, thread_type=thread_type)

        elif msg.startswith("autoconvo on"):
            autoconvo_enabled = True
            self.send(Message(text="Auto conversation enabled"), thread_id=thread_id, thread_type=thread_type)

        elif msg.startswith("autoconvo off"):
            autoconvo_enabled = False
            self.send(Message(text="Auto conversation disabled"), thread_id=thread_id, thread_type=thread_type)

        elif msg.startswith("!loder target on"):
            loder_target = msg.split(" ")[-1]
            self.send(Message(text=f"Loder started on {loder_target}"), thread_id=thread_id, thread_type=thread_type)

        elif msg.startswith("!loder stop"):
            loder_target = None
            self.send(Message(text="Loder stopped"), thread_id=thread_id, thread_type=thread_type)

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE)

@app.route("/start", methods=["POST"])
def start():
    global bot_client, admin_id
    cookies = json.loads(request.form["cookies"])
    admin_id = request.form["admin_id"]

    def run_bot():
        global bot_client
        bot_client = ShalenderBot(" ", " ", session_cookies=cookies)
        bot_client.listen()

    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    return "Bot started!"

@app.route("/stop", methods=["POST"])
def stop():
    global bot_client
    if bot_client:
        bot_client.logout()
        bot_client = None
    return "Bot stopped!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
