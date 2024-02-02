import os
import sys
import datetime

import openai
from openai import OpenAI

# as of Jan 2024: https://openai.com/pricing
# using gpt-4-turbo model
cost_per_input_token = 0.01 / 1000
cost_per_output_token = 0.03 / 1000
model = "gpt-4-turbo-preview"


def main():
    token = os.getenv("OPENAI_API_KEY")
    if token == None or not token.startswith("sk-"):
        print("ERROR: OPENAI_API_KEY must be set and must start with 'sk-...'")
        sys.exit(1)

    client = OpenAI(
        api_key=token,
    )
    welcome()
    # write a timestamp for when this session began to history file:
    write_message_to_history("\n\nSTART {} UTC".format(datetime.datetime.now(datetime.UTC)))
    cumulative_cost = 0.0
    prev_tokens = 0
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

        # make a "user" content message to pass to openai chat completion API
        msg = {"role": "user", "content": user_input}
        write_message_to_history(msg)
        messages.append(msg)
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=4050-prev_tokens,
        )
        print("🤖:")
        print()
        print(resp.choices[0].message.content.strip())
        # response from openai is an "assistant" content message to be passed on the next prompt
        msg = {"role": "assistant", "content": resp.choices[0].message.content}
        write_message_to_history(msg)
        messages.append(msg)
        # calculate and print token and dollar cost
        cumulative_cost = cost(
            resp.usage.prompt_tokens, resp.usage.completion_tokens, cumulative_cost
        )
        prev_tokens = resp.usage.prompt_tokens + resp.usage.completion_tokens
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
    print("  openai chat model: ", model)
    print("  openai python library version: ", openai.version.VERSION)
    print("  python version: ", sys.version)
    print(flush=True)


def cost(prompt_tokens, completion_tokens, cumulative_cost):
    total_tokens = prompt_tokens + completion_tokens
    print()
    print()
    print("💰:")
    print(
        "  tokens: prompt={} response={}, total={}".format(
            prompt_tokens,
            completion_tokens,
            total_tokens,
        )
    )
    cost = prompt_tokens * cost_per_input_token
    cost += completion_tokens * cost_per_output_token
    cumulative_cost += cost
    print("  cost: ${:.6f}".format(cost))
    print("  cumulative cost: ${:.6f}".format(cumulative_cost))
    print()
    return cumulative_cost


if __name__ == "__main__":
    main()
