FROM python:3.7-alpine
WORKDIR /tflapp
COPY . /tflapp 
RUN pip install -U -r requirements.txt
EXPOSE 8080
CMD ["python", "tflapp.py"]
