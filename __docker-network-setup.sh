#!/usr/bin/env bash

# Docker 네트워크가 있는지 확인하고 없으면 생성합니다.
cnt=$(docker network list | grep micro-network | wc -l)
if [[ $cnt -eq 0 ]]; then
    docker network create \
      --driver=bridge \
      --subnet=172.235.0.0/16 \
      --ip-range=172.235.100.0/24 \
      --gateway=172.235.100.254 \
      micro-network
fi
