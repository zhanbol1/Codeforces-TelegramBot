import telebot
import requests
from table_print import PrettyTable
from telebot.types import BotCommand
import time, datetime
import json
import os
from flask import Flask, request
import threading

app = Flask(__name__)

token = os.environ.get('BOT_TOKEN', '8572921621:AAHuBP8MbltuD42jz-dYUrl5YKyoh4pDEWo')



class CodeForces:
    def __init__(self):
        self.token = token
        self.cf_api = "https://codeforces.com/api/"

        self.bot = telebot.TeleBot(self.token)

        self.commands = [
            BotCommand("rating", "returns rating of handle(s) specified in the next message"),
            BotCommand("current_standings", "returns current standings of friends"),
            BotCommand("upcoming", "returns upcoming contests"),
            BotCommand("add_friends", "adds friend(s) whose handle(s) specified in the next message"),
            BotCommand("remove_friends", "removes friend(s)'s handle(s) specified in the next message"),
            BotCommand("show_friends", "Shows list of friends")
        ]

        self.emojis = {
            "newbie" : "🌸newbie",
            "pupil" : "🦋pupil",
            "specialist" : "🕷specialist",
            "expert" : "🐥expert",
            "candidate master" : "🐱CM",
            "master" : "🐶M",
            "international master" : "🐺IM",
            "grandmaster" : "🧑🏻‍🦱GM",
            "international grandmaster" : "👨🏻‍🎓IGM",
            "legendary grandmaster" : "🧑🏻‍⚕️legend"
        }

        self.setup_handler()
    
    def run_webhook(self, webhook_url=None):
        """Setup webhook instead of polling"""
        if webhook_url:
            self.bot.remove_webhook()
            self.bot.set_webhook(url=webhook_url)
            print(f"Webhook set to: {webhook_url}")
        else:
            # For local testing, fall back to polling
            print("Running in polling mode (local testing)")
            self.bot.infinity_polling()
    
    def setup_handler(self):
        @self.bot.message_handler(commands=["start"])
        def start(message):
            self.bot.set_my_commands(self.commands)
            self.bot.reply_to(message, "CodeForcesBot is ready to go")
        
        @self.bot.message_handler(commands=["add_friends"])
        def pre_add_friend(message):
            self.bot.reply_to(message, "Reply with comma separated handle(s)")
            self.bot.register_next_step_handler(message, add_friend)
        def add_friend(message):
            try:
                raw_handles = str(message.text).strip().split(',')

                with open("handles.json", "r" ) as f:
                    handles = json.load(f)

                
                for handle in raw_handles:
                    ready = handle.strip()
                
                    if ready not in handles:
                        handles[f"{ready}"] = True
                    
                with open("handles.json", "w") as f:
                    json.dump(handles, f, indent=4)
                
                self.bot.reply_to(message, "Friends have been added")
            except Exception as e:
                self.bot.reply_to(message, f"Something went wrong, error: {e}")
            
        @self.bot.message_handler(commands=["remove_friends"])
        def pre_remove_friend(message):
            self.bot.reply_to(message, "Reply with handle(s) to remove")
            self.bot.register_next_step_handler(message, remove_friend)
        
        def remove_friend(message):
            try:
                raw_handles = str(message.text).strip()

                with open("handles.json", "r") as f:
                    handles = json.load(f)

                for handle in raw_handles.split(','):
                    if handle in handles:
                        del handles[f"{handle}"]
                
                with open("handles.json", "w") as f:
                    json.dump(handles, f, indent=4)
                
                self.bot.reply_to(message, "Friends have been deleted")
            except Exception as e:
                self.bot.reply_to(message, f"Error: {e}")
        
        @self.bot.message_handler(commands = ["show_friends"])
        def show_friends(message):
            friends = "<pre>"
            with open("handles.json", "r") as f:
                handles = json.load(f)

            if not handles:
                self.bot.reply_to(message, "You have no friends")
            else:
                for handle in handles:
                    friends += handle + '\n'
                
                friends += "</pre>"

                self.bot.send_message(message.chat.id, friends, parse_mode="HTML")
        
        @self.bot.message_handler(commands=['upcoming'])
        def upcoming(message):
            url = self.cf_api + "contest.list?"

            try:
                response = requests.get(url).json()

                if response["status"] == "OK":
                    data = response["result"]

                    local_time = time.time()
                    lst = []
                    for d in data:
                        if d["phase"] == "BEFORE":
                            contest_time = d["startTimeSeconds"] -local_time

                            date = datetime.datetime.fromtimestamp(d["startTimeSeconds"]).strftime('%a, %d %b %H:%M')
                            
                            in_time = ""
                            minutes = contest_time/60
                            hours = minutes/60
                            days = hours/24

                            if days != 0:
                                in_time += str(int(days)) + " days "
                            if hours != 0:
                                if hours >=24:
                                    hours -= int(days)*24
                                    hour_str = str(int(hours))
                                if len(str(int(hours))) < 2:
                                    hour_str = "0" + str(int(hours))
                                in_time += hour_str + ":"
                                
                            if minutes != 0:
                                if minutes >= 60:
                                    minutes -= (int(hours) *60 + int(days) * 60 * 24)
                                    minute_str = str(int(minutes))

                                if len(str(int(minutes))) < 2:
                                    minute_str = "0" + str(int(minutes))
                                in_time += minute_str + " hours "

                            lst.append(
                                f"*{date}* (in {in_time}) \n{d["name"]} \n"
                            )
                        else:
                            break

                    rev_lst = reversed(lst)

                    text = ""
                    for l in rev_lst:
                        text+=l+'\n'
                        
                self.bot.send_message(message.chat.id, text, parse_mode="MarkDown")
                
            except Exception as e:
                self.bot.reply_to(message, f"Error: {e}")

        
        @self.bot.message_handler(commands=["rating"])
        def rating(message):
            self.bot.reply_to(message, "Reply with comma separated handle(s)")
            self.bot.register_next_step_handler(message, rating_user)

        def rating_user(message):
            handles = message.text.split(",")
            
            new_handles = []
            for handle in handles:
                if handle:
                    new_handles.append(handle.strip())
            
            handles = new_handles

            if not handles:
                self.bot.reply_to(message, "Usage: /rating <handle>")

            url = self.cf_api + "user.info?handles="
            for handle in handles:
                url += handle + ';'
            url += "&checkHistoricHandles=false"

            try:
                response = requests.get(url).json()

                ratings = []
                if response["status"] == "OK":
                    data = response["result"]
                    for d in data:
                        rating = str(d.get("rating", "Unrated"))
                        name = d.get("handle")
                        rank = d.get("rank")
                        ratings.append({
                            "name": name,
                            "rating" : rating,
                            "rank" : rank
                        })
                    
                    text = "<pre>"
                    for rating in ratings:
                        text += self.emojis[rating["rank"]] + " "+rating["name"]+ ":" + rating["rating"] + '\n'
                    text += "</pre>"
                    self.bot.send_message(message.chat.id, text, parse_mode="HTML")
                else:
                    self.bot.reply_to(message, response.get('comment', "Unknown error"))
            except Exception as e:
                self.bot.reply_to(message, f"Error: {e}")
        
        @self.bot.message_handler(commands=["current_standings"])
        def current_standings(message):
            url = "https://codeforces.com/api/contest.list"
        
            try:
                response = requests.get(url).json()
                contest_id= ""

                if response["status"]=="OK":
                    contests = response["result"]
                    for contest in contests:
                        if contest.get("phase") == "FINISHED" or contest.get("phase") == "SYSTEM_TEST":
                            contest_id = str(contest.get("id"))
                            break
                else:
                    self.bot.reply_to(message, f"Error: {response.get('comment', 'Unknown error')}")
            except Exception as e:
                self.bot.reply_to(message, f"Error: {e}")
            
            #open txt file with handles
            with open("handles.json", "r") as file:
                handles_data = json.load(file)
                handles = ','.join(handles_data.keys()).split(',')

            if not handles:
                self.bot.reply_to(message, "Add friends first to see their standings")
            
            else:
                contest_url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&showUnofficial=false&handles="
        
                for handle in handles:
                    contest_url+=handle+";"
                

                try:
                    response = requests.get(contest_url).json()

                    if response["status"] == "OK":
                        to_print = []
                        data = response["result"]

                        #prepare contest name and phase data to sent
                        problem_data = data["contest"]
                        to_print.append({
                            "name":problem_data["name"],
                            "phase":problem_data["phase"]
                        })

                        #prepare problems data to sent
                        problems = []
                        for problem in data["problems"]:
                            problems.append(problem["index"])

                        to_print.append({
                            "problems" : problems
                        })

                        #prepare user solvings data to sent
                        user_data = data["rows"]
                        
                        for user in user_data:
                            name = user["party"]["members"][0]["handle"]
                            if user["party"]["participantType"] == "OUT_OF_COMPETITION":
                                name = "* " + name

                            rank = user["rank"]

                            problems_l = user["problemResults"]
                            solved_l = []
                            for problem in problems_l:
                                if problem["points"] == 0:
                                    if problem["rejectedAttemptCount"] != 0:
                                        solved_l.append(f"-{problem["rejectedAttemptCount"]}")
                                    else:
                                        solved_l.append("")
                                else:
                                    if problem["rejectedAttemptCount"] != 0:
                                        solved_l.append(f"+{problem["rejectedAttemptCount"]}")
                                    else:
                                        solved_l.append("+")

                            to_print.append({
                                "handle" : name,
                                "rank" : f"({rank})",
                                "points" : solved_l
                            })

                        #sent the message
                        table = PrettyTable(to_print)
                        table_result = table.generate_table()

                        text ="\nCodeforces Round 1074 (Div. 4) FINISHED <pre>" + f"\n{table_result}" + "\n</pre>"
                        
                        self.bot.send_message(message.chat.id, text, parse_mode="HTML")

                    else:
                        self.bot.reply_to(message, f"Error: {response.get('comment', 'Unknown error')}")

                except Exception as e:
                    self.bot.reply_to(message, f"Error {e}")


