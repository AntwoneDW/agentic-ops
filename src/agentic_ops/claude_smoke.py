import os

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

client = Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"]
)

model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")


# Verify direct connectivity to the Anthropic provider independently
# of the agent orchestration layer.
message = client.messages.create(
    model=model,
    max_tokens=300,
    system=(
        "You are the reasoning component of an AI operations system. "
        "Be concise and technical."
    ),
    messages=[
        {
            "role": "user",
            "content": (
                "The checkout service is returning HTTP 503 errors. "
                "We do not yet have logs or metrics. "
                "What should we investigate first?"
            ),
        }
    ],
)


# Claude responses contain typed content blocks.
# For this smoke test, print only text blocks returned by the model.
for block in message.content:
    if block.type == "text":
        print(block.text)