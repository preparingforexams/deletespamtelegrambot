#!/bin/bash

v=$1
image=torbencarstens/spamkicker
k8sfile=.kubernetes/manifest.yaml

docker build -t $image:$v .
docker push $image:$v
sed -i -e "s/:{{TAG}}/:${v}/g" $k8sfile
kubectl apply -f $k8sfile
sed -i -e "s/:${v}/:{{TAG}}/g" $k8sfile
