FROM centos:8
RUN yum install epel-release -y
RUN yum update -y
RUN dnf -y module disable container-tools
RUN dnf -y install 'dnf-command(copr)'
RUN dnf -y copr enable rhcontainerbot/container-selinux
RUN curl -L -o /etc/yum.repos.d/devel:kubic:libcontainers:stable.repo https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/CentOS_8/devel:kubic:libcontainers:stable.repo
RUN dnf install -y ansible git podman buildah python3-libselinux
RUN mkdir -p /playbooks
COPY roles/ /playbooks/roles/
COPY filter_plugins/ /playbooks/filter_plugins/
#COPY test/ /playbooks/test/
COPY upstream/ /playbooks/upstream/
COPY *.yml /playbooks/
#COPY ansible.cfg /playbooks/
RUN echo "localhost ansible_connection=local" >> /etc/ansible/hosts
RUN mkdir -p /etc/containers/certs.d/kind-registry:5000
RUN ln -sfn /usr/share/pki/ca-trust-source/anchors/ca.crt /etc/containers/certs.d/kind-registry:5000/ca.crt
WORKDIR /playbooks
RUN ansible-playbook upstream/local.yml --tags reset_tools,image_build -e run_upstream=true -e operator_dir=/tmp/operator-dir-dummy -e run_prepare_catalog_repo_upstream=false
CMD ["/bin/bash"]
