"""
    This is a guestbook application built with FastHTML.
    https://github.com/Sven-Bo/fasthtml-guestbook-supabase
    supabase_project_learning_pass = CHsj9mb*#*5N!8
"""

import os
import pytz
from datetime import datetime


from fasthtml.common import *
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

app, rt = fast_app(
    hdrs=(
        Link(
            rel="icon",
            type="assets/x-icon",
            href="/assets/favicon.png"
        ),
    )
)

MAX_NAME_LENGTH = 15
MAX_MESSAGE_LENGTH = 50
TIMESTAMP_FORMAT = "%Y-%m-%d %I:%M:%S %p CET"

def get_cet_time():
    cet_timezone = pytz.timezone("CET")
    return datetime.now(cet_timezone)

def add_message(name, message):
    timestamp = get_cet_time().strftime(TIMESTAMP_FORMAT)
    supabase.table("guestbook").insert({
        "name": name,
        "message": message,
        "timestamp": timestamp
    }).execute()

def get_messages():
    response = (
        supabase.table("guestbook").select("*").order("created_at", desc=True).execute()
    )
    return response.data

def render_message(message):
    article = Article(
        Header(
            message["name"]
        ),
        P(
            message["message"]
        ),
        Footer(
            Small(Em(f"Posted on: {message['timestamp']}"))
        )
    )
    
    return article

def render_message_list():
    messages = get_messages()
    
    return Div(
        *[render_message(message) for message in messages],
        id="message-list"
    )
    

def render_content():
    
    form = Form(
        Fieldset(
            Input(
                type="text",
                name="name",
                placeholder="Your name",
                required=True,
                maxlength=MAX_NAME_LENGTH
            ),
            Input(
                type="text",
                name="message",
                placeholder="Message",
                required=True,
                maxlength=MAX_MESSAGE_LENGTH
            ),
            Button(
                "Submit",
                type="submit"                
            ),
            role="group"
        ),
        method="post",
        hx_post="/submit-message",
        hx_target="#message-list",
        hx_swap="outerHTML",
        hx_on__after_request="this.reset()"
    )
    
    return Div(
        P(
            Em("Write something nice!")
        ),
        form,
        Div(
            "Made with love by ",
            A(
                "Foysal",
                href="https://github.com/foysal-mamun",
                target="_blank"
            )
        ),
        Hr(),
        render_message_list(),
    )
    
    

@rt("/")
def get():
    return Titled(
        "Guestbook 📖",
        render_content()
    )
    
@rt("/submit-message", methods=["POST"])
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()

serve()
