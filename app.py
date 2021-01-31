import logging
logging.basicConfig(level=logging.DEBUG)

# Import the async app instead of the regular one
from slack_bolt.async_app import AsyncApp

# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
app = AsyncApp()

@app.event("app_mention")
async def event_test(body, say, logger):
    logger.info(body)
    await say("What's up?")

@app.command("/hello-bolt-python")
async def command(ack, body, respond):
    await ack()
    await respond(f"Hi <@{body['user_id']}>!")

if __name__ == "__main__":
    app.start(3000)  # POST http://localhost:3000/slack/events
