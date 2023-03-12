import os
import openai
import sys

# as of March 2023: https://openai.com/pricing
cost_per_token = 0.002 / 1000


def main():
    token = os.getenv("OPENAI_API_KEY")
    if token == None or not token.startswith("sk-"):
        print("ERROR: OPENAI_API_KEY must be set and must start with 'sk-...'")
        sys.exit(1)

    cumulative_cost = 0.0
    messages = []
    while True:
        try:
            user_input = input("--> ").strip()
        except KeyboardInterrupt:
            return

        if user_input == "exit":
            return

        messages.append({"role": "user", "content": user_input})
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1500,
        )
        print(resp.choices[0].message.content)
        messages.append(
            {"role": "assistant", "content": resp.choices[0].message.content}
        )
        print()
        print()
        print("Cost of that response:")
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


if __name__ == "__main__":
    main()
