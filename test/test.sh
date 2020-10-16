#!/bin/bash

pip install ansible jmespath

ansible-pull -U https://github.com/J0zi/operator-test-playbooks -C upstream-community -i localhost, -e ansible_connection=local -e run_upstream=true --tags base,docker,kind,kubectl

kubectl get all --all-namespaces
