#!/bin/bash
SLS_URL=${1-"tcp://toolbox.localhost:41000"}

salsa-ndm -s $SLS_URL -c ndm.yaml