bot_instance = CodeForces()

# ========== FLASK ROUTES ==========
@app.route('/')
def home():
    """Home page to check if bot is running"""
    return """
    <h1>🤖 CodeForces Telegram Bot</h1>
    <p>Bot is successfully deployed on PythonAnywhere!</p>
    <p><a href="/setwebhook">Set Webhook</a> | <a href="/deletewebhook">Delete Webhook</a></p>
    <p>Commands available: /start, /rating, /current_standings, /upcoming, /add_friends, /remove_friends, /show_friends</p>
    """

@app.route('/setwebhook')
def set_webhook():
    """Manually set webhook"""
    # Get your PythonAnywhere URL automatically
    pythonanywhere_url = "https://" + os.environ.get('PYTHONANYWHERE_SITE', 'janbol.pythonanywhere.com')
    webhook_url = f"{pythonanywhere_url}/webhook"
    
    bot_instance.bot.remove_webhook()
    result = bot_instance.bot.set_webhook(url=webhook_url)
    
    return f"""
    <h2>Webhook Set Result</h2>
    <p><strong>URL:</strong> {webhook_url}</p>
    <p><strong>Success:</strong> {result}</p>
    <p><a href="/">← Back</a></p>
    """

@app.route('/deletewebhook')
def delete_webhook():
    """Delete webhook"""
    result = bot_instance.bot.remove_webhook()
    return f"""
    <h2>Webhook Deleted</h2>
    <p><strong>Result:</strong> {result}</p>
    <p><a href="/">← Back</a></p>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    """Main webhook endpoint - Telegram sends updates here"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot_instance.bot.process_new_updates([update])
        return 'OK', 200
    return 'Bad request', 400

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK', 200

# ========== FILE INITIALIZATION ==========
def initialize_files():
    """Create necessary files if they don't exist"""
    # Create handles.json if doesn't exist
    if not os.path.exists("handles.json"):
        with open("handles.json", "w") as f:
            json.dump({}, f)


# ========== MAIN ENTRY POINT ==========
if __name__ == '__main__':
    # Initialize files
    initialize_files()
    
    # For local testing - run in polling mode
    print("Starting bot in polling mode (local testing)...")
    bot_instance.run_webhook()  # No URL = polling mode
else:
    # For production (PythonAnywhere) - files will be initialized when imported
    initialize_files()