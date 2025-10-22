from slurpit.apis.baseapi import BaseAPI
from slurpit.utils.utils import handle_response_data

class ScraperAPI(BaseAPI):
    def __init__(self, base_url, api_key, verify):
        """
        Initializes a new instance of the ScraperAPI class, which extends BaseAPI. This class is designed to interact with scraper-related endpoints of an API.

        Args:
            base_url (str): The root URL for the API endpoints.
            api_key (str): The API key used for authenticating requests.
            verfify (bool): Verify HTTPS Certificates.
        """
        formatted_url = "{}/api".format(base_url if base_url[-1] != "/" else base_url[:-1])  # Format the base URL to ensure it ends with '/api'
        self.base_url = formatted_url  # Set the formatted base URL
        super().__init__(api_key, verify)

    async def scrape(self, batch_id: int, offset: int = 0, limit: int = 1000, export_csv: bool = False, export_df: bool = False):
        """
        Retrieves scraped data for a specific batch ID from the scraper endpoint and optionally exports the data to CSV format or pandas DataFrame.

        Args:
            batch_id (int): The ID of the batch to retrieve data for.
            offset (int, optional): The offset for pagination. Defaults to 0.
            limit (int, optional): The maximum number of records to retrieve. Defaults to 1000.
            export_csv (bool): If True, returns the scraped data in CSV format as bytes. If False, returns it as a dictionary.
            export_df (bool): If True, returns the scraped data as a pandas DataFrame.

        Returns:
            dict | bytes | pd.DataFrame: A dictionary containing scraped data if successful, bytes if exporting to CSV,
                                        or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/scraper/{batch_id}"
        response = await self._pager(url, offset=offset, limit=limit)
        return handle_response_data(response, export_csv=export_csv, export_df=export_df)


    async def scrape_planning(self, planning_id: int, offset: int = 0, limit: int = 1000, export_csv: bool = False, export_df: bool = False):
        """
        Retrieve all unique data for a given planning ID from the scraper endpoint and optionally exports the data to CSV format or pandas DataFrame.

        Args:
            planning_id (int): The ID of the planning to retrieve data for.
            offset (int, optional): The offset for pagination. Defaults to 0.
            limit (int, optional): The maximum number of records to retrieve. Defaults to 1000.
            export_csv (bool): If True, returns the scraped planning data in CSV format as bytes.
            export_df (bool): If True, returns the scraped planning data as a pandas DataFrame.

        Returns:
            dict | bytes | pd.DataFrame: A dictionary containing scraped planning data if successful, bytes if exporting to CSV,
                                        or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/scraper/planning/{planning_id}"
        response = await self._pager(url, offset=offset, limit=limit)
        return handle_response_data(response, export_csv=export_csv, export_df=export_df)

    async def scrape_planning_ips(self, planning_id: int, date: str = None, offset: int = 0, limit: int = 1000):
        """
        Retrieves IP addresses related to a specific planning ID and date from the scraper endpoint.

        Args:
            planning_id (int): The ID of the planning to retrieve IP addresses for.
            date (str, optional): The date for which to retrieve IP addresses. Defaults to None.
            offset (int): The starting index of the records to fetch.
            limit (int): The maximum number of records to return in one call.
            
        Returns:
            dict: A dictionary containing IP addresses related to the planning if the request is successful.
        """
        url = f"{self.base_url}/scraper/planning_ips/{planning_id}/{date}"
        response = await self._pager(url, offset=offset, limit=limit)
        return response

    async def scrape_planning_ipam(self, planning_id: int = None, date: str = None, offset: int = 0, limit: int = 1000):
        """
        Retrieve all IPs for a given planning id new then given datetime value

        Args:
            planning_id (int, optional): The ID of the planning to retrieve IP addresses for.
            date (str, optional): The date for which to retrieve IP addresses. Defaults to None.
            offset (int): The starting index of the records to fetch.
            limit (int): The maximum number of records to return in one call.
            
        Returns:
            dict: A dictionary containing IP addresses related to the planning if the request is successful.
        """
        # Base endpoint
        url = f"{self.base_url}/scraper/planning_ipam"

        # Append planning_id to the URL if provided
        if planning_id is not None:
            url += f"/{planning_id}"
      
        response = await self._pager(url, offset=offset, limit=limit)
        return response


    async def scrape_planning_by_hostname(self, planning_id: int, hostname: str, offset: int = 0, limit: int = 1000, export_csv: bool = False, export_df: bool = False):
        """
        Retrieves all unique data for a specific planning ID and hostname from the scraper endpoint, optionally exporting the data to CSV or pandas DataFrame.

        Args:
            planning_id (int): The ID of the planning to retrieve data for.
            hostname (str): The hostname to filter the data by.
            offset (int, optional): The offset for pagination. Defaults to 0.
            limit (int, optional): The maximum number of records to retrieve. Defaults to 1000.
            export_csv (bool): If True, returns the data in CSV format as bytes.
            export_df (bool): If True, returns the data as a pandas DataFrame.

        Returns:
            dict | bytes | pd.DataFrame: A dictionary containing scraped planning data if successful, bytes if exporting to CSV,
                                        or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/scraper/planning/{planning_id}/{hostname}"
        response = await self._pager(url, offset=offset, limit=limit)
        return handle_response_data(response, export_csv=export_csv, export_df=export_df)


    async def scrape_device(self, hostname: str, offset: int = 0, limit: int = 1000, export_csv: bool = False, export_df: bool = False):
        """
        Retrieves scraped data for a specific hostname from the scraper endpoint, optionally exporting the data to CSV or pandas DataFrame.

        Args:
            hostname (str): The hostname to retrieve data for.
            offset (int, optional): The offset for pagination. Defaults to 0.
            limit (int, optional): The maximum number of records to retrieve. Defaults to 1000.
            export_csv (bool): If True, returns the data in CSV format as bytes.
            export_df (bool): If True, returns the data as a pandas DataFrame.

        Returns:
            dict | bytes | pd.DataFrame: A dictionary containing scraped data if successful, bytes if exporting to CSV,
                                        or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/scraper/device/{hostname}"
        response = await self._pager(url, offset=offset, limit=limit)
        return handle_response_data(response, export_csv=export_csv, export_df=export_df)

    async def scrape_batches_latest(self, export_csv: bool = False, export_df: bool = False):
        """
        Retrieves the latest batch IDs and their corresponding planning IDs, optionally exporting the data to CSV or pandas DataFrame.

        Args:
            export_csv (bool): If True, returns the data in CSV format as bytes.
            export_df (bool): If True, returns the data as a pandas DataFrame.

        Returns:
            dict | bytes | pd.DataFrame: A dictionary containing the latest scraped batches if successful, bytes if exporting to CSV,
                                        or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/scraper/batches/latest"
        response = await self.get(url)
        return handle_response_data(response, export_csv=export_csv, export_df=export_df)

    async def scrape_batches(self, planning_id: int, hostname: str, export_csv: bool = False, export_df: bool = False):
        """
        Retrieves a list of all batch IDs and timestamps for the specified hostname and planning ID, optionally exporting the data to CSV or pandas DataFrame.

        Args:
            planning_id (int): The ID of the planning to retrieve data for.
            hostname (str): The hostname to retrieve data for.
            export_csv (bool): If True, returns the data in CSV format as bytes.
            export_df (bool): If True, returns the data as a pandas DataFrame.

        Returns:
            dict | bytes | pd.DataFrame: A dictionary containing scraped batches if successful, bytes if exporting to CSV,
                                        or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/scraper/batches/hostname/{hostname}/{planning_id}"
        response = await self.get(url)
        return handle_response_data(response, export_csv=export_csv, export_df=export_df)

    async def start_scraper(self, scraper_info: dict):
        """
        Start the Data Collector.

        Args:
            scraper_info (dict): Information required to start the scraper. \n
                                The dictionary should include the following keys: \n
                                - "hostnames" (list of str): A list of hostnames to scrape data from.
                                - "planning_id" (int): The unique identifier of the planning.

        Returns:
            dict: A dictionary containing the result of the scraper initiation if successful.
        """
        url = f"{self.base_url}/scraper"
        response = await self.post(url, scraper_info)
        if response:
            started_result = response.json()
            return started_result

    async def clean_logs(self, datetime: str):
        """
        Cleans results and logging older than given datetime.

        Args:
            datetime (str): The datetime to clean logs for. (yyyy-mm-dd hh:mm)

        Returns:
            dict: A dictionary containing the result of the log cleaning if successful.
        """
        request_data = {
            "datetime": datetime
        }
        url = f"{self.base_url}/scraper/clean"
        response = await self.post(url, request_data)
        if response:
            clean_result = response.json()
            return clean_result

    async def get_status(self):
        """
        Retrieves the status of the scraper.

        Returns:
            dict: A dictionary containing the status of the scraper if successful.
        """
        url = f"{self.base_url}/scraper/status"
        response = await self.get(url)
        if response:
            scraper_status = response.json()
            return scraper_status

    async def get_queue_list(self, offset: int = 0, limit: int = 1000, export_csv: bool = False, export_df: bool = False):
        """
        Gives a list of currently queued tasks for the scraper and optionally exports the data to CSV format or pandas DataFrame.

        Args:
            offset (int): The starting index of the records to fetch.
            limit (int): The maximum number of records to return in one call.
            export_csv (bool): If True, returns the queued tasks data in CSV format as bytes.
            export_df (bool): If True, returns the queued tasks data as a pandas DataFrame.

        Returns:
            list[dict] | bytes | pd.DataFrame: A list of queued tasks if successful, bytes if exporting to CSV,
                                            or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/scraper/queue/list"
        response = await self._pager(url, offset=offset, limit=limit)
        return handle_response_data(response, export_csv=export_csv, export_df=export_df)

    async def clear_queue(self):
        """
        Clears the queue of the scraper by sending a DELETE request to the queue list endpoint.

        Returns:
            dict: The result of clearing the queue if successful.
        """
        url = f"{self.base_url}/scraper/queue/clear"
        response = await self.delete(url)
        if response:
            clear_result = response.json()
            return clear_result
