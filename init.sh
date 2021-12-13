#!/bin/bash
echo I am the user `whoami` && sudo apt-get update  && sudo apt-get -y install nginx mariadb-client && sudo systemctl enable nginx && sudo systemctl start nginx

cat <<EOF > mysqluptimeservice.sh
#!/bin/bash
while true
do 
  sleep 1
  htdocsdir=/var/www/html 
  export MYSQL_PWD=pleasedontusethishorriblepassword
  dbURI=idmetsadb.gcp.ynos.us
  export mysqluptime=\$(mysql -udontusethisuser -h\${dbURI} --skip-column-names -B -e 'SHOW GLOBAL STATUS LIKE "Uptime"')
  cat <<_EOF> \${htdocsdir}/index.html 
<html>
 <head>
   <title>Hello world</title>
   <meta http-equiv="refresh" content="3">
  </head>
 <body>
   <center><h1>hello word</h1></center> <br>
   Mysql \${mysqluptime:-NUL}
 </body>
</html>
_EOF
done
EOF

sudo chmod 700 mysqluptimeservice.sh
sudo mv mysqluptimeservice.sh /bin/mysqluptimeservice.sh

cat <<_EOF >  mysqluptimeservice.service
[Unit]
Description=simple systemd service.
[Service]
Type=simple
ExecStart=/bin/bash /bin/mysqluptimeservice.sh
[Install]
WantedBy=multi-user.target
_EOF
sudo mv mysqluptimeservice.service /etc/systemd/system/mysqluptimeservice.service
sudo systemctl enable mysqluptimeservice
sudo systemctl start mysqluptimeservice

