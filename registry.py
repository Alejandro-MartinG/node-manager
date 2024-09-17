class Registry:
    _instance = None
    _registry = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Registry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, key, instance):
        cls._registry[key] = instance

    @classmethod
    def get(cls, key):
        return cls._registry.get(key)

    @classmethod
    def remove(cls, key):
        del cls._registry[key]

    @classmethod
    def list_instances(cls):
        return list(cls._registry.keys())