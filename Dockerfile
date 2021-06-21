FROM registry.access.redhat.com/ubi8/python-38
COPY requirements.txt ./
COPY global-image-puller.py ./
RUN pip install -r requirements.txt
CMD ./global-image-puller.py