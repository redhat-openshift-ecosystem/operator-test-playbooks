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