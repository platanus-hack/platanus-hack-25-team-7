FROM public.ecr.aws/lambda/python:3.10

COPY api_handler/requirements.txt .
RUN pip install -r requirements.txt

COPY api_handler/ .
COPY shared/ shared/

CMD ["handler.lambda_handler"]
