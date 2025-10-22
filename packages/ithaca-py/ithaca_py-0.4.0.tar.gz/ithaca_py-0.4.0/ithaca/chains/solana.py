from datetime import datetime, timedelta, timezone

import base58
import solders

from ..auth import Auth
from ..logger import logger
from ..orders import Orders


class SolanaAuth(Auth):
    """Handle authentication processes, message signing."""

    def __init__(self, parent, private_key: str):
        """
        Initialize the authentication handler.

        Args:
            parent: The parent context or object that holds the Auth instance.
            private_key (str): base58 private key.
        """
        self.parent = parent
        self.private_key = private_key
        self.keypair = solders.keypair.Keypair.from_base58_string(private_key)
        self.parent.address = str(self.keypair.pubkey())
        self.parent.account = self.keypair

    def request_auth(self):
        """Request a nonce for authentication from the server."""
        credentials = {"ethAddress": str(self.keypair.pubkey())}
        return self.parent.post("/auth/requestAuth", json=credentials)

    def sign_message(self, message: str):
        """Sign the nonce with the private key."""

        signature = self.keypair.sign_message(bytes(message.encode()))
        signature_base58 = base58.b58encode(signature.to_bytes()).decode("utf-8")
        return signature_base58

    def login(self) -> bool:
        """
        Attempt to log in using Ethereum signature-based authentication.

        Returns:
            True if login was successful, False otherwise.
        """
        logger.debug("Attempting login...")
        nonce_response = self.request_auth()
        nonce = nonce_response.get("nonce")
        if nonce:
            logger.debug("Received nonce")
            signature = self.sign_message(nonce)
            auth_response = self.parent.post(
                "/auth/validateAuth", json={"nonce": nonce, "signature": signature}
            )
            if "payload" in auth_response:
                self.parent.user = auth_response["payload"]
                logger.debug("Login successful.")
                return True
            else:
                logger.debug("Login failed. No payload in auth response.")
        else:
            logger.debug("Login failed. No nonce received.")

        return False


class SolanaOrders(Orders):
    def sign_order(self, order):
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
            "clientEthAddress": self.parent.address,
            "iocAuctionTime": iocAuctionTime or "null",
            "singlePrice": request_single_price,
        }

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

        del body["singlePrice"]

        body["signature"] = self.sign_order_solana(body)

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
                "clientEthAddress": self.parent.address,
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

            del body["singlePrice"]
            body["signature"] = self.sign_order_solana(body)

            payload.append(body)
        logger.debug(f"[SDK] Client order ids before posting: {client_order_ids}")
        return self.parent.post("/clientapi/newOrders", json=payload)

    def open_orders_with_lock_info(self, currency_pair=None):
        """Return open orders with lock info."""
        if currency_pair is None:
            currency_pair = "WSOL/USDC"

        return self.parent.post(
            f"/clientapi/clientOpenOrdersWithLockInfo?currencyPair={currency_pair}"
        )

    def create_order_sign_message(self, order, is_api=False):
        """Get order to be signed."""
        if is_api:
            endpoint = "/clientapi/createOrderSignMessage"
            res = self.parent.post(endpoint, json=order)
            try:
                return res.get("payload")
            except:
                return res
        else:
            msg = (
                f"""OrderType: LIMIT\n"""
                f"""OrderId: {order['clientOrderId']}\n"""
                f"""Price: {order['totalNetPrice']}\n"""
                f"""TimeInForce: {order['timeInForce']}\n"""
                f"""Address: {order['clientEthAddress']}\n"""
                f"""SinglePrice: {str(order['requestSinglePrice']).lower()}\n"""
                f"""IocAuctionTime: {order['iocAuctionTime']}\n"""
            )
            for idx, leg in enumerate(order["legs"]):
                msg += f"Leg{idx}:\n  ContractId: {leg['contractId']}\n  Quantity: {leg['quantity']}\n  Side: {leg['side']}\n"

            return msg
