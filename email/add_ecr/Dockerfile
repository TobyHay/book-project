FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

EXPOSE 5432

COPY email_sender.py "${LAMBDA_TASK_ROOT}"

COPY requirements.txt "${LAMBDA_TASK_ROOT}"

RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD [ "email_sender.lambda_handler" ]