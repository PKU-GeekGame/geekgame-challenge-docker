需要首先 build 前端目录：https://github.com/PKU-GeekGame/web-terminal-frontend

前端目录的 nginx 配置：

```nginx
server {
	server_name web-terminal.geekgame.pku.edu.cn;
    listen 80;
	listen 443 ssl http2;

	root /opt/web-terminal-frontend/build;

	location / {
		add_header Cache-Control "public";
		add_header Access-Control-Allow-Origin "*";
		expires 1h;
	}
	/* other ssl stuff */
}
```



题目 nginx 配置：

```nginx
server {
    server_name probXX.geekgame.pku.edu.cn;
    listen 80;
    listen 443 ssl http2;

    location / {
        root /opt/web-terminal-frontend/build;
    }
    location /shell {
        proxy_pass http://127.0.0.1:90XX;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;  
        proxy_set_header Connection "Upgrade";  
    }
    /* other ssl stuff */
}
```

