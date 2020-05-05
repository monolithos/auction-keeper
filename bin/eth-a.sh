#!/usr/bin/env bash
dir="$(dirname "$0")"/..
source $dir/venv/bin/activate || exit
export PYTHONPATH=$PYTHONPATH:$dir:$dir/lib/pymaker:$dir/lib/ethgasstation-client
export ACCOUNT_ADDRESS=0xC0CCab7430aEc0C30E76e1dA596263C3bdD82932
exec python3 -u -m model_flip_eth_a $@
