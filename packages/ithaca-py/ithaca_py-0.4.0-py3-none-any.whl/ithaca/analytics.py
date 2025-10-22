"""Analytics Module."""

from datetime import datetime, timedelta, timezone


class Analytics:
    """Analytics class."""

    def __init__(self, parent):
        """Class constructor."""
        self.parent = parent

    def __date_range(self, since, to, since_lag=30, to_lag=0):
        now = datetime.now().astimezone(timezone.utc)
        return {
            "dateRange": {
                "from": since or (now - timedelta(days=since_lag)).strftime("%Y-%m-%d"),
                "to": to or (now + timedelta(days=to_lag)).strftime("%Y-%m-%d"),
            }
        }

    def best_prices(self):
        """Get best bid and best ask in order list.

        POST  api/v1/clientapi/bestBidAsk
        """
        return self.parent.post("/clientapi/bestBidAsk")

    def best_prices_precise(self):
        """Get best bid and best ask in order list.

        POST  api/v1/clientapi/bestBidAskPrecise
        """
        return self.parent.post("/clientapi/bestBidAskPrecise")

    def total_trading_volume(
        self,
        underlier="WETH",
        numeraire="USDC",
    ):
        """Get total trading volume.

        GET  api/v1/analytics/{underlier}/{numeraire}/totalTradingVolume
        """
        return self.parent.get(f"/analytics/{underlier}/{numeraire}/totalTradingVolume")

    def total_contracts_traded(
        self,
        underlier="WETH",
        numeraire="USDC",
    ):
        """Get total contracts traded.

        GET  /api/v1/analytics/{underlier}/{numeraire}/totalContractsTraded
        """
        return self.parent.get(f"/analytics/{underlier}/{numeraire}/totalContractsTraded")

    def total_open_interest(
        self,
        underlier="WETH",
        numeraire="USDC",
    ):
        """Get total open interest.

        GET  /api/v1/analytics/{underlier}/{numeraire}/totalOpenInterest
        """
        return self.parent.get(f"/analytics/{underlier}/{numeraire}/totalOpenInterest")

    def total_value_locked(
        self,
        underlier="WETH",
        numeraire="USDC",
    ):
        """Get total value locked.

        GET  /api/v1/analytics/{underlier}/{numeraire}/totalValueLocked
        """
        return self.parent.get(f"/analytics/{underlier}/{numeraire}/totalValueLocked")

    def trades(
        self,
        since=None,
        to=None,
        underlier="WETH",
        numeraire="USDC",
    ):
        """Get trades.
        POST  /api/v1/analytics/{underlier}/{numeraire}/trades
        """
        payload = self.__date_range(since, to)
        return self.parent.post(
            f"/analytics/{underlier}/{numeraire}/trades",
            payload
        )

    def open_interest_by_product(
        self,
        since=None,
        to=None,
        to_lag=60,
        underlier="WETH",
        numeraire="USDC",
    ):
        """Get open interest by product.

        POST  /api/v1/analytics/{underlier}/{numeraire}/openInterestByProduct
        """
        payload = self.__date_range(since, to, to_lag=to_lag)
        return self.parent.post(
            f"/analytics/{underlier}/{numeraire}/openInterestByProduct",
            payload
        )

    def open_interest_by_strike(
        self,
        since=None,
        to=None,
        to_lag=60,
        underlier="WETH",
        numeraire="USDC",
    ):
        """Get open interest by strike.

        POST  /api/v1/analytics/{underlier}/{numeraire}/openInterestByStrike
        """
        date_range = self.__date_range(since, to, to_lag=to_lag)

        payload = {**date_range, "strikeRange": {"from": 1, "to": 2500000000000}}
        return self.parent.post(
            f"/analytics/{underlier}/{numeraire}/openInterestByStrike",
            payload
        )

    def daily_volume(
        self,
        since=None,
        to=None,
        since_lag=30,
        underlier="WETH",
        numeraire="USDC",
    ):
        """Get daily volume.

        POST  /api/v1/analytics/{underlier}/{numeraire}/dailyVolume
        """
        date_range = self.__date_range(since, to, since_lag=since_lag)
        payload = {**date_range}
        return self.parent.post(
            f"/analytics/{underlier}/{numeraire}/dailyVolume",
            payload
        )

    def all(self,
        since=None,
        to=None,
        underlier="WETH",
        numeraire="USDC",
    ):
        """Get analytics."""
        return {
            "totalTradingVolume": self.total_trading_volume(underlier, numeraire),
            "totalContractsTraded": self.total_contracts_traded(underlier, numeraire),
            "totalOpenInterest": self.total_open_interest(underlier, numeraire),
            "totalValueLocked": self.total_value_locked(underlier, numeraire),
            "trades": self.trades(since, to, underlier, numeraire),
            "openInterestByProduct": self.open_interest_by_product(
                since, to, 60, underlier, numeraire
            ),
            "openInterestByStrike": self.open_interest_by_strike(
                since, to, 60, underlier, numeraire
            ),
            "dailyVolume": self.daily_volume(
                since, to, 30, underlier, numeraire
            ),
        }