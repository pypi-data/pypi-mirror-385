"""Client Module."""

from datetime import datetime

import pandas as pd


class Client:
    """Client class."""

    def __init__(self, parent):
        """Class constructor."""
        self.parent = parent

    def fundlock_state(self):
        """Get client fundlock state.

        Returns:
            _type_: _description_
        """
        return self.parent.post("/clientapi/clientFundLockState")

    def positions_lock_state(self):
        """Get client locked positions collateral.

        Returns:
            _type_: _description_
        """
        return self.parent.post("/clientapi/getLockedCollateral")

    def current_positions(self, _filter=None, details=False):
        """Return a list of the clients positions.

        Args:
            filter (_type_, opt.): COMBINE_STRATEGIES | SHOW_ORDERS.
            details (bool, opt.): If True, returns a DF with contract details.

        Returns:
            _type_: _description_
        """
        body = {"filter": _filter}
        res = self.parent.post("/clientapi/clientCurrentPositions", body)
        if not details:
            return res

        positions_payload = res.get("payload", [])
        if not positions_payload:
            return pd.DataFrame()

        df_positions = pd.DataFrame(positions_payload).set_index("contractId")

        contracts = self.parent.protocol.contract_list().get("payload")
        df_contracts = pd.DataFrame(
            [
                {
                    "contractId": x["contractId"],
                    "payoff": x["payoff"],
                    **x["economics"],
                }
                for x in contracts
            ]
        ).set_index("contractId")

        return df_positions.join(df_contracts)

    def current_positions_for_contract(self, contract_id, filter="SHOW_ORDERS"):
        """Get client current positions for a contract.

        Args:
            contract_id (_type_): _description_
            filter (_type_, opt.): [ "NO_DETAILS", "SHOW_ORDERS", "COMBINE_STRATEGIES" ]

        Returns:
            _type_: _description_
        """
        body = {"contractId": contract_id, "filter": filter}
        res = self.parent.post("/clientapi/clientCurrentPositionsForContract", body)
        if res.get("result") == "OK":
            return res.get("payload")
        else:
            return res

    def valued_positions(self, with_risk=False):
        """Get client valued positions
        Args:
            with_risk (bool): If True, adds greeks

        Example:
            [
                {'contractId': 30915,
                'positionsAvgPrice': 205.4615,
                'position': 0.0013,
                'payoff': 'Call',
                'expiry': '2025-02-07',
                'strike': 3100.0,
                'price': 1.1198981428992576,
                'OptionID': 30915,
                'ref_Spot': 2745.31,
                'ref_Forward': 2745.375,
                'ref_Vol': 0.8662318243209297,
                'Price': 1.1198981428992576,
                'Delta': 0.01967636470590903,
                'Gamma': 0.008195928564929603,
                'Vega': 0.08744108547536777,
                'WeightedVega': 0.37394019076403356,
                'Theta': -1.1087103724753562}
            ]

        Returns:
            List[dict]: _description_
        """
        positions_df = self.current_positions(details=True)
        if positions_df.empty:
            return []
        positions = positions_df.reset_index()[
            [
                "contractId",
                "payoff",
                "expiry",
                "strike",
                "positionsQty",
                "positionsAvgPrice",
            ]
        ]
        positions["expiry"] = positions["expiry"].apply(
            lambda x: datetime.strptime(str(x), "%y%m%d%H%M").strftime("%Y-%m-%d")
        )
        positions = positions.rename(columns={"positionsQty": "position"}).to_dict(
            "records"
        )
        prices = self.parent.calc_server.mark_price(positions)

        if with_risk:
            risk = self.parent.calc_server.get_greeks(positions)
            risk_flds = [
                "OptionID",
                "ref_Spot",
                "ref_Forward",
                "ref_Vol",
                "Price",
                "Delta",
                "Gamma",
                "Vega",
                "WeightedVega",
                "Theta",
            ]
            return (
                pd.DataFrame(positions)[["contractId", "positionsAvgPrice", "position"]]
                .merge(pd.DataFrame(prices), on="contractId")
                .merge(
                    pd.DataFrame(risk)[risk_flds],
                    left_on="contractId",
                    right_on="OptionID",
                )
                .to_dict("records")
            )

        return (
            pd.DataFrame(positions)[["contractId", "positionsAvgPrice", "position"]]
            .merge(pd.DataFrame(prices), on="contractId")
            .to_dict("records")
        )

    def trade_history(
        self,
        date_from: int = None,
        date_to: int = None,
        offset: int = None,
        limit: int = None,
        status: str = None,
    ):
        """Get trade history."""
        """date_from/to are timestamps in backend"""
        body = {
            key: value
            for key, value in {
                "from": date_from,
                "to": date_to,
                "offset": offset,
                "limit": limit,
                "status": status,
            }.items()
            if value is not None
        }

        if body:
            return self.parent.post("/clientapi/tradeHistory", json=body)
        else:
            return self.parent.post("/clientapi/tradeHistory")

    def historical_positions(self, expiry, _filter="NO_DETAILS"):
        """Get client historical positions.

        Args:
            expiry (int): Ithaca expiry date.
            filter (_type_, opt.): NO_DETAILS | COMBINE_STRATEGIES | SHOW_ORDERS.

        """
        body = {"expiry": expiry, "filter": _filter}
        return self.parent.post("/clientapi/clientHistoricalPositions", json=body)

    def historical_positions_by_date(self, _from: int, to: int):
        """Get details of client's past positions filtered by period.

        - if from or to is null last 30 days pos. are returned
        - if from-to period is > 90 days, pos. to-90 days to are returned

        Args:
            _from (int): miliseconds from 1970
            to (int): to miliseconds from 1970

        Example:
            {
                'result': 'OK',
                'details': '',
                'payload': {'totalCollateral': {},
                'expiryPrices': {'WETH/USDC': 2257.43},
                'payoff': {},
                'positions': []}
            }

        Returns:
            dict: _description_
        """
        body = {"from": _from, "to": to}
        return self.parent.post(
            "/clientapi/clientHistoricalPositionsByDatePeriod", json=body
        )

    def net_asset_value(self):
        """Get client net asset value."""
        return self.parent.post("/clientapi/netAssetValue")
