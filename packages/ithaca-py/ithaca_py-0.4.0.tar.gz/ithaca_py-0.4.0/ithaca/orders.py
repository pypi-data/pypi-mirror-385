"""Orders Module."""

from collections import namedtuple
from datetime import datetime, timedelta, timezone

import base58

from .logger import logger


class Orders:
    """Orders class."""

    TIME_IN_FORCE_OPTIONS = [
        "DAY",
        "GOOD_TILL_CANCEL",
        "IMMEDIATE_OR_CANCEL",
        "GOOD_TILL_DATE",
        "AT_AUCTION_ONLY",
    ]
    OrderInfo = namedtuple(
        "OrderInfo",
        "legs price time_in_force order_descr client_order_id",
        defaults=("GOOD_TILL_CANCEL", "", None),
    )

    def __init__(self, parent):
        """Class constructor."""
        self.parent = parent

    def create_client_order_id(self, value=101) -> int:
        """Create a 'random' client order id."""
        return int(
            (datetime.now().astimezone(timezone.utc).timestamp() * 2**10 + value) * 1000
        )

    def sign_order(self, order):
        """Sign Order."""
        raw_order = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                ],
                "ConditionalOrder": [
                    {"name": "orderType", "type": "string"},
                    {"name": "orderId", "type": "uint64"},
                    {"name": "price", "type": "string"},
                    {"name": "timeInForce", "type": "string"},
                    {"name": "address", "type": "string"},
                    {"name": "singlePrice", "type": "bool"},
                    {"name": "iocAuctionTime", "type": "uint64"},
                ],
                "Leg": [
                    {"name": "contractId", "type": "uint32"},
                    {"name": "side", "type": "string"},
                    {"name": "quantity", "type": "string"},
                ],
            },
            "primaryType": "ConditionalOrder",
            "domain": {
                "name": "Ithaca",
                "version": "0.1",
            },
            "message": {
                "orderType": order.get("orderType"),
                "orderId": order.get("clientOrderId"),
                "price": order.get("totalNetPrice"),
                "timeInForce": order.get("timeInForce"),
                "address": order.get("clientEthAddress"),
                "singlePrice": order.get("singlePrice"),
                "iocAuctionTime": order.get("iocAuctionTime"),
            },
        }
        if order.get("iocAuctionTime") is None:
            del raw_order["message"]["iocAuctionTime"]
            conditional_order = raw_order["types"]["ConditionalOrder"]
            raw_order["types"]["ConditionalOrder"] = [
                field
                for field in conditional_order
                if field.get("name") != "iocAuctionTime"
            ]

        for idx, (contract_id, side, qty) in enumerate(order.get("legs")):
            raw_order["types"]["ConditionalOrder"].append(
                {"name": f"leg{idx}", "type": "Leg"},
            )
            raw_order["message"][f"leg{idx}"] = {
                "contractId": contract_id,
                "side": side,
                "quantity": f"{qty:.4f}",
            }
        return self.parent.auth.sign_message(raw_order)

    def sign_order_solana(self, order):
        """Sign Order."""
        message = self.create_order_sign_message(order)
        signature = self.parent.account.sign_message(bytes(message.encode("utf8")))
        signature_base58 = base58.b58encode(signature.to_bytes()).decode("utf-8")

        return signature_base58

    def new_order(
        self,
        legs,
        price,
        client_order_id=None,
        order_type="LIMIT",
        time_in_force="GOOD_TILL_CANCEL",
        request_single_price=True,
        order_descr="",
        iocAuctionTime=None,
    ):
        """Send new order request to Ithaca backend.

        Args:
            legs (list): list of legs as
                     (contractId: int, side: 'BUY' | 'SELL', quantity: float)
            price (float): Order limit for the conditional order
            order_type (str, optional): Order type. Defaults to "LIMIT".
            time_in_force (str, optional): Time in force.
                                         Defaults to "GOOD_TILL_CANCEL".
            order_descr (str, optional): Order description. Defaults to "".

        Example:
            legs: [(5559, "SELL", 1), (5563, "BUY", 1)]

        Returns:
            json: {'result': 'OK', 'details': '', 'clientOrderId': 1742473240341423}
        """
        legs = sorted(legs, key=lambda x: x[0])
        if client_order_id is None:
            client_order_id = self.create_client_order_id()

        order = {
            "clientOrderId": client_order_id,
            "totalNetPrice": price if isinstance(price, str) else f"{price:.4f}",
            "legs": legs,
            "orderType": order_type,
            "timeInForce": time_in_force,
            "clientEthAddress": self.parent.address.lower(),
            "iocAuctionTime": iocAuctionTime or "null",
            "singlePrice": request_single_price,
        }
        if iocAuctionTime is None:
            del order["iocAuctionTime"]

        body = {
            **order,
            "orderGenesis": "CLIENT_PREDEFINED",
            "orderDescr": order_descr,
            "signature": "",
            "legs": [
                {"contractId": contract_id, "side": side, "quantity": f"{qty:.4f}"}
                for contract_id, side, qty in legs
            ],
            "requestSinglePrice": request_single_price,
        }

        body["signature"] = self.sign_order(order)
        del body["singlePrice"]

        res = self.parent.post("/clientapi/newOrder", json=body)

        try:
            return {**res, "clientOrderId": client_order_id}
        except TypeError:
            return {"result": "ERROR", "clientOrderId": client_order_id}

    def new_orders(self, orders, tif=None):
        """Send new orders request to Ithaca backend."""
        logger.debug("[SDK] Running new_orders method")
        payload = []
        client_order_ids = []
        for order_info in orders:
            order_info = self.OrderInfo(*order_info)
            if tif is not None:
                order_info = order_info._replace(time_in_force="GOOD_TILL_DATE")
            time_in_force = (
                order_info.time_in_force
                if self._is_time_in_force_valid(order_info.time_in_force)
                else "GOOD_TILL_CANCEL"
            )
            legs = sorted(order_info.legs, key=lambda x: x[0])
            price = order_info.price
            if not order_info.client_order_id:
                logger.debug(
                    f"[SDK] Client order id is empty for order: {order_info}. Creating new client order id."
                )
            client_order_id = (
                order_info.client_order_id
                if order_info.client_order_id
                else self.create_client_order_id()
            )
            client_order_ids.append(client_order_id)
            order_descr = order_info.order_descr

            order = {
                "clientOrderId": client_order_id,
                "totalNetPrice": price if isinstance(price, str) else f"{price:.4f}",
                "legs": legs,
                "orderType": "LIMIT",
                "timeInForce": time_in_force,
                "clientEthAddress": self.parent.address.lower(),
                "singlePrice": True,
            }

            if tif is None:
                if order_info.time_in_force == "GOOD_TIL_DATE":
                    order_expiry = datetime.now(tz=timezone.utc) + timedelta(minutes=3)
                    order["iocAuctionTime"] = int(order_expiry.timestamp() * 1000)
                else:
                    order["iocAuctionTime"] = "null"
            else:
                order["iocAuctionTime"] = tif

            body = {
                **order,
                "orderGenesis": "CLIENT_PREDEFINED",
                "orderDescr": order_descr,
                "signature": "",
                "legs": [
                    {"contractId": contract_id, "side": side, "quantity": f"{qty:.4f}"}
                    for contract_id, side, qty in legs
                ],
                "requestSinglePrice": True,
            }

            body["signature"] = self.sign_order(order)
            del body["singlePrice"]

            payload.append(body)
        logger.debug(f"[SDK] Client order ids before posting: {client_order_ids}")
        return self.parent.post("/clientapi/newOrders", json=payload)

    def open_orders(self):
        """Return open orders."""
        return self.parent.post("/clientapi/clientOpenOrders")

    def open_orders_with_lock_info(self, currency_pair=None):
        """Return open orders with lock info."""
        if currency_pair is None:
            currency_pair = "WETH/USDC"

        return self.parent.post(
            f"/clientapi/clientOpenOrdersWithLockInfo?currencyPair={currency_pair}"
        )

    def order_status(self, client_order_id):
        """Get order status."""
        body = {"clientOrderId": client_order_id}
        return self.parent.post("/clientapi/orderStatus", json=body)

    def order_cancel(self, client_order_id):
        """Cancel an order."""
        body = {
            "clientOrderId": client_order_id,
        }
        return self.parent.post("/clientapi/orderCancel", json=body)

    def order_cancel_all(self, contains=None):
        """Cancel all orders, with optional filter."""
        endpoint = "/clientapi/allOrdersCancel"
        if contains:
            endpoint += f"?contains={contains}"
        return self.parent.post(endpoint).get("payload")

    def _is_time_in_force_valid(self, value):
        if value in self.TIME_IN_FORCE_OPTIONS:
            return True
        return False
