# operator-bundle-validate-container
CVP midstream operator bundle validate container

# Usage

## Building image on local machine 

```
git clone https://github.com/redhat-operator-ecosystem/operator-test-playbooks.git
cd Dockerfiles
### podman build -t <image_name>:<tagname> -f <filepath> --build-arg OPERATOR_SDK_VERSION=<operator_sdk_version> --build-arg OPERATOR_TEST_PLAYBOOKS_TAG=<operator_test_playbooks_tag>
### example:
podman build -t midstream_image:latest -f Dockerfile --build-arg OPERATOR_SDK_VERSION=v1.4.0 --build-arg OPERATOR_TEST_PLAYBOOKS_TAG=v1.0.11
```

## Running image with operator bundle

```
podman run -it -v <operator_bundle_dir>:/project/operator-bundle -v <output_log>:/project/output --security-opt label=disable <imagename>:<tagname> -e IMAGE_TO_TEST=<image_url_to_test>
mkdir output_logs
podman run -it -v ./example-bundle:/project/operator-bundle -v ./output_logs:/project/output --security-opt label=disable midstream_image:latest -e IMAGE_TO_TEST='quay.io://image_url_to_test' 
```

### Note:
Example operator bundle tree looks as follows:
```
example-bundle
├── manifests
│   ├── clusterresourceoverride.crd.yaml
│   └── clusterresourceoverride-operator.v4.6.0.clusterserviceversion.yaml
└── metadata
    └── annotations.yaml
```

