# --------------------------------------------------------------
#  groq_example.py
# --------------------------------------------------------------
from groq import Groq
import os
from dotenv import load_dotenv   # pip install python-dotenv   (optional)

# --------------------------------------------------------------
# Load .env if you have one (does nothing if file missing)
# --------------------------------------------------------------
load_dotenv()   # <-- remove if you don't use a .env file

# --------------------------------------------------------------
# Verify the key exists (helps with debugging)
# --------------------------------------------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError(
        "❗️ GROQ_API_KEY not set. "
        "Set it in your environment or a .env file."
    )

# --------------------------------------------------------------
# Create the client – explicit key passing (clear & testable)
# --------------------------------------------------------------
client = Groq(api_key=api_key)

# --------------------------------------------------------------
# Make a chat completion request
# --------------------------------------------------------------
completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "Hello, Groq!"}],
    temperature=1,
    max_completion_tokens=8192,
    top_p=1,
    reasoning_effort="medium",
    stream=True,
    stop=None,
)

# --------------------------------------------------------------
# Stream the response to stdout
# --------------------------------------------------------------
for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
print()   # final newline