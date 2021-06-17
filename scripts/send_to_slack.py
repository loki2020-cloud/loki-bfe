import os
from slack import WebClient
from slack.errors import SlackApiError

def sendToSlack(channel: str, text: str):
    SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
    client = WebClient(token=SLACK_BOT_TOKEN)
    try:
        client.chat_postMessage(channel=channel, text=text)

    except SlackApiError as e:
        error = e.response["error"]
        print(error)
        assert error