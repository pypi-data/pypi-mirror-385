import os
import logging
import hvac

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VaultController:
    
    def __init__(self, mount_path: str, credentials: dict, strict_http: bool = True):
        """
        Initialize the VaultController with configuration from a JSON file.
        
        :param mount_path: The mount path in Vault.
        :param credentials: Dictionary with Vault credentials.
        :param strict_http: If True, use GET with ?list=true instead of LIST method (required for AppRole).
        """
        self.vault_addr = os.getenv('VAULT_ADDR')
        self.mount_path = mount_path
        self.app_role_id = credentials.get('app_role_id') if credentials.get('app_role_id') is not None else os.getenv('APP_ROLE_ID')
        self.app_secret_id = credentials.get('app_secret_id') if credentials.get('app_secret_id') is not None else os.getenv('APP_SECRET_ID')

        # Initialize Vault client with strict_http for AppRole compatibility
        self.client = hvac.Client(url=self.vault_addr, strict_http=strict_http)
        self.client.auth.approle.login(
            role_id=self.app_role_id,
            secret_id=self.app_secret_id,
        )
       
        # Check if the client is authenticated
        if not self.client.is_authenticated():
            raise ValueError("Failed to authenticate to Vault. Check your token and server configuration.")

        logger.info(f"Successfully authenticated to Vault with base path: {self.mount_path}")

    def build_secret_path(self, root_path, sub_path, secret_key):
        """
        Build the full secret path using sub_path and secret_key.
        
        :param sub_path: The tenant ID to append to the path.
        :param secret_key: The secret key name to append to the path.
        :return: The complete secret path.
        """
        
        if sub_path is None or sub_path == "":
            return f"{root_path}/{secret_key}"
        return f"{root_path}/{sub_path}/{secret_key}"

    def secret_exists(self, root_path, sub_path, secret_key):
        """
        Check if a secret exists at the specified path.
        
        :param sub_path: The tenant ID to check.
        :param secret_key: The connector ID to check.
        :return: True if the secret exists, False otherwise.
        """
        secret_path = self.build_secret_path(root_path, sub_path, secret_key)
        try:
            self.client.secrets.kv.v2.read_secret_version(path=secret_path, mount_point=self.mount_path.strip('/'))
            return True
        except hvac.exceptions.InvalidRequest as e:
            logger.warning(f"Invalid request for secret at {secret_path}: {str(e)}")
            if 'path' in str(e):
                logger.warning(f"Secret path not found at: {secret_path}. Check if tenant ID '{sub_path}' and connector ID '{secret_key}' are correct.")
            return False

    def store_secret(self, root_path, sub_path, secret_key, secret_data):
        """
        Store a new secret in HashiCorp Vault.
        
        :param sub_path: Tenant ID to append to the secret path.
        :param secret_key: Connector ID to append to the secret path.
        :param secret_data: Dictionary containing the secret data to be stored.
        """
        secret_path = self.build_secret_path(root_path, sub_path, secret_key)
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=secret_path,  # KV v2 path
                mount_point=self.mount_path.strip('/'),
                secret=secret_data
            )
            logger.info(f"Secret stored successfully at {secret_path}")
        except Exception as e:
            logger.error("Failed to store secret: %s", str(e))
            raise

    def get_secret(self, root_path, sub_path, secret_key):
        """
        Retrieve a secret from HashiCorp Vault.
        
        :param sub_path: Tenant ID to append to the secret path.
        :param secret_key: Connector ID to append to the secret path.
        :return: The retrieved secret data as a dictionary, or None if not found.
        """
        secret_path = self.build_secret_path(root_path, sub_path, secret_key)
        if not self.secret_exists(root_path, sub_path, secret_key):
            logger.info(f"No secret found for service ID {root_path}, tenant ID '{sub_path}' and connector ID '{secret_key}'.")
            return None
        
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=secret_path,
                mount_point=self.mount_path.strip('/')
            )
            secret_data = response['data']['data']
            logger.info(f"Secret retrieved successfully from {secret_path}")
            return secret_data
        except hvac.exceptions.VaultError as e:
            logger.error(f"Vault error occurred: {str(e)}")
            return None
        except hvac.exceptions.InvalidPath as e:
            # This exception is raised when the path doesn't exist
            logger.warning(f"No secrets found for service ID {root_path}, tenant ID '{sub_path}' and connector ID '{secret_key}'. Path does not exist: {str(e)}")
            return None
        except hvac.exceptions.InvalidRequest as e:
            logger.info(f"Invalid request for secret at {secret_path}: {str(e)}")
            return None
        except hvac.exceptions.Forbidden as e:
            logger.error(f"Permission denied when accessing secret for service ID {root_path}, tenant ID '{sub_path}' and connector ID '{secret_key}': {str(e)}")
            raise
        except Exception as e:
            logger.error("Failed to retrieve secret: %s", str(e))
            raise

    def update_secret(self, root_path, sub_path, secret_key, updated_data):
        """
        Update an existing secret in HashiCorp Vault.
        
        :param sub_path: Tenant ID to append to the secret path.
        :param secret_key: Connector ID to append to the secret path.
        :param updated_data: Dictionary containing the updated secret data.
        """
        secret_path = self.build_secret_path(root_path, sub_path, secret_key)
        if not self.secret_exists(root_path, sub_path, secret_key):
            logger.info(f"No secret found for service ID {root_path}, tenant ID '{sub_path}' and connector ID '{secret_key}' to update.")
            return {"status":"success", "message":f"No secret found for service ID {root_path}, tenant ID '{sub_path}' and connector ID '{secret_key}' to update."}

        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=secret_path,
                mount_point=self.mount_path.strip('/'),
                secret=updated_data
            )
            logger.info(f"Secret updated successfully at {secret_path}")
            return {"status":"success", "message":"Secret updated successfully"}
        except Exception as e:
            logger.error("Failed to update secret: %s", str(e))
            raise

    def delete_secret(self, root_path, sub_path, secret_key):
        """
        Delete an existing secret in HashiCorp Vault.
        
        :param sub_path: Tenant ID to append to the secret path.
        :param secret_key: Connector ID to append to the secret path.
        """
        secret_path = self.build_secret_path(root_path, sub_path, secret_key)
        if not self.secret_exists(root_path, sub_path, secret_key):
            logger.info(f"No secret found for service ID {root_path}, tenant ID '{sub_path}' and connector ID '{secret_key}' to delete.")
            return {"status":"success", "message":f"No secret found for service ID {root_path}, tenant ID '{sub_path}' and connector ID '{secret_key}' to update."}

        try:
            # Delete the secret at the specified path
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=secret_path,
                mount_point=self.mount_path.strip('/'),
            )
            logger.info(f"Secret deleted successfully at {secret_path}")
            return {"status":"success", "message":"Secret deleted successfully"}
        except Exception as e:
            logger.error("Failed to delete secret: %s", str(e))
            raise

    def delete_all_secrets_for_tenant(self, root_path):
        """
        Delete all secrets for a specific tenant recursively.

        :param root_path: The tenant ID to delete secrets for
        """
        secret_keys = self.get_all_secrets(root_path)
        logger.info(f"Retrieved secrets structure for tenant {root_path}")
        self._delete_secrets_recursive(root_path, secret_keys)
        
        return {"status":"success", "message":"All secrets deleted successfully"}
    
    def delete_secrets_recursive(self, base_path, secrets_dict):
        for key, value in secrets_dict.items():
            if key.endswith('/'):
                # It's a folder - recurse into it
                folder_name = key.rstrip('/')
                nested_path = f"{base_path}/{folder_name}"
                self.delete_secrets_recursive(nested_path, value)
            else:
                path_parts = base_path.split('/', 1)
                tenant_id = path_parts[0]
                folder_path = path_parts[1] if len(path_parts) > 1 else ""
                secret_name = key
                self.delete_secret(tenant_id, folder_path, secret_name)

    def list_all_secrets(self, root_path):
        """
        List all secrets for a specific root path.

        :param root_path: The root path to list all secrets for.
        """
        return self.client.secrets.kv.v2.list_secrets(path="")
    
    def get_all_secrets(self, path=""):
        """
        Recursively get all secrets from a given path.
        
        :param path: The path to start listing secrets from.
        :return: Dictionary containing all secrets and their values.
        """
        secrets_data = {}

        try:
            # List secrets at the given path
            response = self.client.secrets.kv.v2.list_secrets(
                path=path,
                mount_point=self.mount_path.strip('/')
            )
            
            if 'data' in response and 'keys' in response['data']:
                for key in response['data']['keys']:
                    full_path = f"{path}/{key}".strip("/")  # Construct full secret path

                    try:
                        if key.endswith("/"):  # It's a folder, recurse into it
                            secrets_data[key] = self.get_all_secrets(full_path)
                        else:  # It's a secret, fetch its value
                            secret_response = self.client.secrets.kv.v2.read_secret_version(
                                path=full_path,
                                mount_point=self.mount_path.strip('/')
                            )
                            secrets_data[key] = secret_response["data"]["data"]
                            logger.info(f"Secret retrieved successfully from {full_path}")
                    except hvac.exceptions.InvalidPath as e:
                        logger.warning(f"Path does not exist: {full_path}. Error: {str(e)}")
                        continue
                    except hvac.exceptions.InvalidRequest as e:
                        logger.info(f"Invalid request for secret at {full_path}: {str(e)}")
                        continue
                    except hvac.exceptions.Forbidden as e:
                        logger.error(f"Permission denied when accessing secret at {full_path}: {str(e)}")
                        raise
                    except Exception as e:
                        logger.error(f"Failed to retrieve secret at {full_path}: {str(e)}")
                        raise

            return secrets_data

        except hvac.exceptions.VaultError as e:
            logger.error(f"Vault error occurred while listing secrets: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to list secrets at path {path}: {str(e)}")
            raise