import os
import sys
import datetime

import openai
from openai import OpenAI

DEFAULT_MODEL = "gpt-4.1-mini"

def main():
    token = os.getenv("OPENAI_API_KEY")
    if token == None or not token.startswith("sk-"):
        print("ERROR: OPENAI_API_KEY must be set and must start with 'sk-...'")
        sys.exit(1)

    model = os.getenv("OPENAI_MODEL")
    if model == None or len(model) == 0:
        model = DEFAULT_MODEL

    client = OpenAI(
        api_key=token,
    )
    welcome(model)
    # write a timestamp for when this session began to history file:
    write_message_to_history(
        "\n\nSTART {} UTC".format(datetime.datetime.now(datetime.UTC))
    )
    cumulative_cost = 0.0
    prev_tokens = 0
    messages = []
    while True:
        print("Enter you query below, two blank lines is interpreted as end of input.")
        contents = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            except KeyboardInterrupt:
                return
            if line.strip() == "":
                if len(contents) > 0 and contents[len(contents) - 1].strip() == "":
                    # two blank lines
                    break
            if line.strip() == "exit":
                break
            contents.append(line)

        user_input = "\n".join(contents)

        if user_input.strip() == "exit":
            return
        if user_input.strip() == "":
            continue

        # make a "user" content message to pass to openai chat completion API
        msg = {"role": "user", "content": user_input}
        write_message_to_history(msg)
        print("Submitting to OpenAI, please wait...", flush=True)
        messages.append(msg)
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            #max_tokens=4050 + prev_tokens,
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
            resp.usage.prompt_tokens, resp.usage.completion_tokens, cumulative_cost, model
        )
        prev_tokens = resp.usage.prompt_tokens + resp.usage.completion_tokens
        print("*******************************")


def write_message_to_history(m):
    with open("/.chatgpt_history", "a") as f:
        f.write("{}\n".format(m))


def welcome(model):
    print("Welcome to the ChatGPT command-line chatbot 🤖")
    print("  enter your questions at the prompt.")
    print("  type 'exit' or use ctrl-C to exit.")
    print()
    print("version info:")
    print("  openai chat model: ", model)
    print("  openai python library version: ", openai.version.VERSION)
    print("  python version: ", sys.version)
    print(flush=True)


def cost(prompt_tokens, completion_tokens, cumulative_cost, model):
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
    cost_per_input_token, cost_per_output_token = get_pricing(model)
    cost = prompt_tokens * cost_per_input_token
    cost += completion_tokens * cost_per_output_token
    cumulative_cost += cost
    print("  cost: ${:.6f}".format(cost))
    print("  cumulative cost: ${:.6f}".format(cumulative_cost))
    print()
    return cumulative_cost


# As of Aug 2025: https://platform.openai.com/docs/pricing
def get_pricing(model_name):
    costs = {
        "gpt-4o": {
            "input_cost": 5.00 / 1000000,
            "output_cost": 15.00 / 1000000,
        },
        "gpt-4o-mini": {
            "input_cost": 0.15 / 1000000,
            "output_cost": 0.6 / 1000000,
        },
        "gpt-4.1": {
            "input_cost": 2.0 / 1000000,
            "output_cost": 8.0 / 1000000,
        },
        "gpt-4.1-mini": {
            "input_cost": 0.40 / 1000000,
            "output_cost": 1.6 / 1000000,
        },
        "gpt-4.1-nano": {
            "input_cost": 0.1 / 1000000,
            "output_cost": 0.4 / 1000000,
        },
        "gpt-5-nano": {
            "input_cost": 0.05 / 1000000,
            "output_cost": 0.4 / 1000000,
        },
        "gpt-5-mini": {
            "input_cost": 0.25 / 1000000,
            "output_cost": 2.0 / 1000000,
        },
        "o1-mini": {
            "input_cost": 1.10 / 1000000,
            "output_cost": 4.40 / 1000000,
        },
        "o3-mini": {
            "input_cost": 1.10 / 1000000,
            "output_cost": 4.40 / 1000000,
        },
    }

    if model_name in costs:
        return costs[model_name]["input_cost"], costs[model_name]["output_cost"]
    else:
        print("Cost not available: model {model_name} not found.")
        return 0.0, 0.0


if __name__ == "__main__":
    main()
