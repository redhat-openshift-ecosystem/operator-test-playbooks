FROM centos:8
RUN yum install epel-release -y
RUN yum update -y
RUN yum install -y ansible git podman
RUN mkdir /playbooks
COPY roles/ /playbooks/roles/
COPY filter_plugins/ /playbooks/filter_plugins/
COPY test/ /playbooks/test/
COPY *.yml /playbooks/
RUN echo "localhost ansible_connection=local" >> /etc/ansible/hosts
WORKDIR /playbooks
RUN ansible-playbook local.yml --tags image_build -e run_upstream=true -e operator_dir=/tmp/operator-dir-dummy
CMD ["/bin/bash"]