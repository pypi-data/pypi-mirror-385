class DuplicateInstanceError(Exception):
    """Customize Duplicate data in FHIR server"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)