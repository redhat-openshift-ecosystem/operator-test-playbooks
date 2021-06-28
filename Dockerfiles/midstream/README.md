# operator-bundle-validate-container
CVP midstream operator bundle validate container

## Prerequisites

In order to run unit_tests.py on your local without any issues, you need to make sure 
you run the command with specific options. 
Here is an example of running the unit_tests.py locally
`sudo podman run -it -v $PWD:/project/operator-test-playbooks:z <midstream_image> /unit_tests.py`
First thing you reckon is that you are running this command directly from upstream repo `operator-test-playbooks` and you have build your own midstream_image locally from Dockerfiles/midstream/Dockerfile.

# Usage

## Building image on local machine 

```
git clone https://github.com/redhat-operator-ecosystem/operator-test-playbooks.git
cd operator-test-playbooks
### podman build -t <image_name>:<tagname> -f <filepath> --build-arg OPERATOR_SDK_VERSION=<operator_sdk_version> --build-arg
### example:
podman build -t midstream_image:latest -f Dockerfile . --build-arg OPERATOR_SDK_VERSION=v1.4.0 
```

## Running image with operator bundle

```
podman run -it -v <operator_bundle_dir>:/project/operator-bundle -v <output_log>:/project/output --security-opt label=disable <imagename>:<tagname> -e IMAGE_TO_TEST=<image_url_to_test> -e VERBOSITY=<number in range of 1 to 4>
mkdir output_logs
podman run -it -v ./example-bundle:/project/operator-bundle -v ./output_logs:/project/output --security-opt label=disable midstream_image:latest -e IMAGE_TO_TEST='quay.io://image_url_to_test' VERBOSITY=3
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

