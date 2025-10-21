locals {
  cd_content = {
    "meta-data" = yamlencode({
      instance-id = "iid-local01"
    })
    "user-data" = join("\n", [
      "#cloud-config",
      yamlencode({
        ssh_authorized_keys = [
          data.sshkey.install.public_key
        ]
      })
    ])
  }
}

variable cpus {
  type    = number
  default = 2
}

variable memory {
  type    = number
  default = 2048
}

variable disk_size {
  type    = string
  default = "4500M"
}

variable img_format {
  type    = string
  default = "raw"
}

data "sshkey" "install" {
  name = "packer"
}

source "qemu" "debian-12" {
  iso_url                   = "https://cdimage.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-amd64.qcow2"
  iso_checksum              = "file:https://cdimage.debian.org/images/cloud/bookworm/latest/SHA512SUMS"
  accelerator               = "kvm"
  cpu_model                 = "host"
  boot_wait                 = "5s"
  boot_command              = ["<enter>"]
  cpus                      = var.cpus
  memory                    = var.memory
  disk_image                = true
  disk_size                 = var.disk_size
  disk_interface            = "virtio-scsi"
  disk_cache                = "unsafe"
  disk_discard              = "unmap"
  disk_detect_zeroes        = "unmap"
  disk_compression          = true
  format                    = var.img_format
  net_device                = "virtio-net"
  headless                  = true
  qemu_binary               = "qemu-system-x86_64"
  ssh_timeout               = "30s"
  ssh_username              = "debian"
  ssh_clear_authorized_keys = true
  temporary_key_pair_name   = "packer"
  qemuargs                  = [["-serial", "stdio"]]
  # It's quite unstable to use shrink so uncomment it if you need it very much
  # qemu_img_args {
  #   resize  = ["--shrink"]
  # }
  output_directory          = var.output_directory
  vm_name                   = "${source.name}.${var.img_format}"
  ssh_private_key_file      = data.sshkey.install.private_key_path
  cd_label                  = "cidata"
  cd_content                = local.cd_content
  shutdown_command        = <<EOF
set -ex

# Default network settings
cat << EOF1 | sudo tee /etc/netplan/90-genesis-net-base-config.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    alleths:
      match:
        name: en*
      dhcp4: true
EOF1

# Logs
sudo find /var/log -type f -maxdepth 3 -delete

# Remove temporary keys
# Disable removing host keys temporarily
# sudo rm -f /etc/ssh/*host*key*

# Add developer keys
sudo mkdir -p /home/debian/.ssh
[[ -f /tmp/__dev_keys ]] && sudo mv /tmp/__dev_keys /home/debian/.ssh/authorized_keys

# Tmp files
sudo rm -rf /tmp/* /var/tmp/*

# clear machine-id
sudo rm -f /etc/machine-id /var/lib/dbus/machine-id
sudo touch /etc/machine-id
sudo touch /var/lib/dbus/machine-id

# Shell history
history -c

# Cloud-init clean
sudo cloud-init clean --log --seed

# Sync FS
sudo sync

# Minify orphan space
sudo fstrim -a

# shutdown machine
sudo poweroff
EOF
}
