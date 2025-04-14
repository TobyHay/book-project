FROM python:latest 

WORKDIR /dashboard

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY welcome.py .
COPY pages .

EXPOSE 8501

CMD ["streamlit", "run", "welcome.py"]


# Create Docker Image
# cd to book-project
# docker build -t book-dashboard:v3 --platform "linux/amd64" -f docker/Dockerfile .

# Testing Image Locally
# docker run --platform linux/amd64 --env-file .env -p 8501:8501 book-dashboard:v2