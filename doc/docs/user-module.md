---
id: user-module
title: User
---

The `User` module contains methods related to users in the system such as managing access keys, managing users.
Here are some of its methods:

### Overview

In the WAII system, there's a hierarchical relationship between organizations, tenants, and users. At the top level, we have organizations (orgs), which represent the highest level of grouping. Each organization can contain multiple tenants, which are subgroups within the organization. Tenants, in turn, can have multiple users associated with them.

Users are individual accounts within the system, each belonging to a specific tenant and, by extension, to an organization. This structure allows for flexible management of access and resources across different levels of the hierarchy. For example, a user's permissions and access rights may be determined by their associated tenant and organization.

### Create Access Key
```python
WAII.User.create_access_key(params: CreateAccessKeyRequest) -> GetAccessKeyResponse
```
This method creates a new access key for a user.

### CreateAccessKeyRequest

`CreateAccessKeyRequest` has the following properties:

- `name`: It is a string type denoting the name of the access key.

### Response Fields

`GetAccessKeyResponse` has the following properties:

- `access_keys`: `Optional[List[AccessKey]]`

`AccessKey` is defined as:

- `access_key`: It is the access key string.
 - `user_id`: User ID of the user to whom the access key belongs.
 - `name`: Name of the access key which was given at the time of key creation.
 - `created_at`: Timestamp when the key was created.
    

    

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

`DelAccessKeyRequest` has following properties:

- `names`: It is list of string denoting the name of the access keys which user wants to delete.

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

Note:
- Tenant and Org must be created before creating a user.

#### User role management

In order to create user with specific roles, you can fill the roles field.

Documentation for roles can be found [waii-user-roles](waii-user-roles.md)

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

### Create Tenant
```python
WAII.User.create_tenant(params: CreateTenantRequest) -> CommonResponse
```
This method creates a new tenant.

`CreateTenantRequest` has the following properties:

- `tenant`: Tenant object
  - `id`: (string) unique id of the tenant
  - `name`: (string) Display name of the tenant to be created.
  - `variables`: (Dict (str, Any)) variables of the tenant
  - `org_id`: (string) Org ID of the tenant

Response fields:

- `CommonResponse`: Empty object

For Example:
```python
params = CreateTenantRequest(tenant=Tenant(id="tenant1", name="Example Tenant", variables={"key1": "value1"}, org_id="org123"))
response = WAII.User.create_tenant(params)
print(response)  
```

Note:
- Org must be created before creating a tenant.

### Update Tenant
```python
WAII.User.update_tenant(params: UpdateTenantRequest) -> CommonResponse
```
This method updates information about an existing tenant.

`UpdateTenantRequest` has the following properties:

- `tenant`: Tenant object as described in the create tenant section

Response fields:

- `CommonResponse`: Empty object

For Example:
```python
params = UpdateTenantRequest(tenant=Tenant(id="tenant1", name="Updated Tenant", variables={"key2": "value2"}, org_id="org123"))
response = WAII.User.update_tenant(params)
print(response)  
```

### Delete Tenant
```python
WAII.User.delete_tenant(params: DeleteTenantRequest) -> CommonResponse
```
This method deletes an existing tenant.

`DeleteTenantRequest` has the following properties:

- `id`: The tenant_id to be deleted.

Response fields:

- `CommonResponse`: Empty object

For Example:
```python
params = DeleteTenantRequest(id="tenant1")
response = WAII.Tenant.delete_tenant(params)
print(response)  
```

### List Tenants
```python
WAII.User.list_tenants(params: ListTenantsRequest) -> ListTenantsResponse
```
This method retrieves a list of tenants.

`ListTenantsRequest` has the following properties:

- `lookup_org_id`: (optional) org_id for which the tenants are to be retrieved.

Response fields:

- `ListTenantsResponse`:
  - `tenants`: A list of Tenant objects.

For Example:
```python
params = ListTenantsRequest(lookup_org_id="org123")
response = WAII.User.list_tenants(params)
print(response.tenants)  # List of all tenants
```

### Create Org
```python
WAII.User.create_org(params: CreateOrganizationRequest) -> CommonResponse
```
This method creates a new org.

`CreateOrganizationRequest` has the following properties:

- `organization`: Organization object
  - `id`: (string) unique id of the organization
  - `name`: (string) Display name of the organization to be created.
  - `variables`: (Dict (str, Any)) variables of the organization

Response fields:

- `CommonResponse`: Empty object

For Example:
```python
params = CreateOrganizationRequest(organization=Organization(id="o1", name="My Org"))
response = WAII.User.create_org(params)
print(response)  
```

### Update Org
```python
WAII.User.update_org(params: UpdateOrganizationRequest) -> CommonResponse
```
This method updates information about an existing org.

`UpdateOrganizationRequest` has the following properties:

- `organization`: Organization object as described in the create org section

Response fields:

- `CommonResponse`: Empty object

For Example:
```python
params = UpdateOrganizationRequest(organization=Organization(id="o1", name="My Org2"))
response = WAII.User.update_org(params)
print(response)  
```

### Delete Org
```python
WAII.User.delete_org(params: DeleteOrganizationRequest) -> CommonResponse
```
This method deletes an existing org.

`DeleteOrganizationRequest` has the following properties:

- `id`: The org_id to be deleted.

Response fields:

- `CommonResponse`: Empty object

For Example:
```python
params = DeleteOrganizationRequest(id="org1")
response = WAII.User.delete_org(params)
print(response)  
```

### List Orgs
```python
WAII.User.list_orgs(params: ListOrganizationsRequest) -> ListOrganizationsResponse
```
This method retrieves a list of organizations.

`ListOrganizationsRequest` is an empty object.

Response fields:

- `ListOrganizationsResponse`:
  - `organizations`: A list of organization objects.

For Example:
```python
params = ListOrganizationsRequest()
response = WAII.User.list_orgs(params)
print(response.organizations)  # List of all organizations
```

### Impersonation

Using Python SDK, you can impersonate as a user to perform actions on behalf of that user. This is useful when you want to perform actions that require the user's permissions and access rights.

To impersonate an user, you need to be part of `waii-org-admin-user` role. If you are using SaaS, you need to reach out to Waii team to get this role assigned to you.

Here is an example of how you can impersonate as a user (you can only use the multi-tenant sdk for this):

```python
client1_sdk = Waii()
client1_sdk.initialize(url='...', api_key="<your-api-key>")
with client1_sdk.impersonate_user(user_id="user_id_1"):
    # do other operations such as run query, modify semantic context, etc.
    client1_sdk.semantic_context.modify_semantic_context(ModifySemanticContextRequest(
        updated=[
            # the statement object which mentioned above
        ]
    ))
    client1_sdk.query.run_query(RunQueryRequest(
        query="...",
        variables={...}
    ))
    
    # it will automatically revert back to the original user after the block
```

Even if you are the waii-org-admin-user, you can only impersonate as a user that belongs to the same org as you. And you cannot impersonate as a user that has more permissions than you.

*(Not recommended)* If you don't want to use the `with` block, you can also use the `set_impersonate_user` / `clear_impersonation` methods:

```python
client1_sdk.set_impersonate_user(user_id="user_id_2")

# do other operations such as run query, modify semantic context, etc.

client1_sdk.clear_impersonation()
```