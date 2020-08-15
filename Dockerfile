# pull official base image
FROM python:3

MAINTAINER "Ganawa Juanah <ganawa@juanah.com>"
LABEL version="1.0"
LABEL description="FLASK CoredDNS Listener"

RUN set -eux; \
	apt-get update; \
	apt-get install -y gosu; \
	rm -rf /var/lib/apt/lists/*; \
	gosu nobody true

ARG PUID=1000
ARG PGID=1000
ENV USER=listener
ENV GROUP=listener
ENV HOME=/home/$USER
ENV FLASK_HOME=/home/$USER/app

# setup flask variables
ENV FLASK_ENV=production

# create the listener user
RUN addgroup --system --gid $PGID $USER
RUN adduser --system --uid $PUID --ingroup $GROUP --home $HOME  $USER

# copy project
COPY ./app $FLASK_HOME

# change directory
WORKDIR $FLASK_HOME

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# chown all the files to the app user
RUN chown -R listener:listener $FLASK_HOME

# volume for coredns
RUN mkdir /etc/coredns
RUN chown -R listener:listener /etc/coredns
#VOLUME /etc/coredns

# volume for temporary directory
RUN mkdir /tmp/repos
RUN chown -R listener:listener /tmp/repos
#VOLUME /tmp/repos

HEALTHCHECK CMD curl --fail http://localhost:5000/ || exit 1

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]