#!/bin/bash

our_addresses=()
deal_for=()

while [ "$1" != "" ]; do
    case $1 in
        -h   | --help )                  shift
                                  cat docker-run-help-command.txt
                                  echo
                                  exit 1
                                  ;;
        -msp | --model-start-percent )   shift
                                  export MODEL_START_PERCENT=$1
                                  ;;
        -mfp | --model-finish-percent )  shift
                                  export MODEL_FINISH_PERCENT=$1
                                  ;;
        -mmp | --model-markup_percent )  shift
                                  export MODEL_MARKUP_PERCENT=$1
                                  ;;
        -mp  | --model-pair )            shift
                                  export MODEL_PAIR=$1
                                  ;;
        -moa | --model-our-address )     shift
                                         our_addresses+=( "$1" )
                                  ;;
        -mt  | --model-type )             shift
                                  export MODEL_TYPE=$1
                                  ;;
        -t   | --auction-type )          shift
                                  export AUCTION_TYPE=$1
                                  ;;
        -rpc | --rpc-host )                shift
                                  export RPC_HOST=$1
                                  ;;
        -pk  | --address-private-key )   shift
                                  export ETH_PRIVATE_KEY=$1
                                  ;;
        -a   | --eth-from )              shift
                                  export ETH_FROM=$1
                                  ;;
        -i   | --ilk )                   shift
                                  export ILK=$1
                                  ;;
        --network )                      shift
                                  export NETWORK=$1
                                  ;;
        --rpc-timeout )                  shift
                                  export RPC_TIMEOUT=$1
                                  ;;
        --deal-for )                     shift
                                         deal_for+=( "$1" )
                                  ;;
        --bid-only )                     shift
                                  export BID_ONLY=true
                                  ;;
        --kick-only )                    shift
                                  export KICK_ONLY=true
                                  ;;
        --min-auction )                  shift
                                  export MIN_AUCTION=$1
                                  ;;
        --max-auctions )                  shift
                                  export MAX_AUCTION=$1
                                  ;;
        --min-flip-lot )                 shift
                                  export MIN_FLIP_LOT=$1
                                  ;;
        --bid-check-interval )           shift
                                  export BID_CHECK_INTERVAL=$1
                                  ;;
        --bid-delay )                    shift
                                  export BID_DELAY=$1
                                  ;;
        --from-block )                   shift
                                  export FROM_BLOCK=$1
                                  ;;
        --vat-mcr-target )               shift
                                  export VAT_MCR_TARGET=$1
                                  ;;
        --keep-mcr )                     shift
                                  export KEEP_MCR_IN_VAT_ON_EXIT=true
                                  ;;
        --keep-gem )                     shift
                                  export KEEP_GEM_IN_VAT_ON_EXIT=true
                                  ;;
        --ethgasstation-api-key )           shift
                                  export ETHGASSTATION_API_KEY=$1
                                  ;;
        --fixed-gas-price )              shift
                                  export FIXED_GAS_PRICE=$1
                                  ;;
        --gas-maximum )                  shift
                                  export GAS_MAXIMUM=$1
                                  ;;
        --setzer-pairs )                 shift
                                  setzer pairs
                                  echo
                                  exit 1
                                  ;;
        * )                       shift
                                  ;;
    esac
                                  shift
done

export  MODEL_OUR_ADDRESSES="${our_addresses[*]}"
export  DEAL_FOR="${deal_for[*]}"

if [[ -z $MODEL_START_PERCENT || \
      -z $MODEL_FINISH_PERCENT || \
      -z $MODEL_MARKUP_PERCENT || \
      -z $MODEL_PAIR || \
      -z $MODEL_OUR_ADDRESSES || \
      -z $AUCTION_TYPE || \
      -z $RPC_HOST || \
      -z $ETH_PRIVATE_KEY || \
      -z $ETH_FROM ]] ;
then
    cat docker-run-required-params.txt
    echo
    exit 1
fi

python keeper.py
