# 220724, Tuesday, 04.00 pm 
# Steps (multistage buils)
# 1. Build Dependecy Wheels 
# 2. RUN Application 


ARG PYTHON_VERSION=3.10-bullseye



FROM python:${PYTHON_VERSION} AS python 


# 1. Python Dependency Wheels | Build Stage 1 
FROM python AS python-build-stage
ARG BUILD_ENVIRONMENT=production

RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential \
        libpq-dev 

COPY ./requirements . 


RUN pip wheel --wheel-dir /usr/src/app/wheel \
        -r ${BUILD_ENVIRONMENT}.txt 



# Run the Application | Build Stage 2

# image 
FROM python AS python-run-stage 

# creating an user for the backend. (algocode is the user and group)
RUN addgroup --system cutetube && adduser --system --ingroup cutetube cutetube 

# args
ARG BUILD_ENVIRONMENT=production

# user dir 
ARG APP_HOME=/home/cutetube/app 

# envs 
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1 
ENV BUILD_ENV=${BUILD_ENVIRONMENT}


WORKDIR ${APP_HOME}



#  ${APP_HOME}/vod-media-files is the External volume mount point. See docker compose file for the mount point. 
RUN mkdir -p ${APP_HOME}/staticfiles ${APP_HOME}/mediafiles ${APP_HOME}/vod-media-files && \
        chown -R cutetube:cutetube ${APP_HOME}/staticfiles ${APP_HOME}/mediafiles ${APP_HOME}/vod-media-files && \
        chmod -R 775 ${APP_HOME}/staticfiles ${APP_HOME}/mediafiles ${APP_HOME}/vod-media-files





RUN apt-get update && apt-get install --no-install-recommends -y \
        libpq-dev \
        gettext netcat \
        ffmpeg \
        && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
        && rm -rf /var/lib/apt/lists/*


COPY --from=python-build-stage /usr/src/app/wheel /wheels/

RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
        && rm -rf /wheels/ 



# copy entrypoint as user 
COPY --chown=cutetube:cutetube ./docker/production/django/entrypoint.sh /entrypoint.sh

# unix based system 
RUN sed -i 's/\r$//g' /entrypoint.sh

# execution permission (+x) with chmod to /entrypoiny dir  
# checks the postgres db availability 
RUN chmod +x /entrypoint.sh


COPY --chown=cutetube:cutetube ./docker/production/django/start /start

RUN sed -i 's/\r$//g' /start 


RUN chmod +x /start 


COPY --chown=cutetube:cutetube ./docker/production/django/celery/worker/start /start-celeryworker

RUN sed -i 's/\r$//g' /start-celeryworker

RUN chmod +x /start-celeryworker


COPY --chown=cutetube:cutetube ./docker/production/django/celery/flower/start /start-flower

RUN sed -i 's/\r$//g' /start-flower

RUN chmod +x /start-flower


COPY --chown=cutetube:cutetube . ${APP_HOME} 

# ownership of APP_HOME
RUN chown cutetube:cutetube ${APP_HOME} 

USER cutetube

ENTRYPOINT ["/entrypoint.sh"]