FROM public.ecr.aws/lambda/python:3.10

COPY splitter_handler/requirements.txt .
RUN pip install -r requirements.txt

COPY splitter_handler/ .
COPY shared/ shared/

CMD ["handler.lambda_handler"]
