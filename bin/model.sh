#!/usr/bin/env bash
dir="$(dirname "$0")"/..

our_addresses=()

while [ "$1" != "" ]; do
    case $1 in
        -sp | --start-percent )   shift
                                  export START_PERCENT=$1
                                  ;;
        -fp | --finish-percent )  shift
                                  export FINISH_PERCENT=$1
                                  ;;
        -mp | --markup_percent )  shift
                                  export MARKUP_PERCENT=$1
                                  ;;
        -p | --pair )             shift
                                  export PAIR=$1
                                  ;;
        -a | --our-address )      shift
                                  our_addresses+=( "$1" )
                                  ;;
        -rd | --root-dir )      shift
                                  dir=$1
                                  ;;
        * )                       usage
                                  exit 1
    esac
    shift
done

export  OUR_ADDRESSES="${our_addresses[*]}"

source $dir/venv/bin/activate || exit
export PYTHONPATH=$PYTHONPATH:$dir:$dir/lib/pymaker:$dir/lib/ethgasstation-client
exec python3 -u -m model $@
