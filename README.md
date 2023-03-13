# chatgpt

## Instructions

1. Get an OpenAI API key: https://platform.openai.com/account/api-keys
2. Build the container:
```
docker build . -t chatgpt
```
3. Run (interactive mode and env var are both required)
```
docker run --interactive --env OPENAI_API_KEY=sk-XXXXX chatgpt
```

## To keep a history of past conversations:

```
touch "$HOME/.chatgpt_history"
docker run --name chatgpt --rm --mount type=bind,source="$HOME/.chatgpt_history",target="/.chatgpt_history" --interactive --env "OPENAI_API_KEY=$OPENAI_API_KEY" chatgpt
```
