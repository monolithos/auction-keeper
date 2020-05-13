import os


from auction_keeper.main import AuctionKeeper

BASE_PATH = os.path.dirname(__file__)

# ETHEREUM_SETTINGS
RPC_HOST = 'https://kovan.infura.io/v3/683836c8b9384898a9f99d483ae389bc'
ETH_FROM = '0xC0CCab7430aEc0C30E76e1dA596263C3bdD82932'
ETH_KEY_FILE = "/home/captain/development/dss-deploy-scripts/keystore.json"
ETH_PASS_FILE = "/home/captain/development/dss-deploy-scripts/p.pass"
ADDRESSES_FILE = os.path.join(BASE_PATH, 'addresses', 'kovan-addresses.json')

# MODEL SETTINGS
MODEL_RUN_DIR = 'bin'
MODEL_FILE_NAME = 'model.sh'

model_config = {
    "start-percent": -50,
    "finish-percent": -10,
    "markup_percent": 10,
    "pair": "ETHRUB",
    "our-address": [
        ETH_FROM,
    ]
}

AUCTION_TYPE = 'flip'


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
        '--eth-key', f'key_file={ETH_KEY_FILE}aaaaaaaaaaaa,pass_file={ETH_PASS_FILE}',
        '--addresses-path', ADDRESSES_FILE,
        '--ilk', 'ETH-A',
        '--type', AUCTION_TYPE,
        '--max-auctions', '100',
        '--model', run_model_command,
        '--from-block', '17707858',
        '--debug'
    ]
    AuctionKeeper(keeper_args).main()
