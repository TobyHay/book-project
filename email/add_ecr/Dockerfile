FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

EXPOSE 5432

COPY email_sender.py .

COPY requirements.txt .

RUN pip3 install -r requirements.txt --target .

CMD [ "email_sender.lambda_handler" ]