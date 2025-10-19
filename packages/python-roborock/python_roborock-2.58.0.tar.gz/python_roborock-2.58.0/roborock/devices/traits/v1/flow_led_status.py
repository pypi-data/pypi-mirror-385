from roborock.containers import FlowLedStatus
from roborock.devices.traits.v1 import common
from roborock.roborock_typing import RoborockCommand

_STATUS_PARAM = "status"


class FlowLedStatusTrait(FlowLedStatus, common.V1TraitMixin):
    """Trait for controlling the Flow LED status of a Roborock device."""

    command = RoborockCommand.GET_FLOW_LED_STATUS
    requires_feature = "is_flow_led_setting_supported"

    async def enable(self) -> None:
        """Enable the Flow LED status."""
        await self.rpc_channel.send_command(RoborockCommand.SET_FLOW_LED_STATUS, params={_STATUS_PARAM: 1})

    async def disable(self) -> None:
        """Disable the Flow LED status."""
        await self.rpc_channel.send_command(RoborockCommand.SET_FLOW_LED_STATUS, params={_STATUS_PARAM: 0})
