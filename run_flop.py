import os


from auction_keeper.main import AuctionKeeper


BASE_PATH = os.path.dirname(__file__)
# NETWORK = "kovan"
NETWORK = "mainnet"

# ETHEREUM_SETTINGS
if NETWORK.upper() == "KOVAN":
    RPC_HOST = 'https://kovan.infura.io/v3/****************'
    ETH_FROM = '0x00000000000000000000000000000'
    ETH_KEY_FILE = "/PATH/TO/KEY/FILE.json"
    ETH_PASS_FILE = "/PATH/TO/PASS/FILE.pass"
    ADDRESSES_FILE = os.path.join(BASE_PATH, 'addresses', 'kovan-addresses.json')  # or '/PATH/TO/ADDRESS/FILE.json'
elif NETWORK.upper() == "MAINNET":
    RPC_HOST = 'https://mainnet.infura.io/v3/**************'
    ETH_FROM = '0x00000000000000000000000000000'
    ETH_KEY_FILE = "/PATH/TO/KEY/FILE.json"
    ETH_PASS_FILE = "/PATH/TO/PASS/FILE.pass"
    ADDRESSES_FILE = os.path.join(BASE_PATH, 'addresses', 'mainnet-addresses.json')  # or '/PATH/TO/ADDRESS/FILE.json'
else:
    raise Exception('NOT SUPPORTED NETWORK')

# MODEL SETTINGS
MODEL_RUN_DIR = 'bin'
MODEL_FILE_NAME = 'model.sh'

model_config = {
    "start-percent": -50,
    "finish-percent": -10,
    "markup_percent": 5,
    "pair": "MDTMCR",
    "our-address": [
        ETH_FROM,
    ]
}

AUCTION_TYPE = 'flop'


def get_run_model_command():
    model_path = os.path.join(BASE_PATH, MODEL_RUN_DIR, MODEL_FILE_NAME)
    model_params = ""

    for key, value in model_config.items():
        if key == "our-address":
            model_params += "".join([f" --{key} {address}" for address in value])
        else:
            model_params += f" --{key} {value}"

    return model_path + model_params


if __name__ == '__main__':
    run_model_command = get_run_model_command()

    keeper_args = [
        '--rpc-host', RPC_HOST,
        '--eth-from', ETH_FROM,
        '--eth-key', f'key_file={ETH_KEY_FILE},pass_file={ETH_PASS_FILE}',
        '--addresses-path', ADDRESSES_FILE,
        '--ilk', 'ETH-A',
        '--type', AUCTION_TYPE,
        '--max-auctions', '100',
        '--model', run_model_command,
        '--from-block', '17707858',
        '--debug'
    ]
    AuctionKeeper(keeper_args).main()
