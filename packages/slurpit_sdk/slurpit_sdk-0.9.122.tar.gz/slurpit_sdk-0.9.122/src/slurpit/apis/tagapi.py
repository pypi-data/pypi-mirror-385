from slurpit.apis.baseapi import BaseAPI
from slurpit.models.tag import Tag, TagRule
from slurpit.utils.utils import handle_response_data

class TagAPI(BaseAPI):
    def __init__(self, base_url, api_key, verify):
        """
        Initializes a new instance of TagAPI, extending the BaseAPI class.
        Sets up the base URL for API calls specific to tags and initializes authentication.

        Args:
            base_url (str): The root URL for the tag-related API endpoints.
            api_key (str): The API key used for authenticating requests.
            verfify (bool): Verify HTTPS Certificates.
        """
        formatted_url = "{}/api".format(base_url if base_url[-1] != "/" else base_url[:-1])
        self.base_url = formatted_url
        super().__init__(api_key, verify)

    # TAGS
    async def get_tags(self, offset: int = 0, limit: int = 1000, export_csv: bool = False, export_df: bool = False):
        """
        Retrieves a list of tags from the API.

        Args:
            offset (int): The starting index of the records to fetch.
            limit (int): The maximum number of records to return in one call.
            export_csv (bool): If True, returns the tag data in CSV format as bytes.
                               If False, returns a list of Tag objects.
            export_df (bool): If True, returns the tag data as a pandas DataFrame.

        Returns:
            list[Tag] | bytes | pd.DataFrame: A list of Tag objects, CSV bytes, or DataFrame depending on flags.
        """
        url = f"{self.base_url}/tags"
        response = await self._pager(url, offset=offset, limit=limit)
        return handle_response_data(response, Tag, export_csv, export_df)

    async def create_tag(self, tag_data: dict):
        """
        Creates a new tag in the system.

        Args:
            tag_data (dict): A dictionary containing tag attributes.
                             Expected keys:
                             - "name" (str): Name of the tag.
                             - "type" (str): Type of the tag (e.g., "device").

        Returns:
            Tag: A newly created Tag instance if successful.
        """
        url = f"{self.base_url}/tags"
        response = await self.post(url, tag_data)
        if response:
            tag_data = response.json()
            return Tag(**tag_data)

    async def get_tag(self, tag_id: int):
        """
        Fetches a single tag by its ID.

        Args:
            tag_id (int): The unique identifier of the tag to retrieve.

        Returns:
            Tag: A Tag instance if successful.
        """
        url = f"{self.base_url}/tags/{tag_id}"
        response = await self.get(url)
        if response:
            tag_data = response.json()
            return Tag(**tag_data)

    async def update_tag(self, tag_id: int, tag_data: dict):
        """
        Updates a specific tag using its ID.

        Args:
            tag_id (int): The unique identifier of the tag to update.
            tag_data (dict): A dictionary containing the updated tag attributes.
                             Expected keys:
                             - "name" (str): Name of the tag.
                             - "type" (str): Type of the tag (e.g., "device").

        Returns:
            Tag: An updated Tag instance if successful.
        """
        url = f"{self.base_url}/tags/{tag_id}"
        response = await self.put(url, tag_data)
        if response:
            tag_data = response.json()
            return Tag(**tag_data)

    async def delete_tag(self, tag_id: int):
        """
        Deletes a tag using its ID.

        Args:
            tag_id (int): The unique identifier of the tag to delete.

        Returns:
            Tag: A Tag instance representing the deleted tag if successful.
        """
        url = f"{self.base_url}/tags/{tag_id}"
        response = await self.delete(url)
        if response:
            tag_data = response.json()
            return Tag(**tag_data)

    async def reset_devices(self):
        """
        Resets the devices associated with tags.

        Returns:
            dict: the result of the reset operation.
        """
        url = f"{self.base_url}/tags/reset_devices"
        response = await self.post(url, {})
        return response.json()

    # TAG RULES
    async def get_tagrules(self, offset: int = 0, limit: int = 1000, export_csv: bool = False, export_df: bool = False):
        """
        Retrieves a list of tag rules from the API.

        Args:
            offset (int): The starting index of the records to fetch.
            limit (int): The maximum number of records to return in one call.
            export_csv (bool): If True, returns the tag rule data in CSV format as bytes.
                               If False, returns a list of TagRule objects.
            export_df (bool): If True, returns the tag rule data as a pandas DataFrame.

        Returns:
            list[TagRule] | bytes | pd.DataFrame: A list of TagRule objects, CSV bytes, or DataFrame depending on flags.
        """
        url = f"{self.base_url}/tags/tagrules"
        response = await self._pager(url, offset=offset, limit=limit)
        return handle_response_data(response, TagRule, export_csv, export_df)

    async def create_tagrule(self, tagrule_data: dict):
        """
        Creates a new tag rule in the system.

        Args:
            tagrule_data (dict): A dictionary containing the tag rule attributes.
                                 Expected keys:
                                 - "rule" (str): The rule to be applied.
                                 - "applied_to" (str): The element to which the rule is applied (e.g., "hostname").
                                 - "rule_order" (int): The order of the rule.
                                 - "tag_id" (int): The ID of the tag to which the rule is applied.
                                 - "disabled" (int): Whether the rule is disabled.

        Returns:
            TagRule: A newly created TagRule instance if successful.
        """
        url = f"{self.base_url}/tags/tagrules"
        response = await self.post(url, tagrule_data)
        if response:
            tagrule_data = response.json()
            return TagRule(**tagrule_data)

    async def delete_tagrule(self, tagrule_id: int):
        """
        Deletes a tag rule using its ID.

        Args:
            tagrule_id (int): The unique identifier of the tag rule to delete.

        Returns:
            TagRule: A TagRule instance representing the deleted tag rule if successful.
        """
        url = f"{self.base_url}/tags/tagrules/{tagrule_id}"
        response = await self.delete(url)
        if response:
            tagrule_data = response.json()
            return TagRule(**tagrule_data)

    async def test_tagrule(self, data: dict):
        """
        Tests a tag rule to verify which tag a device would be added to by providing device info.

        Args:
            data (dict): Test payload containing:
                         - "test_string" (str): The value to test against the rules (e.g., "hostname").
                         - "applyTo" (str): The attribute to which the rule applies (e.g., hostname,fqdn, device_os, device_type, ipv4).

        Returns:
            dict: test results with tag if found.
        """
        url = f"{self.base_url}/tags/tagrules/test"
        response = await self.post(url, data)
        return response.json()
