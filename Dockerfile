FROM ubuntu:14.04
MAINTAINER Ngure Nyaga <ngure.nyaga@savannahinformatics.com>
ENV DEBIAN_FRONTEND noninteractive

# Set up software repositories and install language pack
# This is occurring early because of that locale fuck-up below
RUN apt-get update && \
    apt-get dist-upgrade -yqq &&  \
    apt-get install locales language-pack-en-base -yqq

# Locale stuff when running on CircleCI is fucked up
# Our database needs to run with UTF-8 ( C / POSIX locale -> trouble )
RUN touch /etc/default/locale
RUN locale-gen --no-purge en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8
ENV LC_MONETARY en_US.UTF-8
ENV LC_TIME en_US.UTF-8
ENV LC_NUMERIC en_US.UTF-8
RUN echo "LANG="en_US.UTF-8"" >> /etc/default/locale && \
    echo "LC_NUMERIC="en_US.UTF-8"" >> /etc/default/locale && \
    echo "LC_TIME="en_US.UTF-8"" >> /etc/default/locale && \
    echo "LC_MONETARY="en_US.UTF-8"" >> /etc/default/locale && \
    echo "LC_PAPER="en_US.UTF-8"" >> /etc/default/locale && \
    echo "LC_NAME="en_US.UTF-8"" >> /etc/default/locale && \
    echo "LC_ADDRESS="en_US.UTF-8"" >> /etc/default/locale && \
    echo "LC_TELEPHONE="en_US.UTF-8"" >> /etc/default/locale && \
    echo "LC_MEASUREMENT="en_US.UTF-8"" >> /etc/default/locale && \
    echo "LC_IDENTIFICATION="en_US.UTF-8"" >> /etc/default/locale && \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN dpkg-reconfigure locales

# Install the necessary services / dependencies
RUN apt-get install wget -yqq && \
    wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add - && \
    echo 'deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main' >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install language-pack-en postgresql postgresql-plpython-9.3 redis-server elasticsearch python-virtualenv virtualenvwrapper python-pip openjdk-7-jdk postgresql-server-dev-9.3 python-dev build-essential --no-install-recommends -yqq

# Set up PostgreSQL
USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER termserver WITH SUPERUSER PASSWORD 'termserver';" && \
    createdb -O termserver termserver

# Add the current directory contents to /opt/slade360-terminology-server/
USER root
ADD . /opt/slade360-terminology-server/
WORKDIR /opt/slade360-terminology-server/

# Run the SNOMED build
RUN cp -v /opt/slade360-terminology-server/config/postgresql/postgresql.conf  /etc/postgresql/9.3/main/postgresql.conf && \
    cp -v /opt/slade360-terminology-server/config/postgresql/pg_hba.conf  /etc/postgresql/9.3/main/pg_hba.conf && \
    pip install -r /opt/slade360-terminology-server/requirements.txt && \
    /etc/init.d/postgresql start && \
    fab --fabfile=/opt/slade360-terminology-server/fabfile.py build

# Expose the ports that outside world will interact with
# Only the application port at 81; everything else is hidden
# This port 81 will be proxied by an Nginx
USER root
EXPOSE 81

# Add VOLUMEs to allow backup of config, logs and databases
# TODO More volumes, to back up redis and app stuff
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

# Set the default command to run when starting the container
# TODO This will change; to a runit that starts PostgreSQL, Redis, Nginx, the app
CMD ["/usr/lib/postgresql/9.3/bin/postgres", "-D", "/var/lib/postgresql/9.3/main", "-c", "config_file=/etc/postgresql/9.3/main/postgresql.conf"]
