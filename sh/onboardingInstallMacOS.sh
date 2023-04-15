#!/bin/bash 

# install homebrew only part that needs sudo
# sudo /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install mysql
brew install mysql-client
brew install --cask mysqlworkbench

# uncomment to install basic stuff like slack and postman
#brew install slack
#brew install postman

# install via brew
brew install redis
brew install git
brew install --cask wkhtmltopdf
#brew install imagemagick
brew install graphicsmagick
# Dependencies for node-canvas
brew install pkg-config cairo pango libpng jpeg giflib librsvg python

# install n node version manager
brew install n
# use n to install proper version of node
n 18.14
# install via npm, after nodejs
npm install --global yarn



# config & QOL
echo 'export NODE_ENV=development' >> ~/.zprofile
echo "alias ll='ls -la'" >> ~/.zprofile
# enables auto complete for commands
echo "autoload -Uz compinit && compinit" >> ~/.zprofile
echo 'set completion-ignore-case on' >> ~/.inputrc
echo 'set show-all-if-ambiguous on' >> ~/.inputrc
echo 'TAB: menu-complete' >> ~/.inputrc
# sometimes the C+ inclusion path is empty when it needs to point on homebrew stuff
echo 'export CPLUS_INCLUDE_PATH=$CPLUS_INCLUDE_PATH:/opt/homebrew/include' >> ~/.zprofile
echo 'alias graphicsmagick=gm' >> ~/.zprofile
# redis conf
echo 'notify-keyspace-events "AKE"' >> /opt/homebrew/etc/redis.conf





# configure stuff
# user root password root and all defaults, refresh privileges
brew services start redis
brew services start mysql
mysql_secure_installation