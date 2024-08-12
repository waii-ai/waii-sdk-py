---
id: user-module
title: User
---

The `User` module contains methods related to users in the system such as managing access keys, managing users.
Here are some of its methods:

### Create Access Key
```python
WAII.User.create_access_key(params: CreateAccessKeyRequest) -> GetAccessKeyResponse
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
WAII.User.list_access_keys(params: GetAccessKeyRequest) -> GetAccessKeyResponse
```
This method list access keys of the user.

`GetAccessKeyRequest` is empty object with no fields

Response is `GetAccessKeyResponse` which is described above

For Example
```python

params = GetAccessKeyRequest()
resp = WAII.User.list_access_keys(params)

>>> print(response.access_keys)  # List of  access keys
```

### Delete Access key
```python
WAII.User.delete_access_key(params: DelAccessKeyRequest) -> DelAccessKeyResponse
```
This method deletes the access key of the user.

`DelAccessKeyRequest` has following properties
    `names`: It is list of string denoting the name of the access keys which user wants to delete.

Response is `DelAccessKeyResponse` which is empty object

For Example
```python

params = DelAccessKeyRequest(names=["test2"])
resp = WAII.User.delete_access_key(params)
```

### Get User Info
```python
WAII.User.get_user_info(params: GetUserInfoRequest) -> GetUserInfoResponse
```
This method retrieves information about a user.

`GetUserInfoRequest` has the following properties:
- `user_id`: The ID of the user whose information is to be retrieved.

Response fields:
- `GetUserInfoResponse`
  - `id`
  - `name`
  - `email`
  - `roles`
  - `permissions`

For Example:
```python
params = GetUserInfoRequest(user_id="user_1")
response = WAII.User.get_user_info(params)
>>> print(response.user_info)  # Details of the requested user
```

### Update Config
```python
WAII.User.update_config(params: UpdateConfigRequest) -> UpdateConfigResponse
```
This method updates configuration settings for a user.

`UpdateConfigRequest` has the following properties:
- `updated`: Dictionary containing key and values that needs to be updated
- `deleted`: List of string denoting the keys  of config that needs to be deleted

Response fields:
- `UpdateConfigResponse`
  - `configs`: Dictionary denoting the current config

For Example:
```python
params = UpdateConfigRequest(updated={"key1": "value1", "key2": "value2"})
response = WAII.User.update_config(params)
>>> print(response)  
```

### Create User
```python
WAII.User.create_user(params: CreateUserRequest) -> CommonResponse
```
This method creates a new user.

`CreateUserRequest` has the following properties:
    -`user`: User object 
        -`id`: (string) unique id of the user
        - `name`: (string) Display name of the user to be created.
        - `tenant_id`:(string) Tenant id of the user.
        - `org_id`:(string) Org id of the user.
        - `variables`:(Dict (str, Any)) variable of the user
        - `roles`: (List[str]) roles for the user


Response fields:
- `CommonResponse`: Empty object
  

For Example:
```python

params = CreateUserRequest(user=UserDTO( id="user1",name="John Doe",tenant_id="my_tenant_id",org_id="my_org_id"))
response = WAII.User.create_user(params)
>>> print(response)  # Confirmation of user creation
```

### Delete User
```python
WAII.User.delete_user(params: DeleteUserRequest) -> CommonResponse
```
This method deletes an existing user.

`DeleteUserRequest` has the following properties:
- `id`: The user_id of the user to be deleted.

Response fields:
- `CommonResponse` Empty object

For Example:
```python
params = DeleteUserRequest(id="user_1")
response = WAII.User.delete_user(params)
>>> print(response)  
```

### Update User
```python
WAII.User.update_user(params: UpdateUserRequest) -> CommonResponse
```
This method updates information about an existing user.

`UpdateUserRequest` has the following properties:
    - `user`: User object as described in create user section


Response fields:
- `CommonResponse`: Empty object
  

For Example:
```python
params = UpdateUserRequest(user=UserDTO( id="user1",name="Pravin",tenant_id="my_tenant_id",org_id="my_org_id"))
response = WAII.User.update_user(params)
>>> print(response)  
```

### List Users
```python
WAII.User.list_users(params: ListUsersRequest) -> ListUsersResponse
```
This method retrieves a list of users.

`ListUsersRequest`:
    -`lookup_org_id`: org_id for which the users are to be retrieved.

Response fields:
- `ListUsersResponse`
  - `users`: A list of user object.

For Example:
```python
params = ListUsersRequest(lookup_org_id="my_org_id")
response = WAII.User.list_users(params)
>>> print(response.users)  # List of all users
```



