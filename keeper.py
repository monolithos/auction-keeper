import os
import uuid
import json

import web3

from auction_keeper.main import AuctionKeeper


BASE_PATH = os.path.dirname(__file__)

NETWORK = os.environ.get("NETWORK", "mainnet")
AUCTION_TYPE = os.environ.get("AUCTION_TYPE", "flip")

# MODEL SETTINGS
MODEL_RUN_DIR = 'bin'
MODEL_FILE_NAME = 'model.sh'


def get_run_model_command(model_config):
    model_path = os.path.join(BASE_PATH, MODEL_RUN_DIR, MODEL_FILE_NAME)
    model_params = ""

    for key, value in model_config.items():
        if value is not None and not isinstance(value, (bool, list)):
            model_params += f" --{key} {value}"
        elif isinstance(value, bool) and value:
            model_params += f" --{key}"
        elif isinstance(value, list) and len(value) > 0 and value[0] is not None:
            model_params += "".join([f" --{key} {address}" for address in value])

    return model_path + model_params


def generate_params_line(param_group: list):
    args = []
    for param in param_group:
        if param[1] is not None and not isinstance(param[1], (bool, list)):
            args.append(param[0])
            args.append(str(param[1]))
        elif isinstance(param[1], bool) and param[1]:
            args.append(param[0])
        elif isinstance(param[1], list) and len(param[1]) > 0 and param[1][0] is not None:

            for item in param[1]:
                args.append(param[0])
                args.append(str(item))
    return args


class EnvParam:
    value = None

    def __init__(self, env_name: str, cast_type, required, default=None):
        try:
            if cast_type in (list, set, tuple):
                self.value = cast_type(os.environ[env_name].split())
            else:
                self.value = cast_type(os.environ[env_name])
        except (TypeError, KeyError) as e:
            if required:
                raise Exception(f'Param {env_name} is required and must be cast to {str(cast_type)}')
            if cast_type in (list, set, tuple) and default is not None:
                self.value = cast_type([default])
            else:
                self.value = cast_type(default) if default is not None else None


def get_telegram_params():
    telegram_bot_token = EnvParam(env_name="TELEGRAM_BOT_TOKEN", cast_type=str, required=False).value

    if telegram_bot_token:
        chat_ids = {}
        ids = EnvParam(env_name="TELEGRAM_CHAT_IDS", cast_type=list, required=False, default=[]).value
        list(map(lambda x: chat_ids.update({x: x}), ids))
        telegram_conf_file = os.path.join(BASE_PATH, "telegram_conf.json")
        telegram_conf = {
            "bot_token": telegram_bot_token,
            "project_name": EnvParam(env_name="PROJECT_NAME", cast_type=str, required=False, default="monolithos_market_maker_keeper").value,
            "use_proxy": False,
            "request_kwargs": {
                "proxy_url": "",
                "urllib3_proxy_kwargs": {
                    "username": "",
                    "password": ""
                }
            },
            "chat_ids": chat_ids
        }
        with open(telegram_conf_file, "w") as file:
            file.write(json.dumps(telegram_conf))

        return [('--telegram-log-config-file', telegram_conf_file)]
    else:
        return []


