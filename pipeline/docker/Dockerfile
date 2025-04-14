FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY extract.py .
COPY transform.py .
COPY load.py .
COPY pipeline.py .

EXPOSE 5432

CMD [ "pipeline.handler" ]

# cd to book-project
# docker build -t book-pipeline:v2 --platform "linux/amd64" -f pipeline/docker/Dockerfile pipeline/
# docker run --platform linux/amd64 --env-file pipeline/.env -p 9000:8080 book-pipeline:v2