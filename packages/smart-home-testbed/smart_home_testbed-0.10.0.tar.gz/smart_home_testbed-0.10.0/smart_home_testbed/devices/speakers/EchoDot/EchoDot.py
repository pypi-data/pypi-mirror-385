from ....DeviceState   import DeviceState
from ....DeviceControl import DeviceControl


class EchoDot(DeviceState, DeviceControl):
    """
    Amazon Echo Dot (2nd generation).
    """

    ### CLASS VARIABLES ###

    # Android package name
    # We use a recorded voice note to interact with the device
    android_package = "com.google.android.apps.recorder"

    # Screen coordinates to play voice recording
    x = 972
    y = 582


    ### METHODS ###

    def voice(self) -> None:
        """
        Play the voice recording to interact with the Echo Dot.
        """
        self.get_phone().shell(f"input tap {self.x} {self.y}")

    
    def get_state(self) -> None:
        """
        Get the state of the device.
        Irrelevant for the Echo Dot: always return None.
        """
        return None

    
    def is_event_successful(self, _ = None) -> bool:
        """
        Check if an event was successful.
        For this device, always return True.

        Args:
            _ (Any): Ignored.
        Returns:
            bool: Always True.
        """
        return True
