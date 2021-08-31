FROM ckan/ckan:latest

USER root
ADD wsgi.py /etc/ckan/wsgi.py
ADD ckan-uwsgi.ini /etc/ckan/ckan-uwsgi.ini
RUN rm -rf /usr/lib/ckan/*
COPY ./ /usr/lib/ckan/
RUN apt update && \
    apt install uwsgi -y && \
    cd /usr/lib/ckan/ && \
    rm -rf venv && mkdir .venv && \
    pip install pipenv \
    pipenv sync && chown -R ckan . 

RUN apt clean && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/ckan-entrypoint.sh"]
#USER ckan
EXPOSE 5000
CMD ${CKAN_VENV}/bin/uwsgi --ini-paste ${CKAN_CONFIG}/ckan-uwsgi.ini



