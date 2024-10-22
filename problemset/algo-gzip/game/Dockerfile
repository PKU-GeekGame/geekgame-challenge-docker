FROM debian:12

RUN apt update && apt install -y python3 python3-pip

COPY logger.py /root
COPY variant.py /root
COPY server.py /root

WORKDIR /root
CMD ["/usr/bin/python3", "-u", "/root/server.py"]
