#!/bin/bash

disk="sdb"

if [ "`lsblk | grep $disk`" ]; then
    if [ "`cat /proc/mounts | grep $disk`" == "" ]; then
        echo "Mount disk $disk"
        
        (
        echo o # Create a new empty DOS partition table
        echo n # Add a new partition
        echo p # Primary partition
        echo 1 # Partition number
        echo   # First sector (Accept default: 1)
        echo   # Last sector (Accept default: varies)
        echo w # Write changes
        ) | sudo fdisk /dev/${disk}

        sudo mkfs.ext4 -F /dev/${disk}1
        sudo mkdir -p /mnt/store
        sudo mount /dev/${disk}1 /mnt/store
    else:
        echo "Disk $disk already mounted"
    fi
fi

