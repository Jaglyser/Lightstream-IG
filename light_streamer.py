import pandas as pd
import logging
from time_frame import TimeFrame
from trading_ig import IGService, IGStreamService
from trading_ig.config import config
from trading_ig.lightstreamer import Subscription


class LightStreamer:
    def __init__(self, epic: list, timeFrame) -> None:
        self.connection = IGService(
            config.username, config.password, config.api_key, config.acc_type)
        self.stream = IGStreamService(self.connection)
        self.session = self.stream.create_session()
        self.accounts = self.session[u"accounts"]
        self.accountId = None
        self.epic = epic
        self.timeFrame = timeFrame
        self.timeObject = TimeFrame(self.timeFrame)
        self.counter = False

    async def init(self):
        accountId = await self.accountHandler()
        if(accountId == None):
            print("No account found")
            return
        self.accountId = accountId
        self.stream.connect(self.accountId)
        # Making a new Subscription in MERGE mode
        subscriptionPrices = Subscription(
            mode="MERGE",
            items=self.epic,
            fields=["UPDATE_TIME", "BID", "OFFER",
                    "CHANGE", "MARKET_STATE"],
        )
        # adapter="QUOTE_ADAPTER")

        # Adding the "on_price_update" function to Subscription
        subscriptionPrices.addlistener(self.onPriceUpdate)

        # Registering the Subscription
        subKeyPrices = self.stream.ls_client.subscribe(
            subscriptionPrices)

        # Making an other Subscription in MERGE mode
        subscriptionAccount = Subscription(
            mode="MERGE", items=["ACCOUNT:" + accountId], fields=["AVAILABLE_CASH"],
        )
        #    #adapter="QUOTE_ADAPTER")

        # Adding the "on_balance_update" function to Subscription
        subscriptionAccount.addlistener(self.onAccountUpdate)

        # Registering the Subscription
        subKeyAccount = self.stream.ls_client.subscribe(
            subscriptionAccount)

        input(
            "{0:-^80}\n".format(
                "HIT CR TO UNSUBSCRIBE AND DISCONNECT FROM \
        LIGHTSTREAMER"
            )
        )

        # Disconnecting
        self.stream.disconnect()

    # A simple function acting as a Subscription listener

    def onPriceUpdate(self, item_update):
        # print("price: %s " % item_update)
        """
        print(
            "{stock_name:<19}: Time {UPDATE_TIME:<8} - "
            "Bid {BID:>5} - Ask {OFFER:>5}".format(
                stock_name=item_update["name"], **item_update["values"]
            )
        )"""

        df = pd.DataFrame(data=item_update)
        offer = df.loc['OFFER', :]
        bid = df.loc['BID', :]
        updateTime = df.loc['UPDATE_TIME', :]
        #print("Price: ", offer['values'], end=" ")
        #print("Time: ", update_time['values'])
        self.counter = self.timeObject.counter(updateTime)
        if(self.counter):
            print("a %d has passed" % self.timeFrame)

    def onAccountUpdate(balance_update):
        print("balance: %s " % balance_update)

    # function to open position
    async def accountHandler(self):
        for account in self.accounts:
            if account[u"accountId"] == config.acc_number:
                accountId = account[u"accountId"]
                return accountId
            else:
                print("Account not found: {0}".format(config.acc_number))
                return

    def open_position(self, direction):
        response = self.stream.create_open_position(
            currency_code="EUR",
            direction=direction,
            # epic is a list containing subscription objects from IGs rest api
            epic=self.epic[0],
            expiry="-",
            force_open="false",
            guaranteed_stop="false",
            level=None,
            limit_distance=None,
            limit_level=None,
            order_type="MARKET",
            size="1",
            quote_id=None,
            stop_distance=None,
            stop_level=None,
            trailing_stop_increment=None,
            trailing_stop='false')
