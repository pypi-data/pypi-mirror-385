from fhirpy import AsyncFHIRClient, SyncFHIRClient
from .operator import Operator
from .search import Search
from .loader import Loader
from .digitaltwins import DigitalTwin
from abc import ABC, abstractmethod


class AbstractAdapter(ABC):
    async_client = None
    sync_client = None

    def __init__(self, url, authorization):
        self.async_client = AsyncFHIRClient(url=url, authorization=authorization)
        self.sync_client = SyncFHIRClient(
            url,
            requests_config={
                "verify": False,
                "allow_redirects": True,
                "timeout": 60,
            },
            authorization=authorization
        )

    @property  # pragma no cover
    @abstractmethod
    def operator_class(self):
        pass

    @property  # pragma no cover
    @abstractmethod
    def loader_class(self):
        pass

    @property  # pragma no cover
    @abstractmethod
    def digitaltwin_class(self):
        pass

    @property  # pragma no cover
    @abstractmethod
    def search_class(self):
        pass


class Adapter(AbstractAdapter, ABC):
    operator_class = Operator
    search_class = Search
    loader_class = Loader
    digitaltwin_class = DigitalTwin

    def __init__(self, url, authorization='Bearer TOKEN'):
        super().__init__(url, authorization)

    def search(self):
        return self.search_class(self)

    def operator(self):
        return self.operator_class(self)

    def loader(self):
        return self.loader_class(self, self.operator())

    def digital_twin(self):
        return self.digitaltwin_class(self, self.operator())
