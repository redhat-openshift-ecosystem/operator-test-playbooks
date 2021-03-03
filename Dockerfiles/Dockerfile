FROM registry.fedoraproject.org/fedora:33
RUN rpm -i https://kojipkgs.fedoraproject.org//packages/fedora-repos/33/3/src/fedora-repos-33-3.src.rpm
WORKDIR /project
ARG OPERATOR_SDK_VERSION=v1.4.0
ARG OPERATOR_TEST_PLAYBOOKS_TAG=v1.0.11
RUN mkdir /project/output
RUN export ARCH=$(case $(arch) in x86_64) echo -n amd64 ;; aarch64) echo -n arm64 ;; *) echo -n $(arch) ;; esac); \
    export OS=$(uname | awk '{print tolower($0)}'); \
    export OPERATOR_SDK_DL_URL=https://github.com/operator-framework/operator-sdk/releases/download/$OPERATOR_SDK_VERSION/; \
    curl -LO ${OPERATOR_SDK_DL_URL}/operator-sdk_${OS}_${ARCH};\
    chmod +x operator-sdk_${OS}_${ARCH};\
    mv operator-sdk_${OS}_${ARCH} operator-sdk;\
    mv operator-sdk /usr/local/bin/;
RUN dnf install -y git ansible wget python3-pip
RUN git clone --branch $OPERATOR_TEST_PLAYBOOKS_TAG https://github.com/redhat-operator-ecosystem/operator-test-playbooks.git
COPY ./entrypoint.sh /project/entrypoint.sh
RUN chmod +x /project/entrypoint.sh
ENTRYPOINT ["/project/entrypoint.sh"]
