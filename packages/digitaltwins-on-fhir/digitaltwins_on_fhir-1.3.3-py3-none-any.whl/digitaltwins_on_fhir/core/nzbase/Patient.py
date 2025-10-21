import re
from ..exception.custom_error import DuplicateInstanceError


class NzPatient:
    def __init__(self, client):
        self._profile = "http://hl7.org.nz/fhir/StructureDefinition/NzPatient"
        self._client = client
        self._PatientSearchSet = self._client.resources('Patient')
        self.Patient = None

    async def create_nz_patient(self, identifier):

        result = await self._is_exist(identifier)
        if not result:
            self.Patient = self._client.resource('Patient')
            self.Patient['meta'] = {'profile': [self._profile]}
            self.Patient['identifier'] = [
                {
                    "use": "official",
                    "system": "http://sparc.sds.dataset",
                    "value": identifier
                }
            ]
            await self.Patient.save()

    async def _is_exist(self, identifier):
        patients = await self._PatientSearchSet.search(identifier=identifier).fetch_all()
        if len(patients) == 0:
            return False
        elif len(patients) == 1:
            self.Patient = patients[0]
            return True
        else:
            raise DuplicateInstanceError(
                f"There are duplicate patient resource instance (identifier: {identifier}) found in FHIR server, please delete them!")

    def update_name(self, give_name=[], family_name=''):

        if isinstance(give_name, str):
            give_name_new = [give_name]
        elif isinstance(give_name, list):
            give_name_new = [value for value in give_name if isinstance(value, str)]
        else:
            give_name_new = []
            print("The give_name is neither a string nor a list.")

        self.Patient['name'] = [
            {
                "text": f"{' '.join(give_name_new)} {family_name}",
                'given': give_name_new,
                'family': family_name,
                'use': 'official',
            }
        ]

        return self

    def update_gender(self, gender):
        valid_gender = ['male', 'female', 'other', 'unknown']

        if gender not in valid_gender:
            print(f"Error: Invalid input for gender. The valid gender value are male | female | other | unknown")
            return self

        self.Patient['gender'] = gender

        return self

    def update_birth(self, date):
        patterns = [
            r'^\d{4}$',  # YYYY
            r'^\d{4}-\d{2}$',  # YYYY-MM
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}$'  # YYYY-MM-DDThh:mm:ss+zz:zz
        ]

        for pattern in patterns:
            if re.match(pattern, date):
                self.Patient['birthDate'] = date
                return self

        print(
            "Error: Invalid date for brithDate. The format should be YYYY, YYYY-MM, YYYY-MM-DD or YYYY-MM-DDThh:mm:ss+zz:zz")
        return self

    async def save(self):
        await self.Patient.save()
