FROM python:3.12
LABEL authors="grtsinry43"
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "main.py"]
