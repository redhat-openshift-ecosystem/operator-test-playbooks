FROM registry.fedoraproject.org/fedora:33
WORKDIR /project
ARG OPERATOR_SDK_VERSION=v1.13.1
RUN export ARCH=$(case $(arch) in x86_64) echo -n amd64 ;; aarch64) echo -n arm64 ;; *) echo -n $(arch) ;; esac);\
    export OS=$(uname | awk '{print tolower($0)}');\
    export OPERATOR_SDK_DL_URL=https://github.com/operator-framework/operator-sdk/releases/download/$OPERATOR_SDK_VERSION/;\
    curl -L -o /usr/local/bin/operator-sdk ${OPERATOR_SDK_DL_URL}/operator-sdk_${OS}_${ARCH} && \
    chmod a+x /usr/local/bin/operator-sdk && \
    curl -fL -o /usr/local/bin/yq https://github.com/mikefarah/yq/releases/download/2.2.1/yq_linux_amd64 && \
    chmod a+x /usr/local/bin/yq && \
    mkdir /project/output && \
    dnf install --setopt=install_weak_deps=False -y git-core ansible python3-pip mlocate jq && \
    dnf clean all && \
    pip3 install operator-courier
ADD ./run_tests.py /run_tests.py
CMD ["/run_tests.py"]
