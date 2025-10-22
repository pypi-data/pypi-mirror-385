import uuid

class UniqueIdentifierProvider:
    @staticmethod
    def get_new_identifier() -> str:
        return str(uuid.uuid4())

