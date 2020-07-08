# Instruction for operator test via ansible


## Standard test on clean machine
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua
```

## Standard test with operator prerequisites (-e run_prereqs=true)
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
--tags test
```

## Standard test without operator prerequisites (-e run_prereqs=false)
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
--tags pure_test
```
or
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
--tags test \
-e run_prereqs=false
```

## Super full test on clean machine
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
-e run_manifest_test=true \
-e run_bundle_test=true
```

## Super full test quick (without installation)
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
-e run_manifest_test=true \
-e run_bundle_test=true \
--tags pure_test
```

## Install host only
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags install
```

## Reset host (eg. kind, registry)
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags reset
```

## Install dependency in playbook docker image when building
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags image_build
```

## Input source image
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_input_image=quay.io/cvpops/test-bundle:tigera-131 \
--tags pure_test
```



## Deploy operators to index
Config file:
```
$ cat test/operatos_config.yaml
operator_base_dir: /tmp/community-operators-for-catalog/upstream-community-operators
operators:
- aqua
- prometheus
```

### Deploy starting index image from scratch
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags deploy_bundles \
-e operators_config=test/operatos_config.yaml
```

### Deploy starting index image from kind-registry:5000/test-operator/index:latest
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags reset,deploy_bundles \
-e operators_config=test/operatos_config.yaml \
-e bundle_index_image_from="kind-registry:5000/test-operator/index:latest"
```

### Deploy index image and force channels to stable
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags deploy_bundles \
-e operators_config=test/operatos_config.yaml
-e operator_channel_force=stable
```




