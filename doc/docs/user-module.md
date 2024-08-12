---
id: user-module
title: User
---

The `User` module contains methods related to users in the system such as managing access keys, managing users.
Here are some of its methods:

### Create Access Key
```python
WAII.user.create_access_key(params: CreateAccessKeyRequest) -> GetAccessKeyResponse
```
This method creates a new access key for a user.

`CreateAccessKeyRequest` has following properties
    `name`:It is string type denoting the name of the access key
Response fields:
`GetAccessKeyResponse`
    `access_keys`: Optional[List[AccessKey]]

`AccessKey` is defined as 
    `access_key`: It is access key string
    `user_id`: User id of user to whom access key belongs
    `name`: Name of the access key which was given at the time of key creation
    `created_at`: Timestamp when key was created.
    

    

For Example
```python

params = CreateAccessKeyRequest(name="test-key")
response = Waii.user.create_access_key(params)
>>> print(response.access_keys)  # List of created access keys
```

### List Access Keys
```python
WAII.user.list_access_keys(params: GetAccessKeyRequest) -> GetAccessKeyResponse
```
This method list access keys of the user.

`GetAccessKeyRequest` is empty object with no fields

Response is `GetAccessKeyResponse` which is described above

For Example
```python

params = GetAccessKeyRequest()
resp = WAII.user.list_access_keys(params)

>>> print(response.access_keys)  # List of  access keys
```

### Delete Access key
```python
WAII.user.delete_access_key(params: DelAccessKeyRequest) -> DelAccessKeyResponse
```
This method deletes the access key of the user.

`DelAccessKeyRequest` has following properties
    `names`: It is list of string denoting the name of the access keys which user wants to delete.

Response is `DelAccessKeyResponse` which is empty object

For Example
```python

params = DelAccessKeyRequest(names=["test2"])
resp = WAII.user.delete_access_key(params)
```




