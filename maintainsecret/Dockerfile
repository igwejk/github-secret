FROM --platform=linux/amd64 python:3.11-alpine

COPY * /maintainsecret/

RUN python -m pip install --no-cache-dir --upgrade -r /maintainsecret/requirements.txt

ENTRYPOINT ["/maintainsecret/entrypoint.sh"]
