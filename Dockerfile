FROM python:3.11.9-alpine
COPY . ./tur_region_bot
WORKDIR /tur_region_bot

RUN pip install --upgrade pip && pip install --user --no-warn-script-location --no-cache-dir -r requirements.txt

CMD [ "python", "main.py" ]