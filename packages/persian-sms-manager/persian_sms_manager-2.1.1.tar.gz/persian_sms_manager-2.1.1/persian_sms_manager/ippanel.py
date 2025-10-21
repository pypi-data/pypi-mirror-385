import requests
from typing import Optional, Union

from .base import BaseSMSService


class IPPanelService(BaseSMSService):
    """
    A service for sending SMS messages using the ippanel.com API.

    Attributes:
        api_url (str): The base URL for the API.
        api_key (str): The API key for authentication.
        sender_number (str): The sender's line number.
    """

    api_url = "http://api2.ippanel.com/api/v1"

    def __init__(self, user_mobile: str, api_key: str, sender_number: str, **kwargs) -> None:
        """
        Initializes the IPPanelService.

        Args:
            user_mobile (str): The user's (recipient's) mobile number.
            api_key (str): The ippanel API key.
            sender_number (str): Your dedicated line number in the panel.
        """
        super().__init__(user_mobile, **kwargs)
        self.api_key: str = api_key
        self.sender_number: str = sender_number

    def get_headers(self) -> dict:
        """
        Creates the standard authorization header for all requests.
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"AccessKey {self.api_key}",
        }

    def send_request(self, endpoint: str, data: dict) -> bool:
        """
        Sends a request to the API.

        Args:
            endpoint (str): The API endpoint (e.g., /sms/send/...).
            data (dict): The data to be sent as JSON.

        Returns:
            bool: True if the request was successful, otherwise False.
        """
        try:
            response = requests.post(
                f"{self.api_url}{endpoint}", 
                json=data, 
                headers=self.get_headers()
            )
            # According to ippanel docs, 200 and 201 status codes indicate success
            return response.status_code in [200, 201]
        except requests.RequestException:
            return False

    def send_message(self, message: str) -> bool:
        """
        Sends a simple text message.
        """
        endpoint = "/sms/send/webservice/single"
        data = {
            "recipient": [self.user_mobile],
            "sender": self.sender_number,
            "message": message,
        }
        return self.send_request(endpoint, data)

    def send_auto_otp_code(self) -> bool:
        """
        Sends an auto-generated OTP code.
        The ippanel API generates and sends the code.
        """
        endpoint = "/sms/verification/send/code"
        data = {
            "receptor": self.user_mobile,
            "sender": self.sender_number,
        }
        return self.send_request(endpoint, data)

    def check_auto_otp_code(self, otp_code: Union[str, int]) -> bool:
        """
        Verifies the sent OTP code.
        """
        endpoint = "/sms/verification/check/code"
        data = {
            "receptor": self.user_mobile,
            "code": str(otp_code),
        }
        return self.send_request(endpoint, data)