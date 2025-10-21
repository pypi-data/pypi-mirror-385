from abc import ABC, abstractmethod
import sys
from pathlib import Path
import json


class AbstractLoader(ABC):
    core = None

    def __init__(self, core, operator):
        self.core = core
        self.operator = operator

    @abstractmethod
    def load_fhir_bundle(self, dataset_path):
        pass


class Loader(AbstractLoader, ABC):
    def __init__(self, core, operator):
        super().__init__(core, operator)

    async def load_fhir_bundle(self, dataset_path):
        sys.stdout.write("Import progress: 0%   \r")

        dataset_root = Path(dataset_path)

        filenames = [
            filename.name for filename in dataset_root.iterdir()
            if filename.name.endswith('.json')]

        total_count = len(filenames)
        for index, filename in enumerate(filenames):
            await self._import_bundle(dataset_root / filename)
            progress = int(float(index + 1) / float(total_count) * 100)
            sys.stdout.write("Import progress: %d%%   \r" % progress)
            sys.stdout.flush()
        sys.stdout.write("Import progress: 100%\n")
        sys.stdout.write("{0} bundles imported".format(total_count))

    async def _import_bundle(self, filename):
        with open(filename, encoding='utf-8') as fd:
            patient_json = json.load(fd)
        bundle = self.core.async_client.resource('Bundle')
        bundle['type'] = 'transaction'
        bundle['entry'] = patient_json['entry']
        await bundle.save()