if __name__ == '__main__':
    telegram_params = get_telegram_params()
    password = str(uuid.uuid4())
    pk = EnvParam(env_name="ETH_PRIVATE_KEY", cast_type=str, required=True).value
    encrypt_pk = web3.Web3().eth.account.encrypt(private_key=pk, password=password)

    ETH_FROM = web3.Web3.toChecksumAddress(encrypt_pk["address"])
    P_ETH_FROM = EnvParam(env_name="ETH_FROM", cast_type=str, required=True).value

    if P_ETH_FROM.upper() != ETH_FROM.upper():
        raise Exception(f"private key does not match the ETH_FROM address ({P_ETH_FROM})")

    key_file = os.path.join(BASE_PATH, "key.json")
    pass_file = os.path.join(BASE_PATH, "pass.pass")
    with open(key_file, "w") as file:
        file.write(json.dumps(encrypt_pk))
    with open(pass_file, "w") as file:
        file.write(password)

    ETH_KEY = f'key_file={key_file},pass_file={pass_file}'
    MODEL_TYPE = EnvParam(env_name="MODEL_TYPE", cast_type=str, required=False, default=None).value

    if MODEL_TYPE is None:
        MODEL_TYPE = 'BASE' if AUCTION_TYPE != 'flip' else 'FLIP'

    model_config_ = {
        "start-percent": EnvParam(env_name="MODEL_START_PERCENT", cast_type=str, required=True).value,
        "finish-percent": EnvParam(env_name="MODEL_FINISH_PERCENT", cast_type=str, required=True).value,
        "markup_percent": EnvParam(env_name="MODEL_MARKUP_PERCENT", cast_type=str, required=True).value,
        "pair": EnvParam(env_name="MODEL_PAIR", cast_type=str, required=True).value,
        "model-type": MODEL_TYPE,
        "our-address": EnvParam(env_name="MODEL_OUR_ADDRESSES", cast_type=list, required=False, default=[ETH_FROM]).value,
    }

    required_params = [
        ('--rpc-host', EnvParam(env_name="RPC_HOST", cast_type=str, required=True).value),
        ('--eth-from', str(ETH_FROM)),
        ('--eth-key', str(ETH_KEY)),
        ('--addresses-path', str(os.path.join(BASE_PATH, 'addresses', f'{NETWORK}-addresses.json'))),
        ('--type', str(AUCTION_TYPE)),
        ('--model', str(get_run_model_command(model_config=model_config_))),
    ]

    flip_params = [
        ('--ilk', EnvParam(env_name="ILK", cast_type=str, required=False).value),
        ('--min-flip-lot', EnvParam(env_name="MIN_FLIP_LOT", cast_type=str, required=False).value),
    ]

    optional_params = [
        ('--bid-only', EnvParam(env_name="BID_ONLY", cast_type=bool, required=False, default=False).value),
        ('--kick-only', EnvParam(env_name="KICK_ONLY", cast_type=bool, required=False, default=False).value),
        ('--deal-for', EnvParam(env_name="DEAL_FOR", cast_type=list, required=False, default=[ETH_FROM]).value),
        ('--min-auction', EnvParam(env_name="MIN_AUCTION", cast_type=int, required=False).value),
        ('--max-auctions', EnvParam(env_name="MAX_AUCTIONS", cast_type=int, required=False).value),
        ('--bid-check-interval', EnvParam(env_name="BID_CHECK_INTERVAL", cast_type=float, required=False).value),
        ('--bid-delay', EnvParam(env_name="BID_DELAY", cast_type=float, required=False).value),

        ('--rpc-timeout', EnvParam(env_name="RPC_TIMEOUT", cast_type=int, required=False).value),
        ('--from-block', EnvParam(env_name="FROM_BLOCK", cast_type=int, required=False, default=10310344).value),

        ('--vat-dai-target', EnvParam(env_name="VAT_MCR_TARGET", cast_type=float, required=False).value),
        ('--keep-dai-in-vat-on-exit', EnvParam(env_name="KEEP_MCR_IN_VAT_ON_EXIT", cast_type=bool, required=False, default=False).value),
        ('--keep-gem-in-vat-on-exit', EnvParam(env_name="KEEP_GEM_IN_VAT_ON_EXIT", cast_type=bool, required=False, default=False).value),

        ('--ethgasstation-api-key', EnvParam(env_name="ETHGASSTATION_API_KEY", cast_type=str, required=False).value),
        ('--fixed-gas-price', EnvParam(env_name="FIXED_GAS_PRICE", cast_type=float, required=False).value),
        ('--gas-maximum', EnvParam(env_name="GAS_MAXIMUM", cast_type=float, required=False).value),
        # ('--debug', True),
    ]

    keeper_args = generate_params_line(required_params) + generate_params_line(optional_params)
    if AUCTION_TYPE.upper() == 'FLIP':
        keeper_args += generate_params_line(flip_params)
    keeper_args += generate_params_line(telegram_params)
    AuctionKeeper(keeper_args).main()
    print(f"AuctionKeeper {keeper_args}")
