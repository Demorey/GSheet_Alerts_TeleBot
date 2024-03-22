FROM python:3.11.8-slim-bullseye
COPY . ./tur_region_bot
WORKDIR /tur_region_bot

RUN pip install --upgrade pip
RUN pip install --user --no-warn-script-location -r requirements.txt

CMD [ "python", "main.py" ]