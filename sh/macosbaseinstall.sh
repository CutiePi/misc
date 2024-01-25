echo "install curl & homebrew, before running script"
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# sometimes the C+ inclusion path is empty when it needs to point on homebrew stuff
# echo 'export CPLUS_INCLUDE_PATH=$CPLUS_INCLUDE_PATH:/opt/homebrew/include' >> ~/.zprofile

# install oh my zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# basic stuff
brew install git
#brew install n


# terminal conf & env vars (~/.zshrc or ~/.zprofile or ~/.bash_profile)
echo "alias ll='ls -la'" >> ~/.zshrc

# enables auto complete for commands (not needed built in oh-my-zsh
# echo "autoload -Uz compinit && compinit" >> ~/.zprofile
# echo 'set completion-ignore-case on' >> ~/.inputrc
# echo 'set show-all-if-ambiguous on' >> ~/.inputrc
# echo 'TAB: menu-complete' >> ~/.inputrc
