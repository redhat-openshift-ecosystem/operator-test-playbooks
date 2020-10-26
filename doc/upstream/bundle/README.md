# Bundle deploy and testing

## Bundle format
### Bundle directory structure

Bundle format consists 2 direcotries (`manifests` and `metadata`). It might contain the optional `Dockerfile` to build custom bundles (99% it is not needed).
```
prometheus
└── 0.40.0
    ├── Dockerfile (optional)
    ├── manifests
    │   ├── alertmanagers.monitoring.coreos.com.crd.yaml
    │   ├── podmonitors.monitoring.coreos.com.crd.yaml
    │   ├── prometheuses.monitoring.coreos.com.crd.yaml
    │   ├── prometheusoperator.v0.40.0.clusterserviceversion.yaml
    │   ├── prometheusrules.monitoring.coreos.com.crd.yaml
    │   └── servicemonitors.monitoring.coreos.com.crd.yaml
    └── metadata
        └── annotations.yaml
```

### Manifests directory

This directory contains one CSV file (`<name>.<version>-clusterserviceversion.yaml`) and multiple CRDs needed for operartor to run correctly.

### Metadata directory

Metadata directory contains `annotations.yaml` file with information about operator packaging in yaml format. E.g.
```
[mvala@localhost community-operators]$ cat prometheus/0.40.0/metadata/annotations.yaml
annotations:
  operators.operatorframework.io.bundle.package.v1: "prometheus"
  operators.operatorframework.io.bundle.channels.v1: "preview"
  operators.operatorframework.io.bundle.channel.default.v1: "preview"
  operators.operatorframework.io.bundle.mediatype.v1: "registry+v1"
  operators.operatorframework.io.bundle.manifests.v1: "manifests/"
  operators.operatorframework.io.bundle.metadata.v1: "metadata/"
```
It decribes following values
| Name | Description |
| :---- | :------ |
|operators.operatorframework.io.bundle.package.v1| Package name |
|operators.operatorframework.io.bundle.channels.v1| List of channels (comma separated)|
|operators.operatorframework.io.bundle.channel.default.v1| Default channel|
|operators.operatorframework.io.bundle.mediatype.v1| Operator media type|
|operators.operatorframework.io.bundle.manifests.v1| Location of manifests files|
|operators.operatorframework.io.bundle.metadata.v1| Location of metadata|

### Porting from old manifest format

- Copy all files to `manifests` directory
- Create `metadata/annotations.yaml` file
- Port package information to  `metadata/annotations.yaml` and delete `*package.yaml` file

## Testing of bundle format

Testing documentation is located [here](https://github.com/redhat-operator-ecosystem/operator-test-playbooks/tree/upstream-community/doc/upstream/users). One can use `kiwi` Test to test the operator

### KIWI test
We call full operator test with name `kiwi`. It is easy to remember and user can run same test (Since in CI same name is used), as it is done when doing PR. It consists of following steps

- Verify integrity of operator
- Deploys operator on `kind` cluster
- Test operator if it can be started and healhy for some period of time

In this example, one can see `kiwi` test
```
Using ansible 2.9.13 ...

One can do 'tail -f /tmp/op-test/log.out' from second console to see full logs

Checking for kind binary ...
Test 'kiwi' ...
[kiwi] Reseting kind cluster ...
[kiwi] Running test (upstream-community-operators aqua 1.0.2) ...
Test 'kiwi' : [ OK ]

Done
```

Temporary artifact storage are located in `op-test` container in `/tmp/operator-test` directory. One can enter container via


```
$ podman exec -it op-test /bin/bash
[in container] $ ls -al /tmp/operator-test/
total 156
drwxr-xr-x 1 root root  4096 Oct 26 13:15 .
drwxrwxrwt 1 root root  4096 Oct 26 13:17 ..
drwxr-xr-x 3 root root  4096 Oct 22 08:16 bin
-rw-r--r-- 1 root root   910 Oct 26 13:12 bundle-skopeo-inspect.json
-rw-r--r-- 1 root root     0 Oct 26 13:13 linting-errors.txt
-rw-r--r-- 1 root root     0 Oct 26 13:13 linting-output.txt
-rw-r--r-- 1 root root     1 Oct 26 13:13 linting-rc.txt
-rw-r--r-- 1 root root    31 Oct 26 13:13 linting-results.json
-rw-r--r-- 1 root root     5 Oct 26 13:13 linting-version.txt
-rw-r--r-- 1 root root 17234 Oct 26 13:15 olm-catalog-operator-debug.txt
-rw-r--r-- 1 root root   225 Oct 26 13:15 olm-catalog-source-debug.txt
-rw-r--r-- 1 root root 28462 Oct 26 13:15 olm-installplan-debug.txt
-rw-r--r-- 1 root root  9966 Oct 26 13:15 olm-operator-container-debug.txt
-rw-r--r-- 1 root root 23299 Oct 26 13:15 olm-operator-csv-debug.txt
drwxr-xr-x 2 root root  4096 Oct 26 13:13 olm-operator-files
-rw-r--r-- 1 root root   982 Oct 26 13:15 olm-operator-pod-debug.txt
drwxr-xr-x 4 root root  4096 Oct 26 13:12 operator-bundle
drwxr-xr-x 3 root root  4096 Oct 26 13:13 operator-bundle-for-courier
drwxr-xr-x 4 root root  4096 Oct 26 13:12 operator-files
-rw-r--r-- 1 root root  1130 Oct 26 13:12 parsed_operator_data.yml
-rw-r--r-- 1 root root   475 Oct 26 13:12 validation-output.txt
-rw-r--r-- 1 root root     1 Oct 26 13:12 validation-rc.txt
-rw-r--r-- 1 root root   151 Oct 26 13:12 validation-version.txt
```

### LEMON and ORANGE tests

When operator is well tested one can test if operator can be added to the index catalog. There are 2 test cases:

- `lemon`  : Operator is added to index from scratch (all previous versions are rebuilt)
- `orange` : Operator is added to index and all previous bundle versions are added from production registry for [community-operators](https://quay.io/organization/openshift-community-operators) and [upstream-community-operators](https://quay.io/organization/operatorhubio)

# Index image

Operator can be subscribed to an `index image`. There are 3 location for index images on Quay.io.
* Openshift index https://quay.io/repository/redhat/redhat----community-operator-index?tag=latest&tab=tags
* Openshift public index https://quay.io/repository/openshift-community-operators/catalog?tab=tags. All Openshift operators in bundle image format are a directory above.
* Kubernetes index image https://quay.io/repository/operatorhubio/catalog?tab=tags. Same applies here. All Openshift operators in bundle image format are a directory above.

## Index build process
Index image is build by Travis during [community-operator-catalog build](https://travis-ci.com/github/operator-framework/community-operator-catalog/builds).
There are 2 branches important, `community-operators` and `upstream-community-operators` which are supposed to build index for the specific stream - Openshift and Kubernetes.

### Bundle build
After a merge of specific operator, bundle for specific version is built and pushed to specific quay. It is either [openshift-community-operators]( https://quay.io/repository/openshift-community-operators) or [operatorhubio](https://quay.io/repository/operatorhubio).

### Add operator to index
After actual bundle image is ready, whole package is removed from the index.
Then bundle images are added, existing images from quay plus newly created one. It allows to change [update graph](https://github.com/operator-framework/community-operators/blob/master/docs/operator-versioning.md) after a merge also.

### Corner case - just ci.yaml has changed
In case no operator was modified, just [update graph](https://github.com/operator-framework/community-operators/blob/master/docs/operator-versioning.md), package is removed and added to index with actual flag setting update graph.