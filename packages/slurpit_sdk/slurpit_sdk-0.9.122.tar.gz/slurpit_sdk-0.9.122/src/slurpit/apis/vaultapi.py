from slurpit.apis.baseapi import BaseAPI
from slurpit.models.vault import Vault, SingleVault
from slurpit.models.sshgroup import SshGroup, SingleSshGroup
from slurpit.models.snmpcredential import VaultSnmpCredentials, SingleVaultSnmpCredentials
from slurpit.models.snmpgroup import VaultSnmpGroup, SingleVaultSnmpGroup
from slurpit.utils.utils import handle_response_data

class VaultAPI(BaseAPI):
    def __init__(self, base_url, api_key, verify):
        """
        Initializes a new instance of the VaultAPI class.

        Args:
            base_url (str): The base URL for the Vault API.
            api_key (str): The API key used for authentication.
            verfify (bool): Verify HTTPS Certificates.
        """
        formatted_url = "{}/api".format(base_url if base_url[-1] != "/" else base_url[:-1])  # Format the base URL to ensure it ends with '/api'
        self.base_url = formatted_url  # Set the formatted base URL
        super().__init__(api_key, verify)  # Initializes the BaseAPI with the provided API key

    async def get_vault_ssh_credentials(self, offset: int = 0, limit: int = 1000, group_id: int = None, export_csv: bool = False, export_df: bool = False):
        """
        Fetches a list of all vault ssh credentials from the API and returns them as a list of Vault objects.
        Optionally exports the data to a CSV format or pandas DataFrame if specified.

        Args:
            offset (int): The starting index of the records to fetch.
            limit (int): The maximum number of records to return in one call.
            group_id (int): The ID of the group to filter by.
            export_csv (bool): If True, returns the vault data in CSV format as bytes.
            export_df (bool): If True, returns the vault data as a pandas DataFrame.

        Returns:
            list[Vault] | bytes | pd.DataFrame: Returns a list of Vault objects if successful, bytes if exporting to CSV,
                                            or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/vault/credentials/ssh"
        payload = {"group_id": group_id} if group_id is not None else {}
        response = await self._pager(url, offset=offset, limit=limit, payload=payload)
        return handle_response_data(response, Vault, export_csv, export_df)
        
    async def get_vault_ssh_credential(self, vault_id: int):
        """
        Fetches a single vault ssh credential by its ID.

        Args:
            vault_id (int): The ID of the vault ssh credential to retrieve.

        Returns:
            SingleVault: Returns a SingleVault object if the fetch is successful.
        """
        url = f"{self.base_url}/vault/credentials/ssh/{vault_id}"
        response = await self.get(url)
        if response:
            vault_data = response.json()
            return SingleVault(**vault_data)

    async def create_vault_ssh_credential(self, new_vault: dict):
        """
        Creates a new vault ssh credential with the specified data.

        Args:
            new_vault (dict): A dictionary containing the data for the new vault. \n
                            The dictionary should include the following keys: \n
                            - "username" (str): The username for the vault ssh credential.
                            - "password" (str): The password for the vault ssh credential.
                            - "ssh_key" (str): The SSH key for the vault ssh credential.
                            - "ssh_key_passphrase" (str): The passphrase for the SSH key.
                            - "enable_password" (str): The enable password for the vault ssh credential.
                            - "device_os" (str): The operating system associated with the vault ssh credential.
                            - "comment" (str): Any additional comments or notes about the vault ssh credential.
                            - "group_id" (int): The ID of the group to which the vault ssh credential belongs.

        Returns:
            SingleVault: Returns a SingleVault object if the creation is successful.
        """
        url = f"{self.base_url}/vault/credentials/ssh"
        response = await self.post(url, new_vault)
        if response:
            vault_data = response.json()
            return SingleVault(**vault_data)

    async def update_vault_ssh_credential(self, vault_id: int, update_data: dict):
        """
        Updates a vault ssh credential with specified data.

        Args:
            vault_id (int): The ID of the vault ssh credential to update.
            update_data (dict): A dictionary containing the data to update in the vault. \n
                                The dictionary should include the following keys: \n
                                - "username" (str): The username for the vault.
                                - "password" (str): The password for the vault.
                                - "ssh_key" (str): The SSH key for the vault.
                                - "ssh_key_passphrase" (str): The passphrase for the SSH key.
                                - "enable_password" (str): The enable password for the vault.
                                - "device_os" (str): The operating system associated with the vault.
                                - "comment" (str): Any additional comments or notes about the vault.
                                - "group_id" (int): The ID of the group to which the vault ssh credential belongs.

        Returns:
            SingleVault: Returns a SingleVault object if the update is successful.
        """
        url = f"{self.base_url}/vault/credentials/ssh/{vault_id}"
        response = await self.put(url, update_data)
        if response:
            vault_data = response.json()
            return SingleVault(**vault_data)
    
    async def delete_vault_ssh_credential(self, vault_id: int):
        """
        Deletes a vault ssh credential by its ID.

        Args:
            vault_id (int): The ID of the vault ssh credential to delete.

        Returns:
            SingleVault: Returns a SingleVault object if the deletion is successful.
        """
        url = f"{self.base_url}/vault/credentials/ssh/{vault_id}"
        response = await self.delete(url)
        if response:
            vault_data = response.json()
            return SingleVault(**vault_data)


    # SSH GROUPS
    async def get_ssh_groups(self, offset: int = 0, limit: int = 1000, export_csv: bool = False, export_df: bool = False):
        """
        Retrieve a list of SSH groups.

        Args:
            offset (int): Starting index for pagination.
            limit (int): Max number of records to return.
            export_csv (bool): If True, returns the SSH group data in CSV format as bytes.
            export_df (bool): If True, returns the SSH group data as a pandas DataFrame.

        Returns:
            list[SshGroup] | bytes | pd.DataFrame: Returns a list of SshGroup objects if successful, bytes if exporting to CSV,
                                            or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/vault/groups/ssh"
        response = await self._pager(url, offset=offset, limit=limit)
        return handle_response_data(response, SshGroup, export_csv, export_df)

    async def get_ssh_group(self, group_id: int):
        """
        Retrieve a single SSH group by ID.

        Args:
            group_id (int): The unique identifier of the SSH group.

        Returns:
            SshGroup: SSH group object if found.
        """
        url = f"{self.base_url}/vault/groups/ssh/{group_id}"
        response = await self.get(url)
        if response:
            group_data = response.json()
            return SingleSshGroup(**group_data)

    async def update_ssh_group(self, group_id: int, update_data: dict):
        """
        Update an existing SSH group by ID.

        Args:
            group_id (int): The unique identifier of the SSH group to update.
            update_data (dict): Fields to update for the group.

        Returns:
            SshGroup: Updated SSH group object.
        """
        url = f"{self.base_url}/vault/groups/ssh/{group_id}"
        response = await self.put(url, update_data)
        if response:
            group_data = response.json()
            return SshGroup(**group_data)

    async def delete_ssh_group(self, group_id: int):
        """
        Delete an existing SSH group by ID.

        Args:
            group_id (int): The unique identifier of the SSH group to delete.

        Returns:
            SshGroup: Result of the delete operation.
        """
        url = f"{self.base_url}/vault/groups/ssh/{group_id}"
        response = await self.delete(url)
        if response:
            group_data = response.json()
            return SshGroup(**group_data)

    async def create_ssh_group(self, group_data: dict):
        """
        Create a new SSH group.

        Args:
            group_data (dict): Payload for creating the SSH group.

        Returns:
            SshGroup: Created SSH group object.
        """
        url = f"{self.base_url}/vault/groups/ssh"
        response = await self.post(url, group_data)
        if response:
            group_data = response.json()
            return SshGroup(**group_data)
    

    # vault SNMP CREDENTIALS
    async def get_snmp_credentials(self, offset: int = 0, limit: int = 1000, group_id: int = None, export_csv: bool = False, export_df: bool = False):
        """
        Retrieve a list of vault SNMP credentials from the vault.

        Args:
            offset (int): Starting index for pagination.
            limit (int): Max number of records to return.
            group_id (int, optional): Filter by Snmp group ID.
            export_csv (bool): If True, returns the vault SNMP credential data in CSV format as bytes.
            export_df (bool): If True, returns the vault SNMP credential data as a pandas DataFrame.

        Returns:
            list[VaultSnmpCredentials] | bytes | pd.DataFrame: Returns a list of VaultSnmpCredentials objects if successful, bytes if exporting to CSV,
                                            or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/vault/credentials/snmp"
        payload = {"group_id": group_id} if group_id is not None else {}
        response = await self._pager(url, offset=offset, limit=limit, payload=payload)
        return handle_response_data(response, VaultSnmpCredentials, export_csv, export_df)

    async def create_snmp_credential(self, credential_data: dict):
        """
        Create a new vault SNMP credential in the vault.

        Args:
            credential_data (dict): Payload for creating the vault SNMP credential.

        Returns:
            SingleVaultSnmpCredentials: Created vault SNMP credential object.
        """
        url = f"{self.base_url}/vault/credentials/snmp"
        response = await self.post(url, credential_data)
        if response:
            credential_data = response.json()
            return SingleVaultSnmpCredentials(**credential_data)

    async def get_snmp_credential(self, vault_snmp_id: int):
        """
        Retrieve a single vault SNMP credential by ID.

        Args:
            vault_snmp_id (int): The unique identifier of the vault SNMP credential.

        Returns:
            SingleVaultSnmpCredentials: vault SNMP credential object if found.
        """
        url = f"{self.base_url}/vault/credentials/snmp/{vault_snmp_id}"
        response = await self.get(url)
        if response:
            credential_data = response.json()
            return SingleVaultSnmpCredentials(**credential_data)

    async def update_snmp_credential(self, vault_snmp_id: int, update_data: dict):
        """
        Update an existing vault SNMP credential by ID.

        Args:
            vault_snmp_id (int): The unique identifier of the vault SNMP credential to update.
            update_data (dict): Fields to update for the vault SNMP credential.

        Returns:
            SingleVaultSnmpCredentials: Updated vault SNMP credential object.
        """
        url = f"{self.base_url}/vault/credentials/snmp/{vault_snmp_id}"
        response = await self.put(url, update_data)
        if response:
            credential_data = response.json()
            return SingleVaultSnmpCredentials(**credential_data)

    async def delete_snmp_credential(self, vault_snmp_id: int):
        """
        Delete an existing vault SNMP credential by ID.

        Args:
            vault_snmp_id (int): The unique identifier of the vault SNMP credential to delete.

        Returns:
            SingleVaultSnmpCredentials: Result of the delete operation.
        """
        url = f"{self.base_url}/vault/credentials/snmp/{vault_snmp_id}"
        response = await self.delete(url)
        if response:
            credential_data = response.json()
            return SingleVaultSnmpCredentials(**credential_data)

    # VAULT SNMP GROUPS
    async def get_snmp_groups(self, offset: int = 0, limit: int = 1000, export_csv: bool = False, export_df: bool = False):
        """
        Retrieve a list of vault SNMP groups.

        Args:
            offset (int): Starting index for pagination.
            limit (int): Max number of records to return.
            export_csv (bool): If True, returns the vault SNMP group data in CSV format as bytes.
            export_df (bool): If True, returns the vault SNMP group data as a pandas DataFrame.

        Returns:
            list[VaultSnmpGroup] | bytes | pd.DataFrame: Returns a list of VaultSnmpGroup objects if successful, bytes if exporting to CSV,
                                            or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/vault/groups/snmp"
        response = await self._pager(url, offset=offset, limit=limit)
        return handle_response_data(response, VaultSnmpGroup, export_csv, export_df)

    async def create_snmp_group(self, group_data: dict):
        """
        Create a new vault SNMP group.

        Args:
            group_data (dict): Payload for creating the vault SNMP group.

        Returns:
            VaultSnmpGroup: Created vault SNMP group object.
        """
        url = f"{self.base_url}/vault/groups/snmp"
        response = await self.post(url, group_data)
        if response:
            group_data = response.json()
            return VaultSnmpGroup(**group_data)

    async def get_snmp_group(self, group_id: int):
        """
        Retrieve a single vault SNMP group by ID.

        Args:
            group_id (int): The unique identifier of the vault SNMP group.

        Returns:
            VaultSnmpGroup: vault SNMP group object if found.
        """
        url = f"{self.base_url}/vault/groups/snmp/{group_id}"
        response = await self.get(url)
        if response:
            group_data = response.json()
            return SingleVaultSnmpGroup(**group_data)

    async def update_snmp_group(self, group_id: int, update_data: dict):
        """
        Update an existing vault SNMP group by ID.

        Args:
            group_id (int): The unique identifier of the vault SNMP group to update.
            update_data (dict): Fields to update for the vault SNMP group.

        Returns:
            VaultSnmpGroup: Updated vault SNMP group object.
        """
        url = f"{self.base_url}/vault/groups/snmp/{group_id}"
        response = await self.put(url, update_data)
        if response:
            group_data = response.json()
            return VaultSnmpGroup(**group_data)

    async def delete_snmp_group(self, group_id: int):
        """
        Delete an existing vault SNMP group by ID.

        Args:
            group_id (int): The unique identifier of the vault SNMP group to delete.

        Returns:
            VaultSnmpGroup: Result of the delete operation.
        """
        url = f"{self.base_url}/vault/groups/snmp/{group_id}"
        response = await self.delete(url)
        if response:
            group_data = response.json()
            return VaultSnmpGroup(**group_data)
    
