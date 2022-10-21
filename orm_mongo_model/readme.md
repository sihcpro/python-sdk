# ORM Mongo Model

I try to use PClass vs pymongo to create an ORM model for Mongo.

## Model Example:

```python
class UserModel(MongoModel):
    APPROVED = "A"
    PEDDING = "P"
    REJECTED = "R"
    DELETED = "D"
    STATUS = [
        (APPROVED, "Approved"),
        (PEDDING, "Pedding"),
        (REJECTED, "Rejected"),
        (DELETED, "Deleted"),
    ]

    username = field(str, mandatory=True)
    password = field(str, mandatory=True)

    env = field(str, mandatory=True, initial="test")
    status = field(str, mandatory=True, initial=PEDDING, invariant=choices(STATUS))

    created = field(
        datetime,
        mandatory=True,
        initial=datetime.utcnow,
        factory=to_type(datetime),
        serializer=lambda format, x: str(x),
    )
    updated = field(
        datetime,
        mandatory=True,
        initial=datetime.utcnow,
        factory=lambda x: to_type(datetime),
        serializer=lambda format, x: str(x),
    )

    class Meta:
        db = "database_name"
        db_table = "table_name"
```

## Query Example

### List all
```python
data = list(UserModel.objects.find({}))
print("All users", list(data))
```

### Create a new user
```python
user_info = {
    "username": "Chi",
    "password": "123456",
}
user = UserModel(**user_info)
user.save()
print("user": user.serialize())
```
- Expect:
```python
{
    "_id": "6244671586ebe62645fbead8",
    "username": "Chi",
    "password": "123456",
    "env": "test",
    "status": "P",
    "created": datetime.datetime(2022, 10, 21, 0, 18, 16, 895655),
    "updated": datetime.datetime(2022, 10, 21, 0, 18, 16, 895655),
}
```


### Update an user
```python
user_info = UserModel.objects.find_one({"_id": ObjectId("6244671586ebe62645fbead8")})
user = UserModel(**user_info)
user.password = "123456789"
user.save()
```
or 
```python
user = UserModel.get("6244671586ebe62645fbead8")
user.password = "123456789"
user.save()
```


### Delete an user
```python
user_info = UserModel.objects.find_one({"_id": ObjectId("6244671586ebe62645fbead8")})
user = UserModel(**user_info)
user.delete()
```
or
```python
user = UserModel.get("6244671586ebe62645fbead8")
user.delete()
```
