import json
import os
import logging
from typing import TypedDict, NotRequired

class Profile(TypedDict):
    host: str
    port: int
    TLS: bool
    name: str
    ca_authority: NotRequired[str | None]


class ProfileConfig(TypedDict):
    profiles: list[Profile]
    default_profile: str
    default_username: str
    default_password: str | None
    auto_login: bool

    
class Profiles:
    def __init__(self):
        self.log: logging.Logger = logging.getLogger("indralib.server_config")
        self.profile_file: str = os.path.expanduser("~/.config/indrajala/servers.json")
        def_config: ProfileConfig = {"profiles": [
                                {
                                    "name": "default",
                                    "host": "localhost",
                                    "port": 8080,
                                    "TLS": False,
                                    "ca_authority": ""
                                },
                            ],
                            "default_profile": "default",
                            "default_username": "stat",
                            "default_password": None,
                            "auto_login": False,
                        }
        if not os.path.exists(os.path.dirname(self.profile_file)):
            os.makedirs(os.path.dirname(self.profile_file))
        if not os.path.exists(self.profile_file):
            with open(self.profile_file, "w") as f:
                _ = f.write(
                    json.dumps(def_config,
                        indent=4,
                    )
                )
            self.log.error("Default configuration written to {self.profile_file}, please edit!")
        with open(self.profile_file, "rb") as f:
            try:
                raw_profiles: ProfileConfig = json.load(f)  # pyright: ignore[reportAny]
            except Exception as e:
                self.log.error(f"Error reading profiles from {self.profile_file}: {e}")
                raw_profiles = def_config
        for index, profile in enumerate(raw_profiles["profiles"]):
            if not self.check_profile(profile):
                self.log.error(f"Invalid profile: {profile} in {self.profile_file}")
                del raw_profiles["profiles"][index]
        self.profiles: list[Profile] = raw_profiles["profiles"]
        self.default_profile: str = raw_profiles["default_profile"]
        self.default_username: str = raw_profiles["default_username"]
        self.default_password: str | None = raw_profiles["default_password"]
        self.auto_login: bool = raw_profiles["auto_login"]

    def get_profiles(self):
        return self.profiles

    def get_default_profile(self):
        return self.get_profile(self.default_profile)

    def get_profile(self, profile_name: str):
        for profile in self.profiles:
            if profile["name"] == profile_name:
                return profile
        return None

    @staticmethod
    def check_profile(profile: Profile):
        optional_keys = ["ca_authority"]
        for key in optional_keys:
            if key not in profile:
                profile[key] = ""

    @staticmethod
    def get_uri(profile: Profile):
        uri = "ws"
        if profile.get("TLS", False):
            uri += "s"
        uri += f"://{profile['host']}:{profile['port']}/ws"
        return uri

    def save_profiles(self):
        # check for duplicate names
        names: list[str] = []
        for profile in self.profiles:
            while profile["name"] in names:
                new_name = profile["name"] + " (copy)"
                self.log.warning(
                    f"Duplicate profile name: {profile['name']}, changing to {new_name}"
                )
                profile["name"] = new_name
            names.append(profile["name"])
        raw_profiles = {
            "profiles": self.profiles,
            "default_profile": self.default_profile,
            "default_username": self.default_username,
            "default_password": self.default_password,
            "auto_login": self.auto_login,
        }
        with open(self.profile_file, "w") as f:
            try:
                json.dump(raw_profiles, f, indent=4)
            except Exception as e:
                self.log.error(f"Error saving profiles: {e}")
