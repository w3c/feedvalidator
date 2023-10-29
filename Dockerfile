FROM debian:12

RUN apt-get update
RUN apt-get --yes install apache2
RUN apt-get --yes install python3 python3-libxml2 python3-rdflib python3-rdflib-jsonld
RUN apt-get --yes install ca-certificates

RUN a2dissite 000-default

RUN a2enmod cgid
RUN a2enmod rewrite
RUN echo 'ServerName feedvalidator.org' >>/etc/apache2/apache2.conf

WORKDIR /feedvalidator

ADD . /feedvalidator
ADD sites-available-feedvalidator.conf /etc/apache2/sites-available/feedvalidator.conf

RUN a2ensite feedvalidator

EXPOSE 80

ENV HTTP_HOST https://feedvalidator.org/
ENV SCRIPT_NAME check.cgi
ENV SCRIPT_FILENAME /feedvalidator/check.cgi

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
