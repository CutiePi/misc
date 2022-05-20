#!/bin/bash 

# manual update apt dependencies
# https://dev.mysql.com/downloads/repo/apt/
curl https://repo.mysql.com//mysql-apt-config_0.8.22-1_all.deb --output ./mysqlApt.deb
apt install ./mysqlApt.deb
apt update

# update apt dependencies
# use node 16 repo, default apt is v10
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -

# install basic stuff via snap, commented optional items
#snap install code --classic
snap install slack
#snap install postman
#snap install webstorm

# install via apt & apt-get
apt-get install redis-server
apt-get install git-all
apt-get install wkhtmltopdf
apt install imagemagick
apt install mysql-server
apt install mysql-client
apt install mysql-workbench-community
apt install nodejs

# install via npm, after nodejs
npm install --global yarn




# configs
echo 'export NODE_ENV=development' >> ~/.bashrc
echo 'notify-keyspace-events "AKE"' >> /etc/redis/redis.conf


# configure stuff
 mysql_secure_installation