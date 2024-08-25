FROM python:3.12
WORKDIR /app
COPY . ./
ENV PYTHONPATH=./python
EXPOSE 5000
RUN pip install python-telegram-bot==21.3
RUN pip install httpx
RUN pip install pandas
RUN pip install mplfinance
RUN pip install matplotlib
RUN pip install asyncpg
RUN pip install aenum
CMD ["python", "main.py"]