FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY ***.py .

EXPOSE 5432

CMD [ "***.handler" ]