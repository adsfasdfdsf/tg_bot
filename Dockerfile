FROM python:3.12
WORKDIR /app
COPY . ./
ENV PYTHONPATH=./python
EXPOSE 5000
RUN pip install requirements.txt
CMD ["python", "main.py"]