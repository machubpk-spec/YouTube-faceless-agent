import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

models = client.models.list()
print("Models available to this Groq API key:\n")
for m in models.data:
    print(f"- {m.id}")
