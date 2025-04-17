FROM python:latest 

run mkdir ./dashboard 
WORKDIR /dashboard

COPY requirements.txt .
RUN pip install -r requirements.txt

run mkdir ./pages
COPY Welcome.py .
COPY pages/1_Statistics.py ./pages
COPY pages/2_Compare_Authors.py ./pages
COPY pages/3_Add_Authors.py ./pages
COPY pages/4_Sign_Up_For_Emails.py ./pages

EXPOSE 8501

CMD python -m streamlit run Welcome.py