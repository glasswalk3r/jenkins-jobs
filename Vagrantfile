# frozen_string_literal: true

# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
  config.vm.box = 'bento/rockylinux-8'
  config.vm.box_version = '202510.26.0'
  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  config.vm.network 'forwarded_port', guest: 8080, host: 8080, id: 'jenkins'

  config.vbguest.auto_update = false
  config.vm.synced_folder '.', '/vagrant', disabled: true

  config.vm.provider 'virtualbox' do |vb|
    # Display the VirtualBox GUI when booting the machine
    # vb.gui = true
    vb.memory = '2048'
    vb.cpus = '2'
    vb.name = 'jenkins-sample'
    vb.customize ['modifyvm', :id, '--vram', '16']
  end

  config.vm.provision 'shell', inline: <<~SHELL
    set -e
    dnf makecache
    dnf upgrade -y
    dnf group install 'Development Tools' -y
    dnf install -y git python3-pip java-21-openjdk-headless bzip2-devel glibc-common tk-devel libffi-devel dnf-plugins-core
    dnf remove java-1.8.0-openjdk-headless -y
    TARGET_JAVA_PATH=$(alternatives --display java | grep "family java-21-openjdk" | head -n1 | cut -d' ' -f1)
    echo "Setting Java binary to $TARGET_JAVA_PATH"
    alternatives --set java "$TARGET_JAVA_PATH"
    dnf config-manager --add-repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
    rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io.key
    dnf install epel-release -y
    dnf makecache
    dnf install python3-xmltodict python3-jenkins jenkins -y
    systemctl enable jenkins
    systemctl start jenkins
    pwd_file=/var/lib/jenkins/secrets/initialAdminPassword

    while test 1
    do
          if ![ -f "${pwd_file}" ]
          then
              sleep 5
          else
              echo 'Initial admin password for Jenkins:'
              cat "${pwd_file}"
              break
          fi
    done
  SHELL
end
