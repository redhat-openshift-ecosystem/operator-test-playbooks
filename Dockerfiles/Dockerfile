from fedora:32

WORKDIR /project

RUN dnf update -y;
RUN mkdir /project/output
RUN export ARCH=$(case $(arch) in x86_64) echo -n amd64 ;; aarch64) echo -n arm64 ;; *) echo -n $(arch) ;; esac); \
    export OS=$(uname | awk '{print tolower($0)}'); \
    export OPERATOR_SDK_DL_URL=https://github.com/operator-framework/operator-sdk/releases/download/v1.4.0/; \
    curl -LO ${OPERATOR_SDK_DL_URL}/operator-sdk_${OS}_${ARCH};\
    chmod +x operator-sdk_${OS}_${ARCH};\
    mv operator-sdk_${OS}_${ARCH} operator-sdk;\
    mv operator-sdk /usr/local/bin/;
RUN dnf install -y git ansible wget python3-pip
RUN git clone --branch v1.0.11 https://github.com/redhat-operator-ecosystem/operator-test-playbooks.git
COPY ./entrypoint.sh /project/entrypoint.sh
RUN chmod +x /project/entrypoint.sh
ENTRYPOINT ["/project/entrypoint.sh"]
