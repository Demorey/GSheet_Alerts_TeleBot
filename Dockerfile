FROM python:3.10-bullseye
COPY . ./tur_region_bot
WORKDIR /tur_region_bot

RUN pip install --upgrade pip
RUN pip install --user -r requirements.txt

CMD [ "python", "main.py" ]