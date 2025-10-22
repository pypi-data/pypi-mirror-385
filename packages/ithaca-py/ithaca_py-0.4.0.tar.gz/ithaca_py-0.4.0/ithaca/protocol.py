"""Protocol Module."""

from datetime import datetime, timedelta

import pandas as pd


class Protocol:
    """Protocol Class."""

    def __init__(self, parent):
        """Class constructor."""
        self.parent = parent

    def system_info(self):
        """Get System Info."""
        return self.parent.post("/clientapi/systemInfo")

    def next_auction(self):
        """Get next auctions."""
        return self.parent.post("/clientapi/nextAuction")

    def contract_list(self, flat=False):
        """Get contract list."""
        contracts = self.parent.post("/clientapi/contractList")

        def parse_economics(row):
            return (
                row["currencyPair"],
                row["expiry"],
                row["priceCurrency"],
                row["qtyCurrency"],
                row.get("strike"),
            )

        if flat:
            return [
                [x["contractId"], x["payoff"], *parse_economics(x["economics"])]
                for x in contracts.get("payload")
            ]
        return contracts

    def contract_list_df(self):
        """Get contract list as DataFrame."""
        contracts = self.contract_list(True)
        flds = ["contract_id", "payoff", "pair", "expiry", "quote", "base", "strike"]
        df = (
            pd.DataFrame(contracts, columns=flds)
            .set_index("contract_id")
            .drop(columns=["quote", "base"])
        )
        df["expiry"] = df["expiry"].apply(
            lambda x: datetime.strptime(str(x), "%y%m%d%H%M")
        )
        return df

    def contract_list_by_ids(self, ids):
        """Get contract list by Id."""
        body = {"ids": ids}
        return self.parent.post("/clientapi/contractListByIds", json=body)

    def find_contract(self, payoff, expiry, strike=None):
        """Find contract Id."""
        contracts = self.contract_list(flat=True)
        if isinstance(expiry, str):
            dt = datetime.strptime(expiry, "%Y-%m-%d")
            expiry = int(dt.strftime("%y%m%d%H%M")[:-3] + "80")

        for contract in contracts:
            if contract[1] == payoff and contract[3] == expiry:
                if strike is None or contract[6] == strike:
                    return contract[0]
        return None

    def historical_contracts(self, expiry):
        """Get historical contracts."""
        body = {"expiry": expiry}
        return self.parent.post("/clientapi/historicalContracts", json=body)

    def orderbook(self):
        """Get orderbook if flagged as MARKET_MAKER"""
        return self.parent.post("/clientapi/orderbook")

    def get_next_expiries(self, num: int = 4, min_days: int = 5, anchor=None):
        """Get next n expiries in contracts"""
        if anchor is None:
            anchor = datetime.now()
        contracts = self.contract_list(True)
        vanillas = filter(lambda row: row[1] in ["Call", "Put"], contracts)
        expiries = {row[3] for row in vanillas}
        expiry_dates = [datetime.strptime(str(exp), "%y%m%d%H%M") for exp in expiries]
        expiry_dates.sort()
        fridays = filter(
            lambda date: date.weekday() == 4 and (date - anchor).days >= min_days,
            expiry_dates,
        )
        return list(fridays)[:num]
