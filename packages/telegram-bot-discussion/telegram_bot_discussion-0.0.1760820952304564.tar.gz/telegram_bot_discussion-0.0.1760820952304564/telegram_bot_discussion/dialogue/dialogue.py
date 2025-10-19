from abc import ABC, abstractmethod


from .replicas.base import EmptyReplica, Polemic


class Dialogue(ABC):
    @abstractmethod
    def dialogue(self, *args, **kwargs) -> Polemic:
        """Method `dialogue()` contains yielded-sequence of `Replicas` which ended by `StopReplica`."""
        ...

    def _replicas_flow(self, *args, **kwargs) -> Polemic:
        """Method `_replicas_flow()` is internal and help init `Replica`-iterator by default first `Dialogue` step."""
        _ = yield EmptyReplica()
        return (yield from self.dialogue(*args, **kwargs))
