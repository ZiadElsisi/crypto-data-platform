# pull the base image
FROM apache/airflow:3.3.2-python3.14
## copy the requirements file to the image so it loads the needed dependencies
COPY airflow/requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt