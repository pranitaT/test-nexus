FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app.py backend/app.py
COPY frontend frontend
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
EXPOSE 5000
CMD ["gunicorn","--bind","0.0.0.0:5000","--workers","2","--threads","4","--chdir","backend","app:app"]
