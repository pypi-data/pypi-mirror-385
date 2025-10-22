import json

class ObjectExtension:
    @staticmethod
    def to_json(obj) -> str:
        return json.dumps(obj, default=ObjectExtension._convert_to_camel_case, separators=(',', ':'))

    @staticmethod
    def _convert_to_camel_case(obj):
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                new_key = ''.join([k[0].lower() if i == 0 else k[i] for i in range(len(k))])
                new_obj[new_key] = ObjectExtension._convert_to_camel_case(v)
            return new_obj
        elif isinstance(obj, list):
            return [ObjectExtension._convert_to_camel_case(item) for item in obj]
        else:
            return obj
