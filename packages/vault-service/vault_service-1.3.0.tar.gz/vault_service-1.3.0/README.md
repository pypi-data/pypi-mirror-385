# Vault Service

The **Vault Service** package provides a convenient interface for interacting with HashiCorp Vault. It offers various methods to manage secrets for both services and tenants.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Methods](#methods)
  - [Service Methods](#service-methods)
    - [store_service_secret](#store_service_secret)
    - [get_service_secret](#get_service_secret)
    - [update_service_secret](#update_service_secret)
    - [delete_service_secret](#delete_service_secret)
  - [Tenant Methods](#tenant-methods)
    - [store_tenant_secret](#store_tenant_secret)
    - [get_tenant_secret](#get_tenant_secret)
    - [update_tenant_secret](#update_tenant_secret)
    - [delete_tenant_secret](#delete_tenant_secret)
- [License](#license)

## Installation

You can install the Vault Service package using pip:

```bash
pip install vault-service
```

## Usage

To use the Vault Service, you need to initialize the `VaultController` and then call the utility functions. Make sure to set the required environment variables for Vault connection:

```bash
export VAULT_ADDR='https://your-vault-address'
export APP_ROLE_ID='your-app-role-id'
export APP_SECRET_ID='your-app-secret-id'
```

## Methods

### Service Methods

#### `store_service_secret(root_path: str, sub_path: str, secret_name: str, secret_data: SecretData, credentials: dict)`

Stores a new secret in HashiCorp Vault under the "secret" mount path.

**Parameters:**
- `root_path`: The root path in Vault
- `sub_path`: The sub path in Vault
- `secret_name`: The name of the secret to store
- `secret_data`: An instance of `SecretData`, containing the secret information
- `credentials`: Dictionary containing Vault credentials:
  ```python
  {
      'app_role_id': 'your-app-role-id',
      'app_secret_id': 'your-app-secret-id'
  }
  ```

**Returns:** 
- `dict`: Response object containing:
  - `status`: "success" or "error"
  - `message`: Description of the operation result

**Sample Payload for `secret_data`:**
```json
{
  "auth_key": "<auth-key>",
  "database_credentials": {
    "host": "localhost",
    "port": 5432,
    "database": "my_database",
    "user": "my_user",
    "password": "my_password"
  },
  "redis_credentials": {
    "host": "localhost",
    "port": 6379,
    "password": "my_password"
  }
}
```

---

#### `get_service_secret(root_path: str, sub_path: str, secret_name: str, credentials: dict)`

Retrieves a secret from HashiCorp Vault.

**Parameters:**
- `root_path`: The root path in Vault.
- `sub_path`: The sub path in Vault.
- `secret_name`: The name of the secret to retrieve.
- `credentials`: Dictionary containing Vault credentials.

**Returns:**
- `dict`: Response object containing:
  - `status`: "success" or "error"
  - `message`: Description of the operation result
  - `data`: The retrieved secret data (when successful)

---

#### `update_service_secret(root_path: str, sub_path: str, secret_name: str, secret_data: SecretData, credentials: Optional[dict] = None)`

Updates an existing secret in HashiCorp Vault for the specified service, tenant, and secret name.

**Parameters:**
- `root_path`: The root path in Vault
- `sub_path`: The sub path in Vault
- `secret_name`: The name of the secret to update
- `secret_data`: An instance of `SecretData`, containing the updated secret information
- `credentials`: Optional dictionary containing Vault credentials:
  ```python
  {
      'app_role_id': 'your-app-role-id',
      'app_secret_id': 'your-app-secret-id'
  }
  ```

**Returns:** A message indicating the success or failure of the operation.

**Sample Payload for `secret_data`:**
```json
{
  "auth_key": "<new-auth-key>",
  "database_credentials": {
    "host": "localhost",
    "port": 5432,
    "database": "my_database",
    "user": "my_user",
    "password": "new_password"
  },
  "redis_credentials": {
    "host": "localhost",
    "port": 6379,
    "password": "new_password"
  }
}
```

---

#### `delete_service_secret(root_path: str, sub_path: str, secret_name: str, credentials: dict)`

Deletes a secret from HashiCorp Vault for the specified service, tenant, and secret name.

**Parameters:**
- `root_path`: The root path in Vault
- `sub_path`: The sub path in Vault
- `secret_name`: The name of the secret to delete.

**Returns:** A message indicating the success or failure of the deletion.

---

### Tenant Methods

#### `store_tenant_secret(tenant_id: str, sub_path: str, secret_name: str, secret_data: SecretData, credentials: dict)`

Stores a new secret in HashiCorp Vault under the "tenant" mount path.

**Parameters:**
- `tenant_id`: The ID of the tenant
- `sub_path`: The sub path in Vault
- `secret_name`: The name of the secret to store
- `secret_data`: An instance of `SecretData`, containing the secret information
- `credentials`: Dictionary containing Vault credentials:
  ```python
  {
      'app_role_id': 'your-app-role-id',
      'app_secret_id': 'your-app-secret-id'
  }
  ```

**Returns:** 
- `dict`: Response object containing:
  - `status`: "success" or "error"
  - `message`: Description of the operation result

**Sample Payload for `secret_data`:**
```json
{
  "auth_key": "<auth-key>",
  "database_credentials": {
    "host": "localhost",
    "port": 5432,
    "database": "my_database",
    "user": "my_user",
    "password": "my_password"
  },
  "redis_credentials": {
    "host": "localhost",
    "port": 6379,
    "password": "my_password"
  }
}
```

---

#### `get_tenant_secret(tenant_id: str, sub_path: str, secret_name: str, credentials: dict)`

Retrieves a secret from HashiCorp Vault under the tenant mount path.

**Parameters:**
- `tenant_id`: The ID of the tenant
- `sub_path`: The sub path in Vault
- `secret_name`: The name of the secret to retrieve
- `credentials`: Dictionary containing Vault credentials

**Returns:**
- `dict`: Response object containing:
  - `status`: "success" or "error"
  - `message`: Description of the operation result
  - `data`: The retrieved secret data (when successful)

---

#### `update_tenant_secret(tenant_id: str, sub_path: str, secret_name: str, secret_data: SecretData, credentials: dict)`

Updates an existing secret in HashiCorp Vault under the tenant mount path.

**Parameters:**
- `tenant_id`: The ID of the tenant
- `sub_path`: The sub path in Vault
- `secret_name`: The name of the secret to update
- `secret_data`: An instance of `SecretData`, containing the updated secret information
- `credentials`: Dictionary containing Vault credentials:
  ```python
  {
      'app_role_id': 'your-app-role-id',
      'app_secret_id': 'your-app-secret-id'
  }
  ```

**Returns:** A message indicating the success or failure of the operation.

**Sample Payload for `secret_data`:**
```json
{
  "auth_key": "<new-auth-key>",
  "database_credentials": {
    "host": "localhost",
    "port": 5432,
    "database": "my_database",
    "user": "my_user",
    "password": "new_password"
  },
  "redis_credentials": {
    "host": "localhost",
    "port": 6379,
    "password": "new_password"
  }
}
```

---

#### `delete_tenant_secret(tenant_id: str, sub_path: str, secret_name: str, credentials: dict)`

Deletes a secret from HashiCorp Vault under the tenant mount path.

**Parameters:**
- `tenant_id`: The ID of the tenant
- `sub_path`: The sub path in Vault
- `secret_name`: The name of the secret to delete
- `credentials`: Dictionary containing Vault credentials

**Returns:** A message indicating the success or failure of the deletion.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

### Changes:
- Added `tenant_id` as the first required parameter for each method.
- Specified that `tenant_id` is not optional in each method.
- Added `credentials` parameter to each method signature.
- Specified that `credentials` is optional in each method documentation.