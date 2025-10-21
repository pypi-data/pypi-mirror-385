"""Oracle module messages."""

from __future__ import annotations

import hashlib

import attr
from terra_proto.terra.oracle.v1beta1 import (
    MsgAggregateExchangeRatePrevote as MsgAggregateExchangeRatePrevote_pb,
)
from terra_proto.terra.oracle.v1beta1 import (
    MsgAggregateExchangeRateVote as MsgAggregateExchangeRateVote_pb,
)
from terra_proto.terra.oracle.v1beta1 import (
    MsgDelegateFeedConsent as MsgDelegateFeedConsent_pb,
)

from terra_classic_sdk.core import AccAddress, Coins, Dec, ValAddress
from terra_classic_sdk.core.msg import Msg

__all__ = [
    "vote_hash",
    "aggregate_vote_hash",
    "MsgDelegateFeedConsent",
    "MsgAggregateExchangeRatePrevote",
    "MsgAggregateExchangeRateVote",
]


def vote_hash(denom: str, exchange_rate: Dec, salt: str, validator: str) -> str:
    """Calculates vote hash for submitting :class:`MsgExchangeRatePrevote`.

    Args:
        denom (str): denom to vote for
        exchange_rate (Dec): exchange rate of LUNA
        salt (str): salt
        validator (str): validator operator address

    Returns:
        str: vote hash
    """
    payload = f"{denom}:{exchange_rate!s}:{salt}:{validator}"
    sha_hash = hashlib.sha256(payload.encode())
    return sha_hash.hexdigest()[:40]


def aggregate_vote_hash(salt: str, exchange_rates: Coins.Input, validator: str) -> str:
    """Calculates aggregate vote hash for submitting :class:`MsgAggregateExchangeRatePrevote`.

    Args:
        salt (str): salt
        exchange_rates (Coins.Input): exchange rates in various denominations
        validator (str): validator operator address

    Returns:
        str: aggregate vote hash
    """
    payload = f"{salt}:{str(Coins(exchange_rates))}:{validator}"
    sha_hash = hashlib.sha256(payload.encode())
    return sha_hash.hexdigest()[:40]


@attr.s
class MsgDelegateFeedConsent(Msg):
    """Re-assign oracle feeder account for a validator.

    Args:
        operator: validator to change feeder for
        delegate: new feeder address
    """

    type_amino = "oracle/MsgDelegateFeedConsent"
    """"""
    type_url = "/terra.oracle.v1beta1.MsgDelegateFeedConsent"
    """"""
    action = "delegatefeeder"
    """"""
    prototype = MsgDelegateFeedConsent_pb
    """"""

    operator: ValAddress = attr.ib()
    delegate: AccAddress = attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {"operator": self.operator, "delegate": self.delegate},
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgDelegateFeedConsent:
        return cls(operator=data["operator"], delegate=data["delegate"])

    def to_proto(self) -> MsgDelegateFeedConsent_pb:
        return MsgDelegateFeedConsent_pb(operator=self.operator, delegate=self.delegate)

    @classmethod
    def from_proto(cls, proto: MsgDelegateFeedConsent_pb) -> MsgDelegateFeedConsent:
        return cls(operator=proto.operator, delegate=proto.delegate)


@attr.s
class MsgAggregateExchangeRatePrevote(Msg):
    """Submit an aggregate vote for the current vote period.

    Args:
        hash: aggregate vote hash
        feeder: account submitting the aggregate prevote
        validator: validator to which the aggregate prevote corresponds
    """

    type_amino = "oracle/MsgAggregateExchangeRatePrevote"
    """"""
    type_url = "/terra.oracle.v1beta1.MsgAggregateExchangeRatePrevote"
    """"""
    prototype = MsgAggregateExchangeRatePrevote_pb
    """"""

    hash: str = attr.ib()
    feeder: AccAddress = attr.ib()
    validator: ValAddress = attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "hash": self.hash,
                "feeder": self.feeder,
                "validator": self.validator,
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgAggregateExchangeRatePrevote:
        return cls(
            hash=data["hash"],
            feeder=data["feeder"],
            validator=data["validator"],
        )

    def to_proto(self) -> MsgAggregateExchangeRatePrevote_pb:
        return MsgAggregateExchangeRatePrevote_pb(
            hash=self.hash, feeder=self.feeder, validator=self.validator
        )

    @classmethod
    def from_proto(
        cls, proto: MsgAggregateExchangeRatePrevote_pb
    ) -> MsgAggregateExchangeRatePrevote:
        return cls(
            hash=proto.hash,
            feeder=proto.feeder,
            validator=proto.validator,
        )


@attr.s
class MsgAggregateExchangeRateVote(Msg):
    """Submit an aggregate prevote for the current vote.

    Args:
        exchange_rates (Coins.Input): exchange rates to use
        salt: aggregate vote salt
        feeder: feeder account submitting aggregate prevote
        validator: validator vote corresponds to
    """

    type_amino = "oracle/MsgAggregateExchangeRateVote"
    """"""
    type_url = "/terra.oracle.v1beta1.MsgAggregateExchangeRateVote"
    """"""
    prototype = MsgAggregateExchangeRateVote_pb
    """"""

    exchange_rates: Coins = attr.ib(converter=Coins)
    salt: str = attr.ib()
    feeder: AccAddress = attr.ib()
    validator: ValAddress = attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "exchange_rates": str(self.exchange_rates.to_dec_coins()),
                "salt": self.salt,
                "feeder": self.feeder,
                "validator": self.validator,
            },
        }

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "exchange_rates": self.exchange_rates.to_dec_coins().to_data(),
            "salt": self.salt,
            "feeder": self.feeder,
            "validator": self.validator
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgAggregateExchangeRateVote:
        rates = data.get("exchange_rates")
        if type(rates) is str:
            rates = Coins.from_str(rates)
        else:
            rates = Coins.from_data(rates)
        return cls(
            exchange_rates=rates,
            salt=data.get("salt"),
            feeder=data.get("feeder"),
            validator=data.get("validator"),
        )

    def to_proto(self) -> MsgAggregateExchangeRateVote_pb:
        return MsgAggregateExchangeRateVote_pb(
            exchange_rates=str(self.exchange_rates),
            salt=self.salt,
            feeder=self.feeder,
            validator=self.validator,
        )

    @classmethod
    def from_proto(
        cls, proto: MsgAggregateExchangeRateVote_pb
    ) -> MsgAggregateExchangeRateVote:
        return cls(
            exchange_rates=Coins.from_str(proto.exchange_rates),
            salt=proto.salt,
            feeder=proto.feeder,
            validator=proto.validator,
        )

    def get_aggregate_vote_hash(self) -> str:
        """Vote hash required for message's associated prevote.

        Returns:
            str: aggregate vote hash
        """
        return aggregate_vote_hash(self.salt, self.exchange_rates, self.validator)

    def get_aggregate_prevote(self) -> MsgAggregateExchangeRatePrevote:
        """Generates the associated :class:`MsgAggregateExchangeRatePrevote` object with
        the correct prepopulated fields.

        Returns:
            MsgAggregateExchangeRatePrevote: associated aggregate prevote
        """
        return MsgAggregateExchangeRatePrevote(
            hash=self.get_aggregate_vote_hash(),
            feeder=self.feeder,
            validator=self.validator,
        )
