from abc import ABC, abstractmethod

class Controller(ABC):
    @property
    @abstractmethod
    def NAME(self) -> str:
        """The name of the controller."""
        pass

    @abstractmethod
    async def is_active(self) -> bool:
        """Check if the controller is active (e.g., Spotify is playing, TV is on, etc.)."""
        pass
