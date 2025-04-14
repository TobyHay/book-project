FROM python:latest 

WORKDIR /dashboard

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY welcome.py .
COPY pages .

EXPOSE 8501

CMD ["streamlit", "run", "welcome.py"]