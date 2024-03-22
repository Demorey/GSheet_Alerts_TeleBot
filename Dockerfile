FROM python:3.11.6-slim-bullseye
COPY . ./tur_region_bot
WORKDIR /tur_region_bot
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --user -r requirements.txt

CMD [ "python", "main.py" ]