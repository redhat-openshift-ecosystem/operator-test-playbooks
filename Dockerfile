FROM centos:8
RUN yum install epel-release -y
RUN yum update -y
RUN yum install -y ansible git
RUN mkdir /playbooks
COPY roles/ /etc/ansible/roles/
COPY *.yml /playbooks/
RUN ln -s /etc/ansible/roles /playbooks/roles
RUN echo "localhost ansible_connection=local" >> /etc/ansible/hosts
WORKDIR /playbooks
RUN ansible-playbook local.yml --tags image_build -e "operator_dir=/tmp/operator-dir-dummy"
CMD ["/bin/bash"]