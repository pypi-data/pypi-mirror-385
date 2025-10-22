import base64
import hashlib
import os
from datetime import datetime, timedelta, timezone

import bech32
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from nacl.encoding import RawEncoder
from nacl.signing import SigningKey

from ..auth import Auth
from ..logger import logger
from ..orders import Orders


class SUIFunctions:
    def _encode_uleb128(self, value: int) -> bytes:
        """
        Encode integer as ULEB128 (unsigned little-endian base 128)

        Args:
            value: Integer to encode

        Returns:
            ULEB128 encoded bytes
        """
        result = []
        while value >= 0x80:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)

    def _create_sui_signature_message(self, message: str) -> bytes:
        """
        Create the message bytes that need to be signed according to SUI standards

        Args:
            message: The plain text message to sign

        Returns:
            Formatted message bytes for signing
        """
        # Convert message to bytes
        message_bytes = message.encode("utf-8")

        # SUI signature format:
        # - Intent scope (1 byte): 3 for ProofOfPossession
        # - SUI version (1 byte): 0
        # - App ID (1 byte): 0
        # - Message length (ULEB128)
        # - Message bytes

        result = bytearray()
        result.append(3)  # Intent scope: ProofOfPossession
        result.append(0)  # SUI version
        result.append(0)  # App ID
        result.extend(self._encode_uleb128(len(message_bytes)))  # Message length
        result.extend(message_bytes)  # Message

        return bytes(result)

    def sign_message(self, message: str) -> str:
        """
        Sign a message using SUI standards

        Args:
            signing_key: Ed25519 signing key
            message: Message to sign

        Returns:
            Base64 encoded signature in SUI format
        """
        # Create the formatted message for signing
        formatted_message = self._create_sui_signature_message(message)

        # Hash the formatted message with Blake2b-256
        hasher = hashlib.blake2b(digest_size=32)
        hasher.update(formatted_message)
        message_digest = hasher.digest()

        # Sign the hash
        signature_obj = self.parent.auth.signing_key.sign(
            message_digest, encoder=RawEncoder
        )
        signature_bytes = signature_obj.signature  # 64 bytes

        # Get public key
        public_key_bytes = self.parent.auth.signing_key.verify_key.encode()  # 32 bytes

        # SUI signature format: scheme_byte + signature + public_key
        scheme_byte = b"\x00"  # Ed25519 scheme
        sui_signature = scheme_byte + signature_bytes + public_key_bytes

        # Encode as base64
        return base64.b64encode(sui_signature).decode("utf-8")


class SUIAuth(SUIFunctions, Auth):
    """Handle authentication processes, including RSA and Ethereum message signing."""

    def __init__(self, parent, private_key_path="private-key.pem"):
        """
        Initialize the authentication handler.

        Args:
            parent: The parent context or object that holds the Auth instance.
            private_key_path (str): Path to the RSA private key file.
        """
        self.parent = parent
        private_key_hex = decode_bech32_private_key(self.parent.private_key)
        private_key_bytes = bytes.fromhex(private_key_hex)
        self.signing_key = SigningKey(private_key_bytes)
        self.parent.address = self.get_sui_address(self.signing_key.verify_key)
        logger.info(f"SUI Address: {self.parent.address}")

        # self.private_key_path = private_key_path
        # self.private_key = self.load_private_key()

    def request_auth(self):
        """Request a nonce for authentication from the server."""
        credentials = {"ethAddress": self.parent.address}
        return self.parent.post("/auth/requestAuth", json=credentials)

    def get_sui_address(self, verify_key):
        """
        Derive Sui address from public key
        Sui address = first 32 bytes of Blake2b(flag || public_key)
        where flag = 0x00 for Ed25519
        """
        flag = bytes([0x00])  # Ed25519 signature scheme flag
        public_key_bytes = verify_key.encode()

        # Blake2b hash
        h = hashlib.blake2b(flag + public_key_bytes, digest_size=32)
        address_bytes = h.digest()

        # Convert to hex with 0x prefix
        return "0x" + address_bytes.hex()

    def load_private_key(self):
        """
        Load the RSA private key from the specified file.

        Returns:
            The RSA private key or None if the file does not exist.
        """
        if os.path.exists(self.private_key_path):
            with open(self.private_key_path, "rb") as key_file:
                return load_pem_private_key(key_file.read(), password=None)
        return

    def login(self) -> bool:
        """
        Attempt to log in using Ethereum signature-based authentication.

        Returns:
            True if login was successful, False otherwise.
        """
        return self._login_with_signature_method(self.sign_message)

    def _login_with_signature_method(self, sign_method) -> bool:
        """
        Attempt login using a specified signature method.

        Args:
            sign_method: The method to use for signing the authentication message.

        Returns:
            True if login was successful, False otherwise.
        """
        logger.debug("Attempting login...")
        nonce_response = self.request_auth()
        nonce = nonce_response.get("nonce")

        if nonce:
            signature = sign_method(nonce)
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

    def link_address(self, address):
        """Link an address."""
        # if self.parent.chain in [Chains.EVM]:
        #     address = address.lower()

        response = self.parent.post("/linked_wallets/request_link", {"addr": address})
        nonce = response["payload"]
        eth_signature = self.sign_message(nonce)
        confirm_response = self.parent.post(
            "/linked_wallets/confirm_link",
            json={
                "nonce": nonce,
                "signature": eth_signature,
            },
        )
        try:
            return confirm_response
        except KeyError:
            # Handle the error (e.g., log it, return a specific value, etc.)
            error_msg = (
                "Error: 'payload' key not found in the response. "
                "This may indicate that wallet is already linked to the account."
            )
            logger.error(error_msg)
            return None


