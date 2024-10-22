FROM debian:12
RUN apt update && apt -y upgrade && \
    apt install -y xinetd python3-openssl docker.io python3-pip && \
    rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages requests httpx
COPY main.py /
COPY cert.pem /
COPY flaglib.py /
COPY db.py /
COPY redirect.html /
COPY socat /
RUN chmod +x /socat
COPY socat_static /
RUN chmod +x /socat_static
CMD ["python3", "main.py"]
