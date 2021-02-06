# frozen_string_literal: true

# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
  config.vm.box = 'arfreitas/centos7-vbguest'
  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  config.vm.network 'forwarded_port', guest: 8080, host: 8080, id: 'jenkins'

  config.vm.provider 'virtualbox' do |vb|
    # Display the VirtualBox GUI when booting the machine
    # vb.gui = true
    vb.memory = '2048'
    vb.cpus = '2'
  end

  config.vm.provision 'shell', inline: <<-SHELL
    set -e
    yum makecache fast
    yum upgrade -y
    yum group install 'Development Tools' -y
    yum install -y git python3-pip python3-jenkins java-11-openjdk bzip2-devel libsqlite3x-devel glibc-common tk-devel python36-xmltodict libffi-devel
    wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
    rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io.key
    yum makecache fast
    yum install jenkins -y
    systemctl enable jenkins
    systemctl start jenkins
    cat /var/lib/jenkins/secrets/initialAdminPassword
  SHELL
end
