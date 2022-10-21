from datetime import datetime

from bson.objectid import ObjectId
from darasdk_helper.factory import to_object_id
from darasdk_helper.mongo.base_client import BaseClient
from pymongo.collection import Collection
from pyrsistent import PClass, field


class ModelBaseMetaclass(type(PClass)):
    """Metaclass for all models."""

    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, ModelBaseMetaclass)]
        if not parents:
            return super_new(cls, name, bases, attrs, **kwargs)
        new_class = super_new(cls, name, bases, attrs, **kwargs)

        module = attrs.pop("__module__")
        attr_meta = attrs.pop("Meta", None)
        abstract = getattr(attr_meta, "abstract", False)

        if attr_meta is None:
            raise RuntimeError(
                "Model class %s.%s doesn't declare Meta class." % (module, name)
            )

        db = getattr(attr_meta, "db", None)
        db_table = getattr(attr_meta, "db_table", None)
        if not (db and db_table):
            raise RuntimeError(
                "Model class %s.%s doesn't declare db and db_table in "
                "Meta class." % (module, name)
            )

        for parent in parents:
            _get_client = getattr(parent, "_get_client", None)
            if _get_client is not None:
                break

        client = _get_client() if callable(_get_client) else _get_client

        setattr(new_class, "objects", client[db][db_table])
        return new_class


class MongoModel(PClass, metaclass=ModelBaseMetaclass):
    objects: Collection

    _id = field(ObjectId, factory=to_object_id, serializer=lambda format, x: str(x))

    UPDATED_KEY = "updated"

    def get(self, _id: str):
        obj_data = self.objects.find_one({"_id": to_object_id(_id)})
        return self.__class__(**obj_data)

    def save(self, updated_key="updated"):
        data = self.serialize()
        if "_id" not in data:
            resp = self.objects.insert_one(data)
            self._id = resp.inserted_id
            return resp
        else:
            _id = data.pop("_id")
            if hasattr(self, self.UPDATED_KEY):
                data[self.UPDATED_KEY] = datetime.utcnow()
            return self.objects.update_one({"_id": ObjectId(_id)}, {"$set": data})

    def delete(self):
        data = self.serialize()
        if "_id" not in data:
            return

        _id = data.pop("_id")
        return self.objects.delete_one({"_id": ObjectId(_id)})

    _get_client = BaseClient.load_from_env().getclient

    __setattr__ = object.__setattr__

    class Meta:
        db = ""
        db_table = None
