from .base import create_demux, create_demux_proto, create_demux_unpack_any

# core msgs
from terra_classic_sdk.core.authz import (
    MsgExecAuthorized,
    MsgGrantAuthorization,
    MsgRevokeAuthorization,
)
from terra_classic_sdk.core.bank import MsgMultiSend, MsgSend
from terra_classic_sdk.core.distribution import (
    MsgCommunityPoolSpend,
    MsgFundCommunityPool,
    MsgSetWithdrawAddress,
    MsgWithdrawDelegatorReward,
    MsgWithdrawValidatorCommission,
)
from terra_classic_sdk.core.gov.msgs import MsgDeposit, MsgSubmitProposal, MsgVote, MsgVote_v1beta1, MsgDeposit_v1beta1, \
    MsgSubmitProposal_v1beta1
from terra_classic_sdk.core.ibc.msgs import (
    MsgAcknowledgement,
    MsgChannelCloseConfirm,
    MsgChannelCloseInit,
    MsgChannelOpenAck,
    MsgChannelOpenConfirm,
    MsgChannelOpenInit,
    MsgChannelOpenTry,
    MsgConnectionOpenAck,
    MsgConnectionOpenConfirm,
    MsgConnectionOpenInit,
    MsgConnectionOpenTry,
    MsgCreateClient,
    MsgRecvPacket,
    MsgSubmitMisbehaviour,
    MsgTimeout,
    MsgUpdateClient,
    MsgUpgradeClient,
)
from terra_classic_sdk.core.ibc_transfer import MsgTransfer
from terra_classic_sdk.core.market import MsgSwap, MsgSwapSend
from terra_classic_sdk.core.oracle import (
    MsgAggregateExchangeRatePrevote,
    MsgAggregateExchangeRateVote,
    MsgDelegateFeedConsent,
)
from terra_classic_sdk.core.slashing import MsgUnjail
from terra_classic_sdk.core.staking import (
    MsgBeginRedelegate,
    MsgCreateValidator,
    MsgDelegate,
    MsgEditValidator,
    MsgUndelegate,
    MsgCancelUnbondingDelegation,
)
from terra_classic_sdk.core.wasm import (
    MsgClearAdmin,
    MsgExecuteContract,
    MsgExecuteContract_vbeta1,
    MsgInstantiateContract,
    #MsgMigrateCode,
    MsgMigrateContract,
    MsgStoreCode,
    MsgStoreCode_vbeta1,
    MsgUpdateAdmin,
    MsgInstantiateContract2,
    MsgUpdateContractAdmin

)
from terra_classic_sdk.core.feegrant import (
    MsgGrantAllowance,
    MsgRevokeAllowance
)
from terra_classic_sdk.core.crisis import (
    MsgVerifyInvariant
)

from terra_classic_sdk.core.osmosis import (
    MsgExitPool,
    MsgJoinPool,
    MsgSwapExactAmountIn,
    MsgSwapExactAmountOut,
    MsgJoinSwapExternAmountIn
)

bank_msgs = [MsgSend, MsgMultiSend]
distribution_msgs = [
    MsgCommunityPoolSpend,
    MsgFundCommunityPool,
    MsgSetWithdrawAddress,
    MsgWithdrawDelegatorReward,
    MsgWithdrawValidatorCommission,
]
gov_msgs = [MsgDeposit, MsgSubmitProposal,MsgSubmitProposal_v1beta1, MsgVote,MsgVote_v1beta1,MsgDeposit_v1beta1]
market_msgs = [MsgSwap, MsgSwapSend]
authz_msgs = [
    MsgExecAuthorized,
    MsgGrantAuthorization,
    MsgRevokeAuthorization,
]
oracle_msgs = [
    MsgAggregateExchangeRatePrevote,
    MsgAggregateExchangeRateVote,
    MsgDelegateFeedConsent,
]
slashing_msgs = [MsgUnjail]
staking_msgs = [
    MsgBeginRedelegate,
    MsgCreateValidator,
    MsgDelegate,
    MsgEditValidator,
    MsgUndelegate,
    MsgCancelUnbondingDelegation,
]
wasm_msgs = [
    MsgStoreCode,
    MsgStoreCode_vbeta1,
    #MsgMigrateCode,
    MsgInstantiateContract,
    MsgExecuteContract,
    MsgExecuteContract_vbeta1,
    MsgMigrateContract,
    MsgUpdateAdmin,
    MsgClearAdmin,
    MsgInstantiateContract2,
    MsgUpdateContractAdmin

]
feegrant_msgs = [
    MsgGrantAllowance,
    MsgRevokeAllowance
]

ibc_transfer_msgs = [MsgTransfer]
ibc_msgs = [
    MsgCreateClient,
    MsgUpdateClient,
    MsgUpgradeClient,
    MsgSubmitMisbehaviour,
    MsgConnectionOpenInit,
    MsgConnectionOpenTry,
    MsgConnectionOpenAck,
    MsgConnectionOpenConfirm,
    MsgChannelOpenInit,
    MsgChannelOpenTry,
    MsgChannelOpenAck,
    MsgChannelOpenConfirm,
    MsgChannelCloseInit,
    MsgChannelCloseConfirm,
    MsgRecvPacket,
    MsgTimeout,
    MsgAcknowledgement,
]
crisis_msgs = [
    MsgVerifyInvariant
]

osmosis_msgs = [
    MsgExitPool,
    MsgJoinPool,
    MsgJoinSwapExternAmountIn,
    MsgSwapExactAmountIn,
    MsgSwapExactAmountOut
]

parse_msg = create_demux(
    [
        *authz_msgs,
        *bank_msgs,
        *distribution_msgs,
        *feegrant_msgs,
        *gov_msgs,
        *market_msgs,
        *oracle_msgs,
        *slashing_msgs,
        *staking_msgs,
        *wasm_msgs,
        *ibc_msgs,
        *ibc_transfer_msgs,
        *crisis_msgs,
        *osmosis_msgs
    ]
)

parse_proto = create_demux_proto(
    [
        *authz_msgs,
        *bank_msgs,
        *distribution_msgs,
        *feegrant_msgs,
        *gov_msgs,
        *market_msgs,
        *oracle_msgs,
        *slashing_msgs,
        *staking_msgs,
        *wasm_msgs,
        *ibc_msgs,
        *ibc_transfer_msgs,
        *crisis_msgs,
        *osmosis_msgs
    ]
)


parse_unpack_any = create_demux_unpack_any(
    [
        *authz_msgs,
        *bank_msgs,
        *distribution_msgs,
        *feegrant_msgs,
        *gov_msgs,
        *market_msgs,
        *oracle_msgs,
        *slashing_msgs,
        *staking_msgs,
        *wasm_msgs,
        *ibc_msgs,
        *ibc_transfer_msgs,
        *crisis_msgs,
        *osmosis_msgs
    ]
)