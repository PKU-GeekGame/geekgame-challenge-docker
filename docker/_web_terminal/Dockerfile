FROM node:22-bookworm
RUN apt update && apt -y upgrade && \
    apt install -y netcat-traditional && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /srv
COPY package.json package.json ./
RUN npm i --registry=https://registry.npmmirror.com
COPY app.ts ./
RUN ./node_modules/.bin/tsc app.ts
CMD ["node", "app.js"]
