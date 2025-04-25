import os
import openai
from dotenv import load_dotenv
from openai import OpenAI

# Load the API key from the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

print("OpenAI API Key:", os.getenv("OPENAI_API_KEY"))


def chat_with_openai():
    print("Start a conversation with OpenAI (type 'exit' to quit):")
    conversation_history = []

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Conversation ended.")
            break

        # Add user input to the conversation history
        conversation_history.append({"role": "user", "content": user_input})

        # Call the OpenAI API
        try:
            response = client.responses.create(
                model="gpt-3.5-turbo",
                temperature=0.7,
                instructions="",
                input=user_input,
            )
            assistant_reply = response.output_text
            print(f"Assistant: {assistant_reply}")

            # Add assistant reply to the conversation history
            conversation_history.append({"role": "assistant", "content": assistant_reply})
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    chat_with_openai()