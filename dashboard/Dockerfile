FROM python:latest 

run mkdir ./dashboard 
WORKDIR /dashboard

COPY requirements.txt .
RUN pip install -r requirements.txt

run mkdir ./pages
COPY welcome.py .
COPY pages/1_Statistics.py ./pages

EXPOSE 8501

CMD python -m streamlit run welcome.py