#!/bin/bash 

# manual update apt dependencies
# https://dev.mysql.com/downloads/repo/apt/
apt install curl -y
curl https://repo.mysql.com//mysql-apt-config_0.8.22-1_all.deb --output ./mysqlApt.deb
apt install ./mysqlApt.deb
apt update -y

# update apt dependencies
# use node 14 repo, default apt is v10
curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -

# install basic stuff via snap, commented optional items
#snap install code --classic
snap install slack
#snap install postman
#snap install webstorm

# install via apt & apt-get
apt-get install redis-server -y
apt-get install git-all -y
apt-get install wkhtmltopdf -y
apt install imagemagick -y
apt install mysql-server -y
apt install mysql-client -y
apt install mysql-workbench-community -y
apt install nodejs -y
apt install -y build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev

# install via npm, after nodejs
npm install --global yarn




# configs
export NODE_ENV=development
echo 'export NODE_ENV=development' >> ~/.bashrc
echo 'notify-keyspace-events "AKE"' >> /etc/redis/redis.conf

# generating your ssh key for git
ssh-keygen -t ed25519
ssh-keyscan github.com >> ~/.ssh/known_hosts
ssh-add ~/.ssh/id_ed25519


# configure stuff
# user root password root and all defaults, refresh privileges
 mysql_secure_installation
 
 
 cat ~/.ssh/id_ed25519.pub
 echo "copy paste this into your github ssh keys"
