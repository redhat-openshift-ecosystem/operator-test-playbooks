# operator-bundle-validate-container
CVP midstream operator bundle validate container

# Usage

## Building image on local machine 

```
git clone https://github.com/redhat-operator-ecosystem/operator-bundle-validate-container
cd operator-bundle-validate-container
### podman build -t <image_name>:<tagname> -f <filepath>
podman build -t midstream_image:latest -f Dockerfile
```

## Running image with operator bundle

```
podman run -it -v <operator_bundle_dir>:/project/operator-bundle -v <output_log>:/project/output --security-opt label=disable <imagename>:<tagname>

podman run -it -v ./example-bundle:/project/operator-bundle -v ./output_logs:/project/output --security-opt label=disable midstream:latest 
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

#### Example Output of the container 
```
operatorSDKVersion is operator-sdk version: "v1.4.0", commit: "67f9c8b888887d18cd38bb6fd85cf3cf5b94fd99", kubernetes version: "1.19.4", go version: "go1.15.5", GOOS: "linux", GOARCH: "amd64"
Operator bundle validation Return Code is 0
Operator bundle Validation output is 
 time="2021-02-12T01:16:57Z" level=debug msg="Debug logging is set"
time="2021-02-12T01:16:57Z" level=debug msg="Found manifests directory" bundle-dir=../operator-bundle container-tool=docker
time="2021-02-12T01:16:57Z" level=debug msg="Found metadata directory" bundle-dir=../operator-bundle container-tool=docker
time="2021-02-12T01:16:57Z" level=debug msg="Getting mediaType info from manifests directory" bundle-dir=../operator-bundle container-tool=docker
time="2021-02-12T01:16:57Z" level=info msg="Found annotations file" bundle-dir=../operator-bundle container-tool=docker
time="2021-02-12T01:16:57Z" level=info msg="Could not find optional dependencies file" bundle-dir=../operator-bundle container-tool=docker
time="2021-02-12T01:16:57Z" level=debug msg="Validating bundle contents" bundle-dir=../operator-bundle container-tool=docker
time="2021-02-12T01:16:57Z" level=info msg="All validation tests have completed successfully"

Bundle image validation is successful
```
