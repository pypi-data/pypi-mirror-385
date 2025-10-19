FROM python:3.12-slim

COPY . /app

WORKDIR /app

RUN pip install .

CMD ["python3", "/usr/local/lib/python3.12/site-packages/square_file_store/main.py"]

# Uncomment for debugging
# CMD ["bash", "-c", "while true; do sleep 60; done"]
