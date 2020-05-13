import decimal
import logging
from decimal import Decimal
from typing import List, Optional

from setzer import Setzer


class BaseAuctionModel:
    """
    our_addresses:
        RU: Адреса дружественных хранителей, чьи ставки не будут перебиваться
        EN: Addresses of friendly keepers whose bids will not be interrupted
    start_percent:
        RU: Нижняя граница допустимого процента изменения рыночной цены
        EN: Lower limit of the acceptable percentage of market price change
    finish_percent:
        RU: Верхняя граница допустимого процента изменения рыночной цены
        EN: Upper limit of the acceptable percentage of market price change
    markup_percent:
        RU: Процент увеличение цены
        EN: Percentage increase in price

    """
    our_addresses: List[str]
    start_percent: Decimal
    finish_percent: Decimal
    markup_percent: Decimal

    accuracy = Decimal("0.00000000001")
    logger = logging.getLogger()

    def __init__(self, our_addresses: List[str], start_percent: Decimal, finish_percent: Decimal, markup_percent: Decimal):
        self.our_addresses = our_addresses
        self.markup_percent = markup_percent
        self.start_percent, self.finish_percent = start_percent, finish_percent

    @staticmethod
    def get_price(*args, **kwargs) -> int:
        """
        RU:
            функция получения цены для пары валюты
        EN:
            function for getting the price for a currency pair
        """
        price = Setzer().price(kwargs.get("pair", "ETHRUB")).value
        return price

    @staticmethod
    def calculate_value(value: int, percent: Decimal) -> int:
        """
        RU:
            Расчет цены с учетом процента наценки или скидки
        EN:
            Calculating the price with a percentage of the markup or discount
        example:
            calculate_value(100, 10):   100 + 10% = 110
            calculate_value(100, -10):  100 + (-10)% = 90
        """
        percent_value = int(value * percent / 100)
        return value + percent_value

    def calculate_price_for_flip_auction(self, bid_info: dict, *args, **kwargs) -> Optional[int]:
        """
        RU:
            1: Проверяем, чтобы предыдущая ставка была сделана не нашим хранителем
            2: Проверка цены:
                2.1: Если минимальная цена, требуемая для ликвидации дефицита в хранилище,
                     больше, чем текущая цена в bid и одновременно меньше чем рыночная цена + [[FINISH_PERCENT]]:
                        -  Минимальная цена ликвидирования дефицита в хранилище и будет ценой для следующей ставки.
                2.2: Если текущая цена из bid + [[MARKUP_PERCENT]] меньше, чем рыночная цена + [[FINISH_PERCENT]]:
                        -  Текущая цена из bid + [[MARKUP_PERCENT]] и будет ценой для следующей ставки.
                2.3: В любых других случаях торговля не осуществляется
        EN:
            1: Check that the previous bid was not made by our Keeper
            2: Checking the price:
                2.1: If the minimum price required to liquidate the deficit in the vault, more than the current
                      bid price and at the same time less than the market price + [[FINISH_PERCENT]]:
                        -  The minimum price for liquidation the deficit in the vault and will
                            be the price for the next bid.
                2.2: If the current bid price + [[MARKUP_PERCENT]] is less than the market price + [[FINISH_PERCENT]]:
                        -  The current price from bid + [[MARKUP_PERCENT]] and will be the price for the next bid.
                2.3: In any other situations, trading is not carried out


        :param bid_info: dic, for example:
            {
                "id": "1",  // bid id
                "bid": "0.000000000000000000000000000000000000000000000",  // amount stable money
                "lot": "0.010000000000000000",  // amount gem money
                "beg": "1.030000000000000000",  // percent for price upper
                "guy": "0x338ca6F74eEc69b671e6A55AEd5fA10992599955",  // owner current high bid (address)
                "era": 1588858560,
                "tic": 0,  // bid expiry
                "end": 1589117720,  //  when the auction will finish / max auction duration
                "price": "0.000000000000000000",  // price for buy gem money / stable money
                "tab": "114.830623992518615104174660397293941268560159733",  // total stb. mny.  wanted from the auction
                "flipper": "0x79535e0ed337f7cC842f93e0db84aC1dFDa2AF6C"  // flip contract address
            }
        :return: int
        """
        assert 'price' in bid_info, "field `price` not found in bid_info"
        assert 'tab' in bid_info, "field `tab` not found in bid_info"
        assert 'lot' in bid_info, "field `lot` not found in bid_info"

        self.logger.info(f"taken bid{bid_info['id']}: \t {bid_info}")

        if bid_info['guy'].lower() in [address.lower() for address in self.our_addresses]:
            self.logger.info(f"bid{bid_info['id']}: \t bid of a friendly keeper")
            return None

        # ru: рыночная цена
        # en: market price
        market_price = self.get_price(pair=kwargs.get("pair", "ETHRUB"))

        # ru: текущая цена в bid
        # en: current bid price
        bid_price = int(
            Decimal(bid_info['price']).quantize(exp=self.accuracy, rounding=decimal.ROUND_UP) * 10 ** 18
        ) if bid_info['price'] is not None else 0

        # ru: Минимальная цена ликвидирования дефицита в хранилище
        # en: Minimum price for liquidation the deficit in vault
        raw_deficit_price = Decimal(
            Decimal(bid_info['tab']) / Decimal(bid_info['lot'])).quantize(exp=self.accuracy,
                                                                          rounding=decimal.ROUND_UP)
        deficit_price = int(raw_deficit_price * 10 ** 18)
        self.logger.info(f"bid{bid_info['id']}: \t market_price={market_price}, bid_price={bid_price}, deficit_price={deficit_price}")
        if bid_price < deficit_price < self.calculate_value(market_price, self.finish_percent):
            self.logger.info(f"bid{bid_info['id']}: \t next bid price is deficit_price = {deficit_price}")
            return deficit_price
        elif self.calculate_value(bid_price, self.markup_percent) < self.calculate_value(market_price, self.finish_percent):
            next_bid_price = self.calculate_value(bid_price, self.markup_percent)
            self.logger.info(f"bid{bid_info['id']}: \t next bid price is bid_price + markup_percent = {next_bid_price}")
            return next_bid_price
        else:
            return None

    def calculate_price_for_auction(self, bid_info: dict, *args, **kwargs) -> Optional[int]:
        """
        RU:
            1: Проверяем, чтобы предыдущая ставка была сделана не нашим хранителем
            2: Проверка цены:
                2.1: Если текущая цена bid == 0 (не установлена):
                        -  Рыночная цена + [[START_PERCENT]] и будет ценой для следующей ставки.
                2.2: Если [[MARKUP_PERCENT]] >= 0 и текущая цена из bid + [[MARKUP_PERCENT]] меньше,
                     чем рыночная цена + [[FINISH_PERCENT]]:
                        -  Текущая цена из bid + [[MARKUP_PERCENT]] и будет ценой для следующей ставки.
                2.3: Если [[MARKUP_PERCENT]] < 0 и текущая цена из bid + [[MARKUP_PERCENT]] больше,
                     чем рыночная цена + [[FINISH_PERCENT]]:
                        -  Текущая цена из bid + [[MARKUP_PERCENT]] и будет ценой для следующей ставки.
                2.4: В любых других случаях торговля не осуществляется
        EN:
            1: Check that the previous bid was not made by our Keeper
            2: Checking the price:
                2.1: If the current bid price = = 0 (not set):
                        -  Market price + [[START_PERCENT]] and will be the price for the next bid
                2.2: If [[MARKUP_PERCENT]] >= 0 and the current bid price + [[MARKUP_PERCENT]]
                     is less than the market price + [[FINISH_PERCENT]]:
                        -  The current price from bid + [[MARKUP_PERCENT]] and will be the price for the next bid.
                2.3: If [[MARKUP_PERCENT]] < 0 and the current bid price + [[MARKUP_PERCENT]]
                     is more than the market price + [[FINISH_PERCENT]]:
                        -  The current price from bid + [[MARKUP_PERCENT]] and will be the price for the next bid.
                2.4: In any other situations, trading is not carried out

        :param bid_info: dic, for example:
            {
                "id": "1",  // bid id
                "bid": "0.000000000000000000000000000000000000000000000",  // amount stable money
                "lot": "0.010000000000000000",  // amount gem money
                "beg": "1.030000000000000000",  // percent for price upper
                "guy": "0x338ca6F74eEc69b671e6A55AEd5fA10992599955",  // owner current high bid (address)
                "era": 1588858560,
                "tic": 0,  // bid expiry
                "end": 1589117720,  //  when the auction will finish / max auction duration
                "price": "0.000000000000000000",  // price for buy gem money / stable money
                "flipper": "0x79535e0ed337f7cC842f93e0db84aC1dFDa2AF6C"  // flip contract address
            }
        :return: int
        """
        assert 'price' in bid_info, "field `price` not found in bid_info"

        self.logger.info(f"taken bid{bid_info['id']}: \t {bid_info}")

        if bid_info['guy'].lower() in [address.lower() for address in self.our_addresses]:
            self.logger.info(f"bid{bid_info['id']}: \t bid of a friendly keeper")
            return None

        # ru: рыночная цена
        # en: market price
        market_price = self.get_price(pair=kwargs.get("pair", "MDTRUB"))

        # ru: текущая цена в bid
        # en: current bid price
        bid_price = int(
            Decimal(bid_info['price']).quantize(exp=self.accuracy, rounding=decimal.ROUND_UP) * 10 ** 18
        ) if bid_info['price'] is not None else 0

        self.logger.info(f"bid{bid_info['id']}: \t market_price={market_price}, bid_price={bid_price}")

        if bid_price == 0:
            next_bid_price = self.calculate_value(market_price, self.start_percent)
            self.logger.info(f"bid{bid_info['id']}: \t next bid price is market_price + start_percent = {next_bid_price}")
            return next_bid_price
        elif self.markup_percent >= 0 and self.calculate_value(bid_price, self.markup_percent) < self.calculate_value(market_price, self.finish_percent):
            next_bid_price = self.calculate_value(bid_price, self.markup_percent)
            self.logger.info(f"bid{bid_info['id']}: \t next bid price is bid_price + markup_percent = {next_bid_price}")
            return self.calculate_value(bid_price, self.markup_percent)
        elif self.markup_percent < 0 and self.calculate_value(bid_price, self.markup_percent) > self.calculate_value(market_price, self.finish_percent):
            next_bid_price = self.calculate_value(bid_price, self.markup_percent)
            self.logger.info(f"bid{bid_info['id']}: \t next bid price is bid_price + markup_percent = {next_bid_price}")
            return self.calculate_value(bid_price, self.markup_percent)
        else:
            return None
