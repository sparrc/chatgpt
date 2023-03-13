import os
import openai
import sys
import datetime

# as of March 2023: https://openai.com/pricing
cost_per_token = 0.002 / 1000


def main():
    token = os.getenv("OPENAI_API_KEY")
    if token == None or not token.startswith("sk-"):
        print("ERROR: OPENAI_API_KEY must be set and must start with 'sk-...'")
        sys.exit(1)

    welcome()
    write_message_to_history("\n\nSTART {} UTC".format(datetime.datetime.utcnow()))
    cumulative_cost = 0.0
    messages = []
    while True:
        try:
            user_input = input("--> ").strip()
        except KeyboardInterrupt:
            return

        if user_input == "exit":
            return
        if user_input == "":
            continue

        msg = {"role": "user", "content": user_input}
        write_message_to_history(msg)
        messages.append(msg)
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1500,
        )
        print("🤖:")
        print()
        print(resp.choices[0].message.content.strip())
        msg = {"role": "assistant", "content": resp.choices[0].message.content}
        write_message_to_history(msg)
        messages.append(msg)
        print()
        print()
        print("💰:")
        print(
            "  tokens: prompt={} response={}, total={}".format(
                resp.usage.prompt_tokens,
                resp.usage.completion_tokens,
                resp.usage.total_tokens,
            )
        )
        cost = resp.usage.total_tokens * cost_per_token
        cumulative_cost += cost
        print("  cost: ${:.6f}".format(resp.usage.total_tokens * cost_per_token))
        print("  cumulative cost: ${:.6f}".format(cumulative_cost))
        print()
        print("*******************************")


def write_message_to_history(m):
    with open("/.chatgpt_history", "a") as f:
        f.write("{}\n".format(m))


def welcome():
    print("Welcome to the ChatGPT command-line chatbot 🤖")
    print("  enter your questions at the prompt.")
    print("  type 'exit' or use ctrl-C to exit.")
    print()
    print("version info:")
    print("  openai library version: ", openai.version.VERSION)
    print("  python version: ", sys.version)
    print(flush=True)


if __name__ == "__main__":
    main()
