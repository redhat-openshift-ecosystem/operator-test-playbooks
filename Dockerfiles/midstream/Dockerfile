FROM registry.fedoraproject.org/fedora:33
ARG OPERATOR_SDK_VERSION=v1.4.0
ARG UMOCI_VERSION=v0.4.5
ENV ANSIBLE_CONFIG=/project/operator-test-playbooks/Dockerfiles/midstream/
ENV ANSIBLE_LOCAL_TEMP=/tmp/
ENV PATH="/operator-test-playbooks/Dockerfiles/midstream/:${PATH}"
ADD extract-operator-bundle.yml validate-operator-bundle.yml /project/operator-test-playbooks/
RUN export ARCH=$(case $(arch) in x86_64) echo -n amd64 ;; aarch64) echo -n arm64 ;; *) echo -n $(arch) ;; esac);\
    export OS=$(uname | awk '{print tolower($0)}');\
    export OPERATOR_SDK_DL_URL=https://github.com/operator-framework/operator-sdk/releases/download/$OPERATOR_SDK_VERSION/;\
    curl -L -o /usr/local/bin/operator-sdk ${OPERATOR_SDK_DL_URL}/operator-sdk_${OS}_${ARCH} && \
    chmod a+x /usr/local/bin/operator-sdk && \
    curl -fL -o /usr/local/bin/umoci https://github.com/opencontainers/umoci/releases/download/${UMOCI_VERSION}/umoci.amd64 && \
    chmod a+x /usr/local/bin/umoci && \
    chmod g+w /etc/passwd && \
    chmod -R 777 /project/ && \
    dnf install --setopt=install_weak_deps=False -y git-core ansible skopeo && \
    dnf clean all
ADD ./Dockerfiles/midstream/fix_etc_passwd_k8s.sh ./Dockerfiles/midstream/run_tests.py ./Dockerfiles/midstream/unit_tests.py ./Dockerfiles/midstream/fix_etc_passwd.sh /usr/bin/
ADD roles /project/operator-test-playbooks/roles/
ADD extract-operator-bundle.yml validate-operator-bundle.yml /project/operator-test-playbooks/
ADD ./Dockerfiles/midstream/ansible.cfg /project/operator-test-playbooks/
WORKDIR /project/
ENTRYPOINT ["/usr/bin/fix_etc_passwd.sh"]
