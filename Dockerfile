FROM python:3.8
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python3", "./models/price.py" ]
CMD [ "python3", "./models/order.py" ]
CMD [ "python3", "./main.py" ]
