import json
import os
import time

import requests
from dotenv import load_dotenv

from .logger import logger

load_dotenv()


class ProxyManager:
    """
    Manages proxy discovery and rotation.

    Iterates ports of the proxy.market pool, verifies geo-location via
    ip-api.com, and tracks used IPs to avoid reuse.
    """

    PROXY_SERVER     = "pool.proxy.market"
    PROXY_PORT_START = 10000
    PROXY_PASSWORD   = os.environ["PROXY_PASSWORD"]
    MAX_ATTEMPTS     = 1000

    def __init__(self, proxies_file: str, used_ips_file: str):
        self._proxies_file  = proxies_file
        self._used_ips_file = used_ips_file

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def find_proxy(self, country: str) -> dict | None:
        """
        Find an unused proxy for the given country code.
        Returns a dict with geo data and credentials, or None on failure.
        """
        try:
            logger.info(f"Finding proxy for country: {country}")
            credentials = self._load_credentials()

            if country not in credentials:
                logger.error(f"No proxy credentials found for country: {country}")
                return None

            username = credentials[country]["username"]
            used_ips = self._load_used_ips()

            for i in range(self.MAX_ATTEMPTS):
                port = self.PROXY_PORT_START + i
                try:
                    logger.debug(f"Trying proxy port: {port}")
                    info = self._get_proxy_info(port, username)
                    if not info:
                        continue

                    ip = info["ip"]
                    if ip not in used_ips:
                        self._save_used_ip(ip)
                        info["credentials"] = {
                            "server":   f"http://{self.PROXY_SERVER}:{port}",
                            "username": username,
                            "password": self.PROXY_PASSWORD,
                        }
                        logger.info(f"Found suitable proxy with IP: {ip}")
                        return info

                    logger.debug(f"IP {ip} already used, trying next port")
                    time.sleep(1)

                except Exception as e:
                    logger.exception(e, f"Error trying proxy port {port}")
                    continue

            logger.error(
                f"Failed to find suitable proxy for country '{country}' "
                f"after {self.MAX_ATTEMPTS} attempts"
            )
            return None

        except Exception as e:
            logger.exception(e, f"Unexpected error finding proxy for country '{country}'")
            return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_proxy_info(self, port: int, username: str) -> dict | None:
        """Query ip-api.com through the proxy and return geo data."""
        try:
            proxy_url = f"http://{username}:{self.PROXY_PASSWORD}@{self.PROXY_SERVER}:{port}"
            proxies   = {"http": proxy_url, "https": proxy_url}

            logger.debug(f"Requesting ip-api.com via port {port}...")
            response = requests.get("http://ip-api.com/json/", proxies=proxies)
            response.raise_for_status()
            data = response.json()

            return {
                "ip":          data["query"],
                "country":     data["country"],
                "countryCode": data["countryCode"],
                "city":        data["city"],
                "timezone":    data["timezone"],
                "location": {
                    "latitude":  data["lat"],
                    "longitude": data["lon"],
                },
            }

        except requests.RequestException as e:
            logger.exception(e, f"Request error for proxy port {port}")
            return None
        except KeyError as e:
            logger.exception(e, "Missing field in ip-api.com response")
            return None
        except Exception as e:
            logger.exception(e, "Unexpected error getting proxy info")
            return None

    def _load_credentials(self) -> dict:
        try:
            logger.debug("Reading proxy credentials...")
            with open(self._proxies_file) as f:
                data = json.load(f)
            logger.info("Proxy credentials loaded successfully")
            return data
        except FileNotFoundError:
            logger.error(f"Proxy credentials file not found: {self._proxies_file}")
            raise
        except json.JSONDecodeError as e:
            logger.exception(e, "Error parsing proxy credentials file")
            raise

    def _load_used_ips(self) -> list:
        try:
            logger.debug("Reading used IPs file...")
            with open(self._used_ips_file) as f:
                used_ips = json.load(f)
            logger.debug(f"Loaded {len(used_ips)} used IPs")
            return used_ips
        except FileNotFoundError:
            logger.warning("Used IPs file not found, creating new one")
            with open(self._used_ips_file, "w") as f:
                json.dump([], f)
            return []
        except Exception as e:
            logger.exception(e, "Error reading used IPs file")
            raise

    def _save_used_ip(self, ip: str):
        try:
            logger.debug(f"Saving used IP: {ip}")
            used_ips = self._load_used_ips()
            used_ips.append(ip)
            with open(self._used_ips_file, "w") as f:
                json.dump(used_ips, f, indent=4)
            logger.debug("IP saved successfully")
        except Exception as e:
            logger.exception(e, "Error saving used IP")
            raise
