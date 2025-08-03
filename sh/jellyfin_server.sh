#!/bin/bash

# A script to configure a fresh Ubuntu install for a Jellyfin server

# --- Section 1: Install Kitty and Oh My Posh ---

echo "Starting Kitty and Oh My Posh installation..."

# ensure curl is install
sudo apt install -y curl

# Install Kitty terminal
sudo apt update
sudo apt install -y kitty

# Install Oh My Posh
curl -s https://ohmyposh.dev/install.sh | bash -s

# install font via oh-my-posh
oh-my-posh font install

# Configure Oh My Posh in your shell profile.
# This assumes you are using bash, which is the default for Ubuntu.
# This will add the oh-my-posh init command to your ~/.bashrc
echo "Configuring Oh My Posh theme in ~/.bashrc..."
# jandedobbeleer.omp.json
# stelbent-compact.minimal.omp.json
# takuya.omp.json
THEME_URL="https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/jandedobbeleer.omp.json"
curl -s "$THEME_URL" -o ~/.oh-my-posh-theme.json

# Add the init command to the end of .bashrc
echo 'eval "$(oh-my-posh init bash --config ~/.oh-my-posh-theme.json)"' >> "$HOME/.bashrc"

echo "Kitty and Oh My Posh installation complete. You may need to restart your terminal."
echo "Remember to change the font in Kitty's config to a Nerd Font (e.g., 'JetBrainsMono Nerd Font') to see the glyphs correctly."
echo "Most likely in ~/.config/kitty/kitty.conf"
echo ""

# --- Section 2: Install and configure Samba Server and Fstab ---

echo "Starting Samba server configuration and fstab setup..."

# Replace "YOUR_DRIVE_UUID" with the UUID you can get via
# sudo blkid
# This will output a list of all your system's block devices. Look for your external hard drive's partition. It will look something like this:
# /dev/sda1: LABEL="MyMediaDrive" UUID="1234-ABCD" TYPE="ext4" PARTUUID="..."
# Find the line that corresponds to your external hard drive and copy its UUID.
DRIVE_UUID="YOUR_DRIVE_UUID"
FILESYSTEM_TYPE="ntfs"
MOUNT_POINT="/mnt/externalMedia"

# Install Samba
sudo apt update
sudo apt install -y samba

# Create the directory for the share if it doesn't exist.
sudo mkdir -p "$MOUNT_POINT"

# Take ownership of the mount point so your user can manage files.
sudo chown -R $USER:$USER "$MOUNT_POINT"

# Backup the original smb.conf file
sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak

# Append a new share configuration to the smb.conf file
echo "Configuring a public share..."
sudo bash -c 'cat << EOF >> /etc/samba/smb.conf
[externalMedia]
   comment = Media Share
   path = '$MOUNT_POINT'
   browseable = yes
   read only = no
   guest ok = yes
   force user = '$USER'
EOF'

# Add an fstab entry to ensure the drive always mounts to the correct location
echo "Adding an fstab entry for persistent mounting..."
# The 'nofail' option ensures the system boots even if the drive isn't plugged in.
# 'defaults' is a good starting point for options.
sudo bash -c 'echo "UUID='$DRIVE_UUID' '$MOUNT_POINT' '$FILESYSTEM_TYPE' defaults,nofail 0 0" >> /etc/fstab'

# Restart the Samba service to apply the changes
sudo systemctl restart smbd nmbd

# Attempt to mount the drive using the new fstab entry
echo "Attempting to mount the drive..."
sudo mount -a

echo "Samba server configured and fstab entry added for the /mnt/externalMedia share."
echo "Your external drive should now automatically mount to this location on reboot."
echo ""

# 3 install jellyfin server

curl https://repo.jellyfin.org/install-debuntu.sh | sudo bash

# Enable and start the Jellyfin service
sudo systemctl enable jellyfin
sudo systemctl start jellyfin

echo "Jellyfin server installed and started."
echo "You can now access the Jellyfin web interface by navigating to http://<your-ubuntu-ip-address>:8096 in your web browser."
echo "Follow the on-screen prompts to complete the initial setup."
echo ""

# --- Section 4: Configure OS to never sleep ---

echo "Configuring OS to prevent sleep..."

# Set the power-button action to "interactive" so you're asked what to do
gsettings set org.gnome.settings-daemon.plugins.power power-button-action 'interactive'

# Disable automatic suspend when the laptop lid is closed
# This is a common issue for headless servers
gsettings set org.gnome.desktop.peripherals.keyboard suspend-when-lid-is-closed false

# Disable the screensaver
gsettings set org.gnome.desktop.screensaver idle-activation-enabled false

# Disable suspend on idle
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type 'nothing'

echo "Power management settings configured to prevent sleep when plugged in."
echo ""
