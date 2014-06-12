FROM ubuntu:13.04

MAINTAINER Pierre Padrixe

ADD ./elements/jenkins/install.d/02-install-jenkins /tmp/install-jenkins.sh

RUN /tmp/install-jenkins.sh

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/usr/share/jenkins/jenkins.war"]
