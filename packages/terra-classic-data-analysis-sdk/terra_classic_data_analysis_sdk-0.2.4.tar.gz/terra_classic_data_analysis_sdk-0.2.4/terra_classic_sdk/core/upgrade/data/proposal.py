"""Upgrade module data objects."""

from __future__ import annotations

__all__ = ["SoftwareUpgradeProposal", "CancelSoftwareUpgradeProposal"]

from typing import Optional

import attr
from terra_classic_sdk.core import AccAddress, Coins
from betterproto.lib.google.protobuf import Any as Any_pb
from terra_proto.cosmos.upgrade.v1beta1 import (
    CancelSoftwareUpgradeProposal as CancelSoftwareUpgradeProposal_pb,
)
from terra_proto.cosmos.upgrade.v1beta1 import (
    SoftwareUpgradeProposal as SoftwareUpgradeProposal_pb,
)

from terra_classic_sdk.core.upgrade.plan import Plan
from terra_classic_sdk.util.json import JSONSerializable


@attr.s
class SoftwareUpgradeProposal(JSONSerializable):
    authority:AccAddress=attr.ib()
    plan: Optional[Plan] = attr.ib()

    type_amino = "upgrade/SoftwareUpgradeProposal"
    """"""
    type_url = "/cosmos.upgrade.v1beta1.MsgSoftwareUpgrade"
    """"""

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "plan": self.plan.to_amino() if self.plan else None,
                "authority": self.authority,
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> SoftwareUpgradeProposal:
        return cls(
            authority=data["authority"],
            plan=Plan.from_data(data["plan"]) if data.get("plan") else None,
        )

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "authority":self.authority,
            "plan": self.plan.to_data() if self.plan else None,
        }

    def to_proto(self) -> SoftwareUpgradeProposal_pb:
        return SoftwareUpgradeProposal_pb(
            authority=self.authority,
            plan=(self.plan.to_proto() if self.plan else None),
        )

    def pack_any(self) -> Any_pb:
        return Any_pb(type_url=self.type_url, value=bytes(self.to_proto()))

    @classmethod
    def from_proto(cls, proto: SoftwareUpgradeProposal_pb) -> SoftwareUpgradeProposal:
        return cls(
            authority=proto.authority,
            plan=Plan.from_proto(proto.plan) if proto.plan else None,
        )


@attr.s
class CancelSoftwareUpgradeProposal(JSONSerializable):
    title: str = attr.ib()
    description: str = attr.ib()

    type_amino = "upgrade/CancelSoftwareUpgradeProposal"
    """"""
    type_url = "/cosmos.upgrade.v1beta1.CancelSoftwareUpgradeProposal"
    """"""

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "title": self.title,
                "description": self.description,
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> CancelSoftwareUpgradeProposal:
        return cls(title=data["title"], description=data["description"])

    def to_proto(self) -> CancelSoftwareUpgradeProposal_pb:
        return CancelSoftwareUpgradeProposal_pb(
            title=self.title, description=self.description
        )

    def pack_any(self) -> Any_pb:
        return Any_pb(type_url=self.type_url, value=bytes(self.to_proto()))

    @classmethod
    def from_proto(cls, proto: CancelSoftwareUpgradeProposal_pb) -> CancelSoftwareUpgradeProposal:
        return cls(title=proto.title, description=proto.description)

