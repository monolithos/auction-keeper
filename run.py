from auction_keeper.main import AuctionKeeper


if __name__ == '__main__':
    flip_args = [
        '--rpc-host', 'https://kovan.infura.io/v3/683836c8b9384898a9f99d483ae389bc',
        '--eth-from', '0xC0CCab7430aEc0C30E76e1dA596263C3bdD82932',
        '--eth-key', 'key_file=/home/captain/development/dss-deploy-scripts/keystore.json,pass_file=/home/captain/development/dss-deploy-scripts/p.pass',
        '--addresses-path', '/home/captain/development/makerdao_python/auction-keeper/addresses/kovan-addresses.json',
        '--ilk', 'ETH-A',
        '--type', 'flip',
        '--max-auctions', '100',
        # '--model', 'bin/auction-keeper',
        '--model', '/home/captain/development/makerdao_python/auction-keeper/bin/eth-a.sh',
        '--from-block', '17707858',
        '--debug'
    ]
    AuctionKeeper(flip_args).main()
