from django.db import models
import ccxt
from django_crypto_trading_bot.users.models import User
from ccxt.base.exchange import Exchange


class Account(models.Model):
    """
    API Account
    for an exchange like binance
    """

    EXCHANGES = (("Binance", "binance"),)

    exchange = models.CharField(max_length=250, choices=EXCHANGES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=250)
    secret = models.CharField(max_length=250)
    password = models.CharField(max_length=250, blank=True, null=True)

    def get_client(self) -> Exchange:
        exchange_id = self.exchange
        exchange_class = getattr(ccxt, exchange_id)
        exchange: Exchange = exchange_class(
            {
                "apiKey": self.api_key,
                "secret": self.secret,
                "timeout": 30000,
                "enableRateLimit": True,
            }
        )

        return exchange

    def __str__(self):
        return "{}: {}".format(self.pk, self.user.get_username())


class Currency(models.Model):
    """
    Cryptocurrency
    """

    name = models.CharField(max_length=50, blank=True, null=True)
    short = models.CharField(max_length=50, unique=True)


class Market(models.Model):
    """
    Market model based on https://github.com/ccxt/ccxt/wiki/Manual#market-structure
    """

    base = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="base")
    quote = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="quote")
    active = models.BooleanField(default=True)
    precision_base = models.IntegerField()
    precision_quote = models.IntegerField()
    precision_amount = models.IntegerField()
    precision_price = models.IntegerField()

    @property
    def symbol(self):
        return "{}/{}".format(self.base.short.upper(), self.quote.short.upper())

    @property
    def market_id(self):
        return "{}{}".format(self.base.short.lower(), self.quote.short.lower())

    @property
    def baseId(self):
        return self.base.short.lower()

    @property
    def quoteId(self):
        return self.quote.short.lower()

    def __str__(self) -> str:
        return self.symbol


class Bot(models.Model):
    """
    Trading Bot
    """

    account = models.ForeignKey(Account, on_delete=models.CASCADE)  # API Account
    market = models.ForeignKey(
        Market, on_delete=models.PROTECT
    )  # Cryptomarket like TRX/BNB
    created = models.DateTimeField(auto_now_add=True)
    day_span = models.IntegerField(
        default=30
    )  # how many days will be analysed for new trading order
    min_profit = models.DecimalField(
        max_digits=30, decimal_places=2, default=0.1
    )  # min profit for each trade in percent


class Order(models.Model):
    """
    Order based on https://github.com/ccxt/ccxt/wiki/Manual#order-structure
    """

    status_choice = (("open", "open"), ("closed", "closed"), ("canceled", "canceled"))
    order_type_choice = (("market", "market"), ("limit", "limit"))
    side_choice = (("buy", "buy"), ("sell", "sell"))

    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=255, unique=True)
    timestamp = models.DateTimeField()
    status = models.CharField(max_length=10, choices=status_choice, default="open")
    order_type = models.CharField(max_length=8, choices=order_type_choice)
    side = models.CharField(max_length=4, choices=side_choice)
    price = models.DecimalField(max_digits=30, decimal_places=8)
    amount = models.DecimalField(max_digits=30, decimal_places=8)
    filled = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    fee_currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    fee_cost = models.DecimalField(max_digits=30, decimal_places=8)
    fee_rate = models.DecimalField(
        max_digits=30, decimal_places=8, blank=True, null=True
    )

    def remaining(self) -> str:
        return self.amount - self.filled

    def cost(self) -> str:
        return self.filled * self.price


class Trade(models.Model):
    """
    Trade based on https://github.com/ccxt/ccxt/wiki/Manual#trade-structure
    """

    taker_or_maker_choice = (("market", "market"), ("limit", "limit"))

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    trade_id = models.CharField(max_length=255, unique=True)
    timestamp = models.DateTimeField()
    taker_or_maker = models.CharField(max_length=8, choices=taker_or_maker_choice)
    amount = models.DecimalField(max_digits=30, decimal_places=8)
    fee_currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    fee_cost = models.DecimalField(max_digits=30, decimal_places=8)
    fee_rate = models.DecimalField(
        max_digits=30, decimal_places=8, blank=True, null=True
    )

    def cost(self):
        return self.amount * self.order.price