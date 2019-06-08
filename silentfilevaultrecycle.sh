#!/bin/bash

# Silent Recycle FileVault Key

# github.com/3jdp

# In cases where you have a known (admin) user/pass, this can recycle the filevault key for Jamf capture
# Jamf capture. Note that while this doesn't echo the new FileVault key into the Jamf logs, it does require
# putting an admin password either into Jamf Pro as a policy argument or in the script itself. 

# Based on documentation by Rich Trouton: 
# https://derflounder.wordpress.com/2015/12/20/managing-el-capitans-filevault-2-with-fdesetup/#more-7577

# $1- $3 are reserved by Jamf
# $4 is the known username
# $5 is the known password

ADMINUSER=$4
ADMINPWD=$5

if [[ -z $(dscl . -list /Users | grep $ADMINUSER) ]]; then
    echo "This admin user is not found on this system"
    exit 1
fi

echo "<?xml version="1.0" encoding="UTF-8"?>" \
"<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">" \
"<plist version="1.0">" \
"<dict>" \
"<key>Username</key>" \
"<string>"$ADMINUSER"</string>" \
"<key>Password</key>" \
"<string>"$ADMINPWD"</string>" \
"</dict>" \
"</plist>" > /tmp/fv.plist

fdesetup changerecovery -personal -inputplist < /tmp/fv.plist > /dev/null 2>&1

echo "Completed FileVault recycle"
exit 0