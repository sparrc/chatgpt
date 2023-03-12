# chatgpt

## Instructions

1. Get an OpenAI API key: https://platform.openai.com/account/api-keys
2. Build the container:
```
docker build . -t chatgpt
```
3. Run (interactive mode and env var are both required)
```
docker run -i --env OPENAI_API_KEY=sk-XXXXX chatgpt
```
