import os
import sys
import json
import enum

from decimal import Decimal

from base_model import BaseAuctionModel


class ModelType(enum.Enum):
    base = "BASE"
    flip = "FLIP"


if __name__ == '__main__':
    our_addresses = os.environ["OUR_ADDRESSES"]
    if isinstance(our_addresses, str):
        our_addresses = our_addresses.split()

    pair = os.environ["PAIR"]
    model_type = os.environ.get("MODEL_TYPE", ModelType.base.value)

    start_percent = Decimal(os.environ["START_PERCENT"])
    finish_percent = Decimal(os.environ["FINISH_PERCENT"])
    markup_percent = Decimal(os.environ["MARKUP_PERCENT"])

    model = BaseAuctionModel(our_addresses=our_addresses, start_percent=start_percent,
                             finish_percent=finish_percent, markup_percent=markup_percent)

    for line in sys.stdin:
        try:
            signal = json.loads(line)
            if model_type.upper() == ModelType.flip.value:
                price = model.calculate_price_for_flip_auction(signal, pair=pair)
            else:
                price = model.calculate_price_for_auction(signal, pair=pair)
            if price:
                stance = {'price': price / 10 ** 18}
                print(json.dumps(stance), flush=True)
        except:
            pass
