FROM python:3.7
ADD . /src
RUN pip install kopf
CMD kopf run global-image-puller --verbose