class SUIOrders(SUIFunctions, Orders):
    def create_order_sign_message(self, order):
        """Get order to be signed."""
        msg = (
            f"""OrderType: LIMIT\n"""
            f"""OrderId: {order["clientOrderId"]}\n"""
            f"""Price: {order["totalNetPrice"]}\n"""
            f"""TimeInForce: {order["timeInForce"]}\n"""
            f"""Address: {order["clientEthAddress"]}\n"""
            f"""SinglePrice: true\n"""
            f"""IocAuctionTime: {order["iocAuctionTime"]}\n"""
        )
        for idx, leg in enumerate(order["legs"]):
            msg += f"Leg{idx}:\n  ContractId: {leg['contractId']}\n  Quantity: {leg['quantity']}\n  Side: {leg['side']}\n"

        return msg

    def sign_order(self, order):
        """Sign Order."""
        message = self.create_order_sign_message(order)
        return self.sign_message(message)

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
        just_order=False,
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

        body["signature"] = self.sign_order(body)
        if just_order:
            return body
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

            body = self.new_order(
                legs=legs,
                price=price,
                client_order_id=client_order_id,
                order_type="LIMIT",
                time_in_force=time_in_force,
                request_single_price=True,
                order_descr=order_descr,
                iocAuctionTime=tif,
                just_order=True,
            )
            payload.append(body)

            # order = {
            #     "clientOrderId": client_order_id,
            #     "totalNetPrice": price if isinstance(price, str) else f"{price:.4f}",
            #     "legs": legs,
            #     "orderType": "LIMIT",
            #     "timeInForce": time_in_force,
            #     "clientEthAddress": self.parent.address.lower(),
            #     "singlePrice": True,
            # }

            # if tif is None:
            #     if order_info.time_in_force == "GOOD_TIL_DATE":
            #         order_expiry = datetime.now(tz=timezone.utc) + timedelta(minutes=3)
            #         order["iocAuctionTime"] = int(order_expiry.timestamp() * 1000)
            #     else:
            #         order["iocAuctionTime"] = "null"
            # else:
            #     order["iocAuctionTime"] = tif

            # body = {
            #     **order,
            #     "orderGenesis": "CLIENT_PREDEFINED",
            #     "orderDescr": order_descr,
            #     "signature": "",
            #     "legs": [
            #         {"contractId": contract_id, "side": side, "quantity": f"{qty:.4f}"}
            #         for contract_id, side, qty in legs
            #     ],
            #     "requestSinglePrice": True,
            # }

            # body["signature"] = self.sign_order(order)
            # del body["singlePrice"]

            # payload.append(body)
        logger.debug(f"[SDK] Client order ids before posting: {client_order_ids}")
        return self.parent.post("/clientapi/newOrders", json=payload)


def decode_bech32_private_key(bech32_key):
    """
    Decode a Sui bech32-encoded private key (suiprivkey1...)

    Args:
        bech32_key: Private key in bech32 format (e.g., suiprivkey1...)

    Returns:
        Hex string of the private key
    """
    if bech32_key is None or not bech32_key.startswith("suiprivkey1"):
        raise ValueError(
            "Invalid Sui private key format. Must start with 'suiprivkey1'"
        )

    # Decode bech32
    hrp, data = bech32.bech32_decode(bech32_key)

    if hrp != "suiprivkey":
        raise ValueError(f"Invalid HRP: expected 'suiprivkey', got '{hrp}'")

    # Convert from 5-bit to 8-bit encoding
    decoded = bech32.convertbits(data, 5, 8, False)

    if not decoded:
        raise ValueError("Failed to decode bech32 data")

    # First byte is the flag (0x00 for Ed25519), rest is the private key
    key_bytes = bytes(decoded[1:])  # Skip the flag byte

    return key_bytes.hex()
