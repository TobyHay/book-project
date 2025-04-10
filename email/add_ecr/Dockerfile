FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY test_ecr.py .

EXPOSE 5432

CMD [ "test_ecr.handler" ]