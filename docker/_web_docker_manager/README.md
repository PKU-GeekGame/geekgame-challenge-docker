原项目为 [PKU-GeekGame/web-docker-manager](https://github.com/PKU-GeekGame/web-docker-manager)



题目 nginx 配置：

```nginx
server {
    server_name ~^probXX-(.+).geekgame.pku.edu.cn$;
    listen 80;
    listen 443 ssl http2;

    location / {
        proxy_pass http://127.0.0.1:90XX;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }
    /* other ssl stuff */
}
```

