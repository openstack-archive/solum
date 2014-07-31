FROM ubuntu:12.04

MAINTAINER Julien Vey

RUN apt-get update

RUN apt-get -y install sudo openssh-server git

RUN locale-gen en_US.UTF-8
RUN dpkg-reconfigure locales

RUN mkdir /var/run/sshd

RUN adduser --system --group --shell /bin/sh git
RUN su git -c "mkdir /home/git/bin"

ADD admin.pub /home/git/admin.pub

RUN cd /home/git; su git -c "git clone git://github.com/sitaramc/gitolite"
RUN cd /home/git; su git -c "gitolite/install -ln"
RUN cd /home/git; su git -c "bin/gitolite setup -pk admin.pub"

ENTRYPOINT ["/usr/sbin/sshd", "-D"]

EXPOSE 22