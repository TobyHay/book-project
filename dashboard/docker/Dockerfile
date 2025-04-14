FROM python:latest 

WORKDIR /dashboard

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY welcome.py .
COPY pages .

EXPOSE 8501

CMD ["streamlit", "run", "welcome.py"]

# cd to book-project
# docker build -t book-dashboard:v2 --platform "linux/amd64" -f dashboard/docker/Dockerfile dashboard/
# docker run --platform linux/amd64 --env-file pipeline/.env -p 8501:8501 book-dashboard:v2