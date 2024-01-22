#!/bin/bash
# generating your ssh key for git, adding to ssh agent
ssh-keygen -t ed25519 -q -N ""
ssh-keyscan github.com >> ~/.ssh/known_hosts
ssh-add ~/.ssh/id_ed25519
echo "copy paste this into your github ssh keys"
cat ~/.ssh/id_ed25519.pub

# ADD gpg signature for commits
# Note: SSH signature verification is available in Git 2.34 or later.
git config --global commit.gpgsign true
git config --global gpg.format ssh
git config --global user.signingkey /Users/jasmin/.ssh/id_ed25519.pub
