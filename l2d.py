from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import requests

import os
import json

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['LINEBOT_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINEBOT_SECRET'])

discord_webhook = os.environ['DISCORD_WEBHOOK']

print("l2d: LINEBOT_ACCESS_TOKEN - " + os.environ['LINEBOT_ACCESS_TOKEN'])
print("l2d: LINEBOT_SECRET - " + os.environ['LINEBOT_SECRET'])
print("l2d: DISCORD_WEBHOOK - " + os.environ['DISCORD_WEBHOOK'])


@app.route("/")
def root():
    return 'OK'


@app.route("/callback", methods=['POST'])
def callback():
    sign = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)

    try:
        handler.handle(body, sign)
    except InvalidSignatureError:
        print("Invalid signature. Check token and/or secret")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("l2d: handle_message()")
    content = event.message.text
    if content.startswith("!"): content = "\"" + content + "\""
    if content.startswith("/"): content = "\"" + content + "\""
    if content.startswith("\\"): content = "\"" + content + "\""
    if content.startswith("$"): content = "\"" + content + "\""
    content += "\n" + str(event)
    profile = line_bot_api.get_group_member_profile(
        event.source.group_id, event.source.user_id)
    print("l2d: " + profile.display_name + " from LINE - " + event.message.text)
    request_data = {
        "content": event.message.text,
        "username": profile.display_name + " from LINE",
        "avatar_url": profile.picture_url
    }
    requests.post(url=discord_webhook, data=request_data)
    print("l2d: handle_message:done")


if __name__ == "__main__":
    app.run()
