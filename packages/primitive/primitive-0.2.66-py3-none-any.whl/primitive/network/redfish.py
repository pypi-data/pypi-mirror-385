import requests
from typing import Literal


class RedfishClient:
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password

    def create_session_token(self):
        response = requests.post(
            f"https://{self.host}/redfish/v1/SessionService/Sessions",
            json={"UserName": self.username, "Password": self.password},
            verify=False,
        )
        response.raise_for_status()
        return response.headers["X-Auth-Token"]

    def get_systems(self):
        token = self.create_session_token()
        headers = {"X-Auth-Token": token}
        response = requests.get(
            f"https://{self.host}/redfish/v1/Systems",
            headers=headers,
            verify=False,
        )
        response.raise_for_status()
        return response.json()

    def get_system(self, system_id: str):
        token = self.create_session_token()
        headers = {"X-Auth-Token": token}
        response = requests.get(
            f"https://{self.host}/redfish/v1/Systems/{system_id}",
            headers=headers,
            verify=False,
        )
        response.raise_for_status()
        return response.json()

    def update_boot_options(
        self,
        system_id: str,
        boot_source_override_enabled: Literal["Once", "Continuous", "Disabled"],
        boot_source_override_target: Literal[
            "None", "Pxe", "Cd", "Usb", "Hdd", "BiosSetup", "Diags", "UefiTarget"
        ],
        boot_source_override_mode: Literal["UEFI", "Legacy"] = "UEFI",
    ):
        token = self.create_session_token()
        headers = {"X-Auth-Token": token}
        body = {
            "Boot": {
                "BootSourceOverrideTarget": boot_source_override_target,
                "BootSourceOverrideEnabled": boot_source_override_enabled,
                "BootSourceOverrideMode": boot_source_override_mode,
            }
        }
        response = requests.patch(
            f"https://{self.host}/redfish/v1/Systems/{system_id}",
            headers=headers,
            verify=False,
            json=body,
        )
        response.raise_for_status()
        return response.json()

    def get_boot_options(self, system_id: str):
        token = self.create_session_token()
        headers = {"X-Auth-Token": token}
        response = requests.get(
            f"https://{self.host}/redfish/v1/Systems/{system_id}/BootOptions",
            headers=headers,
            verify=False,
        )
        response.raise_for_status()
        return response.json()

    def get_boot_option(self, system_id: str, option_id: str):
        # option_id typically looks like Boot000X
        token = self.create_session_token()
        headers = {"X-Auth-Token": token}
        response = requests.get(
            f"https://{self.host}/redfish/v1/Systems/{system_id}/BootOptions/{option_id}",
            headers=headers,
            verify=False,
        )
        response.raise_for_status()
        return response.json()

    def get_pxe_boot_option(self, system_id: str):
        boot_options = self.get_boot_options(system_id)
        for option in boot_options.get("Members", []):
            option_data = self.get_boot_option(
                system_id, option["@odata.id"].split("/")[-1]
            )
            boot_option_enabled = option_data.get("BootOptionEnabled", False)
            display_name = option_data.get("DisplayName", "")
            if "PXE" in display_name and "IPv4" in display_name and boot_option_enabled:
                return option_data

        return None

    def compute_system_reset(
        self,
        system_id: str,
        reset_type: Literal[
            "ForceRestart", "GracefulRestart", "ForceOff", "PowerCycle"
        ],
    ) -> bool:
        token = self.create_session_token()
        headers = {"X-Auth-Token": token}
        response = requests.post(
            f"https://{self.host}/redfish/v1/Systems/{system_id}/Actions/ComputerSystem.Reset",
            json={"ResetType": reset_type},
            headers=headers,
            verify=False,
        )
        response.raise_for_status()
        return response.status_code == 200
