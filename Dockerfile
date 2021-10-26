FROM ckan/ckan:latest

USER root
RUN rm -rf /usr/lib/ckan/*
COPY ./ /usr/lib/ckan/
RUN apt update && \
    apt install uwsgi -y && \
    cd /usr/lib/ckan/ && \
    rm -rf venv && mkdir .venv && \
    pip install pipenv && \
    pipenv sync && chown -R ckan . && \
    ln -s .venv venv

RUN apt clean && rm -rf /var/lib/apt/lists/*

RUN /usr/lib/ckan/bootstrap.sh

ENTRYPOINT ["/usr/lib/ckan/ckan-entrypoint.sh"]
#USER ckan
EXPOSE 5000
CMD ${CKAN_VENV}/bin/uwsgi --ini-paste ${CKAN_CONFIG}/ckan-uwsgi.ini



