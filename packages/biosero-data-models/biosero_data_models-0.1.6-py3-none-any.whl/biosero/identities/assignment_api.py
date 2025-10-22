import requests
import json

class AssignmentAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def assign_resource_to_vessel(self, resource_ref_id: str, vessel_ref_id: str) -> dict:
        """
        Assigns a resource to a vessel.

        :param resource_ref_id: The resource reference ID to be assigned.
        :param vessel_ref_id: The vessel reference ID where the resource will be assigned.
        :return: The API response in JSON format.
        """
        url = f'{self.base_url}/api/identities/v1.0/resources/{resource_ref_id}/assign'
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        payload = {
            "vesselRefId": vessel_ref_id
        }

        return self._make_post_request(url, payload, headers)

    def assign_vessel_to_container(self, vessel_ref_id: str, container_ref_id: str, container_position: str) -> dict:
        """
        Assigns a vessel to a container.

        :param vessel_ref_id: The vessel reference ID to be assigned.
        :param container_ref_id: The container reference ID where the vessel will be assigned.
        :param container_position: The position within the container.
        :return: The API response in JSON format.
        """
        url = f'{self.base_url}/api/identities/v1.0/vessels/{vessel_ref_id}/assign'
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        payload = {
            "containerRefId": container_ref_id,
            "containerPosition": container_position
        }

        return self._make_post_request(url, payload, headers)

    def assign_container_to_device(self, container_ref_id: str, device_ref_id: str, device_position: str) -> dict:
        """
        Assigns a container to a device.

        :param container_ref_id: The container reference ID to be assigned.
        :param device_ref_id: The device reference ID where the container will be assigned.
        :param device_position: The position within the device.
        :return: The API response in JSON format.
        """
        url = f'{self.base_url}/api/identities/v1.0/containers/{container_ref_id}/assign'
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        payload = {
            "deviceRefId": device_ref_id,
            "devicePosition": device_position
        }

        return self._make_post_request(url, payload, headers)

    def assign_device_to_workcell(self, device_ref_id: str, workcell_ref_id: str, workcell_position: str) -> dict:
        """
        Assigns a device to a workcell.

        :param device_ref_id: The device reference ID to be assigned.
        :param workcell_ref_id: The workcell reference ID where the device will be assigned.
        :param workcell_position: The position within the workcell.
        :return: The API response in JSON format.
        """
        url = f'{self.base_url}/api/identities/v1.0/devices/{device_ref_id}/assign'
        print(url)
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        payload = {
            "workcellRefId": workcell_ref_id,
            "workcellPosition": workcell_position
        }
        self.unassign_device(device_ref_id)

        return self._make_post_request(url, payload, headers)
    
    def unassign_device(self, device_ref_id: str) -> dict:
        """
        Assigns a device to a workcell.

        :param device_ref_id: The device reference ID to be assigned.
        :param workcell_ref_id: The workcell reference ID where the device will be assigned.
        :param workcell_position: The position within the workcell.
        :return: The API response in JSON format.
        """
        url = f'{self.base_url}/api/identities/v1.0/devices/{device_ref_id}/assign'
        print(url)
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        payload = {
            # "workcellRefId": "null",
            # "workcellPosition": "null"
        }

        return self._make_post_request(url, payload, headers)

    def assign_container_to_device(self, container_ref_id: str, device_ref_id: str, device_position: str) -> dict:
        """
        Assigns a container to a device.

        :param container_ref_id: The container reference ID to be assigned.
        :param device_ref_id: The device reference ID where the container will be assigned.
        :param device_position: The position within the device.
        :return: The API response in JSON format.
        """
        url = f'{self.base_url}/api/identities/v1.0/Containers/{container_ref_id}/assign'
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        payload = {
            "deviceRefId": device_ref_id,
            "devicePosition": device_position
        }
        # Unassign the device first to avoid conflicts
        self.unassign_container(device_ref_id)
        return self._make_post_request(url, payload, headers)
    
    def unassign_container(self, container_ref_id: str) -> dict:
        """
        Unassigns a container from a device.

        :param container_ref_id: The container reference ID to be unassigned.
        :return: The API response in JSON format.
        """
        url = f'{self.base_url}/api/identities/v1.0/Containers/{container_ref_id}/assign'
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        payload = {
   
        }

        return self._make_post_request(url, payload, headers)
    
    def assign_vessel_to_container(self, vessel_ref_id: str, container_ref_id: str, container_position: str) -> dict:
        """
        Assigns a vessel to a container.

        :param vessel_ref_id: The vessel reference ID to be assigned.
        :param container_ref_id: The container reference ID where the vessel will be assigned.
        :param container_position: The position within the container.
        :return: The API response in JSON format.
        """
        url = f'{self.base_url}/api/identities/v1.0/Vessels/{vessel_ref_id}/assign'
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        payload = {
            "containerRefId": container_ref_id,
            "containerPosition": container_position
        }
        # Unassign the vessel first to avoid conflicts
        self.unassign_vessel(vessel_ref_id)
        
        return self._make_post_request(url, payload, headers)
    


    def unassign_vessel(self, vessel_ref_id: str) -> dict:
        """
        Unassigns a vessel from a container.

        :param vessel_ref_id: The vessel reference ID to be unassigned.
        :return: The API response in JSON format.
        """
        url = f'{self.base_url}/api/identities/v1.0/Vessels/{vessel_ref_id}/assign'
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }
        payload = {}

        return self._make_post_request(url, payload, headers)



    def _make_post_request(self, url: str, payload: dict, headers: dict) -> dict:
        """
        Helper function to make the POST request to the given URL with the provided payload and headers.

        :param url: The URL to which the POST request will be sent.
        :param payload: The data to be sent with the POST request.
        :param headers: The headers to include in the request.
        :return: The API response in JSON format.
        """
        response = requests.post(url, json=payload, headers=headers)

        # Check if the response was successful
        if response.ok:
            return 
        else:
            return {"error": "Request failed", "status_code": response.status_code, "message": response.text}

