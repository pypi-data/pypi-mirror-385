import requests
from typing import Any, Dict
from biosero.identities import Workcell,Device, Vessel, Container, Resource


class Accessioning:
    def __init__(self, base_url: str):
        self.base_url = base_url

    
    def create_workcell(self, workcell: Workcell) -> dict:
        """
        Create a workcell using the provided workcell data. If the workcell already exists, update it instead.
        :param workcell: The data for creating the workcell (Workcell object).
        :return: The API response in JSON format.
        :raises Exception: If an error occurs during the request.
        """
        workcell_data = workcell.to_dict()
        url = f'{self.base_url}/api/identities/v1.0/workcells'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        try:
            return self._make_post_request(url, workcell_data, headers)
        except Exception as e:
            error_message = str(e)

            # Check if the error message contains information about an already existing workcell
            if "Workcell with RefId" in error_message and "already in use" in error_message:
                print(f"Workcell already exists. Attempting to update: {error_message}")
                return self.update_workcell(workcell)  # Call the update method instead of raising an error
            
            raise Exception(f"Failed to create workcell: {error_message}")

    def update_workcell(self, workcell: Workcell) -> dict:

        """
        Update an existing workcell using the provided workcell data.
        :param workcell: The data for updating the workcell (Workcell object).
        :return: The API response in JSON format.
        """
        # Convert the workcell object to a dictionary
        workcell_data = workcell.to_dict()
        
        url = f'{self.base_url}/api/identities/v1.0/workcells/{workcell.workcellRefId}'  # Use the workcellRefId for the endpoint
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        return self._make_put_request(url, workcell_data, headers)
    
    def create_device(self, device: Device) -> dict:
        """
        Create a device using the provided device data. If the device already exists, update it instead.
        :param device: The data for creating the device (Device object).
        :return: The API response in JSON format.
        :raises Exception: If an error occurs during the request.
        """
        device_data = device.to_dict()
        url = f'{self.base_url}/api/identities/v1.0/devices'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        try:
            return self._make_post_request(url, device_data, headers)
        except Exception as e:
            error_message = str(e)

            # Check if the error message contains information about an already existing device
            if "Device with RefId" in error_message and "already in use" in error_message:
                print(f"Device already exists. Attempting to update: {error_message}")
                return self.update_device(device)  # Call the update method instead of raising an error
            
            raise Exception(f"Failed to create device: {error_message}")

    def update_device(self, device: Device) -> dict:
        """
        Update an existing device using the provided device data.
        :param device: The data for updating the device (Device object).
        :return: The API response in JSON format.
        """
        # Convert the device object to a dictionary
        device_data = device.to_dict()
        
        url = f'{self.base_url}/api/identities/v1.0/devices/{device.deviceRefId}'  # Use the deviceRefId for the endpoint
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        return self._make_put_request(url, device_data, headers)

    def create_container(self, container: Container) -> dict:
        """
        Create a container using the provided container data. If the container already exists, update it instead.
        :param
        container: The data for creating the container (Container object).
        :return: The API response in JSON format.
        :raises Exception: If an error occurs during the request.
        """
        container_data = container.to_dict()
        url = f'{self.base_url}/api/identities/v1.0/Containers'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        try:
            return self._make_post_request(url, container_data, headers)
        except Exception as e:
            error_message = str(e)

            # Check if the error message contains information about an already existing container
            if "Container with RefId" in error_message and "already in use" in error_message:
                print(f"Container already exists. Attempting to update: {error_message}")
                return self.update_container(container)
            else:
                raise Exception(f"Failed to create container: {error_message}")
            
    # def update_container(self, container: Container) -> dict:
    #     """
    #     Update an existing container using the provided container data.
    #     :param container: The data for updating the container (Container object).
    #     :return: The API response in JSON format.
    #     """
    #     # Convert the container object to a dictionary
    #     container_data = container.to_dict()
    #     url = f'{self.base_url}/api/identities/v1.0/Containers/{container.containerRefId}'  # Use the containerRefId for the endpoint
    #     headers = {
    #         'accept': 'application/json',
    #         'Content-Type': 'application/json'
    #     }
    #     return self._make_put_request(url, container_data, headers)


    def update_container(self, container: Container) -> dict:
        """
        Update an existing container using the provided container data,
        excluding fields that should not be updated.
        :param container: The data for updating the container (Container object).
        :return: The API response in JSON format.
        """

        IMMUTABLE_FIELDS = {
            'containerRefId',
            'barcode',
            'containerType',
            'rows',
            'columns',
            'positions'
        }

        # Convert to dict and filter out immutable fields
        container_data = {
            k: v for k, v in container.to_dict().items()
            if k not in IMMUTABLE_FIELDS
        }

        url = f'{self.base_url}/api/identities/v1.0/Containers/{container.containerRefId}'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        return self._make_put_request(url, container_data, headers)

    
    def create_vessel(self, vessel: Vessel) -> dict:
        """
        Create a vessel using the provided vessel data. If the vessel already exists, update it instead.
        :param vessel: The data for creating the vessel (Vessel object).
        :return: The API response in JSON format.
        :raises Exception: If an error occurs during the request.
        """
        vessel_data = vessel.to_dict()
        url = f'{self.base_url}/api/identities/v1.0/Vessels'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        try:
            return self._make_post_request(url, vessel_data, headers)
        except Exception as e:
            error_message = str(e)

        # Check if the error message contains information about an already existing vessel
        if "Vessel with VesselRefId " in error_message and "already exists" in error_message:
            print(f"Vessel already exists. Attempting to update: {error_message}")
            return self.update_vessel(vessel)
        else:
            raise Exception(f"Failed to create vessel: {error_message}")

    def update_vessel(self, vessel: Vessel) -> dict:
        """
        Update an existing vessel using the provided vessel data.
        :param vessel: The data for updating the vessel (Vessel object).
        :return: The API response in JSON format.
        """
        vessel_data = vessel.to_dict()
        url = f'{self.base_url}/api/identities/v1.0/Vessels/{vessel.vesselRefId}'  # Use the vesselRefId for the endpoint
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        return self._make_put_request(url, vessel_data, headers)

    def _make_post_request(self, url: str, payload: dict, headers: dict) -> dict:
        """
        Helper function to make a POST request to the given URL with the provided payload and headers.

        :param url: The URL to which the POST request will be sent.
        :param payload: The data to be sent with the POST request.
        :param headers: The headers to include in the request.
        :return: The API response in JSON format or an empty dictionary for 204 responses.
        :raises Exception: If the request fails.
        """
        response = requests.post(url, json=payload, headers=headers)

        if 200 <= response.status_code < 300:  # Check for any successful 2xx response
            return response.json() if response.content else {}  # Avoid JSON decode errors for empty responses

        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

    def _make_put_request(self, url: str, payload: dict, headers: dict) -> dict:
        """
        Helper function to make a PUT request to the given URL with the provided payload and headers.

        :param url: The URL to which the PUT request will be sent.
        :param payload: The data to be sent with the PUT request.
        :param headers: The headers to include in the request.
        :return: The API response in JSON format.
        """
        response = requests.put(url, json=payload, headers=headers)

        if response.status_code == 200:
                return response.json()
        elif response.status_code == 204:  # No Content response
            return {}  # Return an empty dictionary since there's no JSON data
        else:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

