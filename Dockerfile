FROM public.ecr.aws/docker/library/python:3-alpine

RUN pip install --no-cache-dir openai

COPY main.py /

ENTRYPOINT ["python", "/main.py"]
