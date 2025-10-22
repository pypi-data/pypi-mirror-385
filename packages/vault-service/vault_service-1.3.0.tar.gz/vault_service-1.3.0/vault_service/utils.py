from vault_service.models.response import Response
from vault_service.models.model import SecretData
from vault_service.services.vault_controller import VaultController
import hvac


def store_service_secret(root_path: str, sub_path: str, secret_name: str, secret_data: SecretData, credentials: dict):
    mount_path = "secret"
    try:
        vault_controller = VaultController(mount_path, credentials)
        if vault_controller is None:
            return Response(status="error", message="VaultController not initialized").dict()
        vault_controller.store_secret(root_path, sub_path, secret_name, secret_data)
        return Response(status="success", message="Secret stored successfully").dict()
    except Exception as e:
        return Response(status="error", message=f"Error in store_secret with exception {e}").dict()

def store_tenant_secret(tenant_id: str, sub_path: str, secret_name: str, secret_data: SecretData, credentials: dict):
    mount_path = "tenant"
    try:
        vault_controller = VaultController(mount_path, credentials)
        if vault_controller is None:
            return Response(status="error", message="VaultController not initialized").dict()
        vault_controller.store_secret(tenant_id, sub_path, secret_name, secret_data)
        return Response(status="success", message="Secret stored successfully").dict()
    except Exception as e:
        return Response(status="error", message=f"Error in store_secret with exception {e}").dict()

def get_service_secret(root_path: str, sub_path: str, secret_name: str, credentials: dict):
    mount_path = "secret"
    try:
        vault_controller = VaultController(mount_path, credentials)
        if vault_controller is None:
            return Response(status="error", message="VaultController not initialized").dict()
        secret = vault_controller.get_secret(root_path, sub_path, secret_name)
        if secret is None:
            return Response(status="error", message="Secret not found").dict()
        return Response(status="success", message="Secret fetched successfully", data=secret).dict()
    except hvac.exceptions.Forbidden:
        return Response(status="error", message="Vault Server permission denied").dict()
    except hvac.exceptions.VaultError as e:
        return Response(status="error", message="Secret not found").dict()
    except ValueError as e:
        return Response(status="error", message=f"{e}").dict()
    except Exception as e:
        return Response(status="error", message=f"Error in get_secret with exception {e}").dict()

def get_tenant_secret(tenant_id: str, sub_path: str, secret_name: str, credentials: dict):
    mount_path = "tenant"
    try:
        vault_controller = VaultController(mount_path, credentials)
        if vault_controller is None:
            return Response(status="error", message="VaultController not initialized").dict()
        secret = vault_controller.get_secret(tenant_id, sub_path, secret_name)
        if secret is None:
            return Response(status="error", message="Secret not found").dict()
        return Response(status="success", message="Secret fetched successfully", data=secret).dict()
    except hvac.exceptions.Forbidden:
        return Response(status="error", message="Vault Server permission denied").dict()
    except hvac.exceptions.VaultError as e:
        return Response(status="error", message="Secret not found").dict()
    except ValueError as e:
        return Response(status="error", message=f"{e}").dict()
    except Exception as e:
        return Response(status="error", message=f"Error in get_secret with exception {e}").dict()

def update_service_secret(root_path: str, sub_path: str, secret_name: str, secret_data: SecretData, credentials: dict):
    mount_path = "secret"
    try:
        vault_controller = VaultController(mount_path, credentials)
        if vault_controller is None:
            return Response(status="error", message="VaultController not initialized").dict()
        resp_dict = vault_controller.update_secret(root_path, sub_path, secret_name, secret_data)
        if resp_dict and "status" in resp_dict:
            return Response(status=resp_dict["status"], message=resp_dict["message"]).dict()
        return Response(status="success", message="Secret updated successfully").dict()
    except Exception as e:
        return Response(status="error", message=f"Error in update_secret with exception {e}").dict()

def update_tenant_secret(tenant_id: str, sub_path: str, secret_name: str, secret_data: SecretData, credentials: dict):
    mount_path = "tenant"
    try:
        vault_controller = VaultController(mount_path, credentials)
        if vault_controller is None:
            return Response(status="error", message="VaultController not initialized").dict()
        resp_dict = vault_controller.update_secret(tenant_id, sub_path, secret_name, secret_data)
        if resp_dict and "status" in resp_dict:
            return Response(status=resp_dict["status"], message=resp_dict["message"]).dict()
        return Response(status="success", message="Secret updated successfully").dict()
    except Exception as e:
        return Response(status="error", message=f"Error in update_secret with exception {e}").dict()

def delete_service_secret(root_path: str, sub_path: str, secret_name: str, credentials: dict):
    mount_path = "secret"
    try:
        vault_controller = VaultController(mount_path, credentials)
        if vault_controller is None:
            return Response(status="error", message="VaultController not initialized").dict()
        resp_dict = vault_controller.delete_secret(root_path, sub_path, secret_name)
        if resp_dict and "status" in resp_dict:
            return Response(status=resp_dict["status"], message=resp_dict["message"]).dict()
        return Response(status="success", message="Secret deleted successfully").dict()
    except Exception as e:
        return Response(status="error", message=f"Error in delete_secret with exception {e}").dict()

def delete_tenant_secret(tenant_id: str, sub_path: str, secret_name: str, credentials: dict):
    mount_path = "tenant"
    try:
        vault_controller = VaultController(mount_path, credentials)
        if vault_controller is None:
            return Response(status="error", message="VaultController not initialized").dict()
        resp_dict = vault_controller.delete_secret(tenant_id, sub_path, secret_name)
        if resp_dict and "status" in resp_dict:
            return Response(status=resp_dict["status"], message=resp_dict["message"]).dict()
        return Response(status="success", message="Secret deleted successfully").dict()
    except Exception as e:
        return Response(status="error", message=f"Error in delete_secret with exception {e}").dict()

def list_all_secrets(root_path: str, credentials: dict):
    mount_path = "secret"
    try:
        vault_controller = VaultController(mount_path, credentials)
        if vault_controller is None:
            return Response(status="error", message="VaultController not initialized").dict()
        return vault_controller.list_all_secrets(root_path)
    except Exception as e:
        return Response(status="error", message=f"Error in list_all_secrets with exception {e}").dict()

def get_all_service_level_secrets(credentials: dict):
    mount_path = "secret"
    try:
        vault_controller = VaultController(mount_path, credentials)
        return vault_controller.get_all_secrets()
    except Exception as e:
        return Response(status="error", message=f"Error in get_all_secrets with exception {e}").dict()

def get_all_tenant_level_secrets(credentials: dict):
    mount_path = "tenant"
    try:
        vault_controller = VaultController(mount_path, credentials)
        return vault_controller.get_all_secrets()
    except Exception as e:
        return Response(status="error", message=f"Error in get_all_secrets with exception {e}").dict()