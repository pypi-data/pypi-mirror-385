# Module Name: strategies/asymetric.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2025 WattleFlow
# License: Apache 2 Licence
# Description: This modul contains asymetric cryptographic strategies classes.

from abc import abstractmethod

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from wattleflow.core import IStrategy


class StrategyBaseRSA(IStrategy):
    def __init__(self, private_key: RSAPrivateKey):
        self.private_key = private_key

    @abstractmethod
    def execute(self, value: str):
        pass


class StrategyRSAEncrypt256(StrategyBaseRSA):
    def execute(self, value: str):
        public_key = self.private_key.public_key()
        return public_key.encrypt(
            value.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )


class StrategyRSADecrypt256(StrategyBaseRSA):
    def execute(self, value: str):
        return self.private_key.decrypt(
            value,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        ).decode("utf-8")


class StrategyRSAEncrypt512(StrategyBaseRSA):
    def execute(self, value: str):
        public_key = self.private_key.public_key()
        return public_key.encrypt(
            value.encode("utf-8"),
            padding.OAEP(
                # mgf=padding.MGF1(algorithm=hashes.SHA256()),
                mgf=padding.MGF1(algorithm=hashes.SHA512()),
                algorithm=hashes.SHA512(),
                # algorithm=hashes.SHA256(),
                label=None,
            ),
        )


class StrategyRSADecrypt512(StrategyBaseRSA):
    def execute(self, value: str):
        return self.private_key.decrypt(
            value,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA512()),
                algorithm=hashes.SHA512(),
                label=None,
            ),
        ).decode("utf-8")
