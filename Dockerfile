FROM fedora:33
RUN dnf install -y git podman buildah python3-libselinux python3-pip
RUN pip3 install ansible==2.10.5 jmespath
RUN mkdir -p /playbooks
COPY roles/ /playbooks/roles/
COPY filter_plugins/ /playbooks/filter_plugins/
COPY upstream/ /playbooks/upstream/
COPY *.yml /playbooks/
RUN mkdir -p /etc/ansible && echo "localhost ansible_connection=local" >> /etc/ansible/hosts && mkdir -p /etc/containers/certs.d/kind-registry:5000 && ln -sfn /usr/share/pki/ca-trust-source/anchors/ca.crt /etc/containers/certs.d/kind-registry:5000/ca.crt && echo "[engine]" > /etc/containers/containers.conf && echo "cgroup_manager=\"cgroupfs\"" >> /etc/containers/containers.conf
WORKDIR /playbooks
RUN ansible-playbook upstream/local.yml --tags reset_tools,image_build -e run_upstream=true -e operator_dir=/tmp/operator-dir-dummy -e run_prepare_catalog_repo_upstream=false -e save_operator_tools_info=true
RUN dnf clean all
CMD ["/bin/bash"]
