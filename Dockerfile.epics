FROM debian:jessie

MAINTAINER NSLS-II <https://nsls-ii.github.io>

USER root

RUN apt-get update
RUN apt-get install -yq wget 
RUN wget --quiet http://epics.nsls2.bnl.gov/debian/repo-key.pub -O - | apt-key add -
RUN echo "deb http://epics.nsls2.bnl.gov/debian/ jessie/staging main contrib" | tee /etc/apt/sources.list.d/nsls2.list
#RUN echo "deb http://ftp.us.debian.org/debian/ jessie non-free" | tee /etc/apt/sources.list.d/non-free.list
RUN apt-get update
RUN apt-get install -yq build-essential git epics-dev epics-synapps-dev epics-iocstats-dev 
RUN apt-get install -yq procserv telnet sysv-rc-softioc 
# get areadetector dependencies
RUN apt-get install -yq libhdf5-dev libx11-dev libxext-dev libxml2-dev libpng12-dev libbz2-dev libfreetype6-dev 

RUN mkdir /epics && mkdir /epics/iocs
RUN git clone --single-branch -b docker https://github.com/dchabot/motorsim.git /epics/iocs/motorsim
RUN cd /epics/iocs/motorsim && make -s all
#RUN manage-iocs install motorsim
#RUN manage-iocs enable motorsim
 
RUN mkdir /epics/src
RUN git clone https://github.com/dchabot/areadetector-1-9-1.git /epics/src/areadetector-1-9-1
RUN cd /epics/src/areadetector-1-9-1 && make -s -j4 all

RUN git clone --single-branch -b docker https://github.com/dchabot/adsim.git /epics/iocs/adsim
#RUN manage-iocs install adsim
#RUN manage-iocs enable adsim

# flash the neighbours
EXPOSE 5064 5065

#CMD procServ -q --name=motorsim -i ^C^D^] -c /epics/iocs/motorsim 2048 ./st.cmd && \
#    procServ -q -f --name=adsim -i ^C^D^] -c /epics/iocs/adsim 2049 ./st.cmd && bash

#RUN update-iocs-cf
#CMD ["bash", "manage-iocs", "startall"]

RUN apt-get install -yq supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]
#CMD service softioc-motorsim start && bash
