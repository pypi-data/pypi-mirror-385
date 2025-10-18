import os
import time
import asyncio
from contextlib import contextmanager, suppress

import httpx
import cachetools
from radixtarget import RadixTarget


class ASNDBError(Exception):
    pass


class ASNDBTimeoutError(ASNDBError):
    pass


class ASNDBClient:
    BASE_URL = "https://asndb.api.bbot.io/v1"
    DEFAULT_CACHE_SIZE = 10000
    DEFAULT_TIMEOUT = 60

    # Default record used when no ASN data can be found
    UNKNOWN_ASN = {
        "asn": 0,
        "subnets": [],
        "name": "Unknown",
        "description": "Unknown ASN",
        "country": "Unknown",
    }

    def __init__(self, bbot_io_api_key=None):
        self.bbot_io_api_key = os.getenv("BBOT_IO_API_KEY", None) or bbot_io_api_key
        self.base_url = os.getenv("ASNDB_BASE_URL", None) or self.BASE_URL
        self.timeout = int(os.getenv("ASNDB_TIMEOUT", self.DEFAULT_TIMEOUT))
        self.client = httpx.AsyncClient(timeout=self.timeout)

        self.headers = {}
        if self.bbot_io_api_key:
            self.headers["Authorization"] = f"Bearer {self.bbot_io_api_key}"

        self._cache_size = os.getenv("ASNDB_CACHE_SIZE", self.DEFAULT_CACHE_SIZE)
        # IPNetwork -> ASN Number
        self._subnet_cache = RadixTarget()
        # ASN Number -> ASN
        self._asn_cache = cachetools.LRUCache(maxsize=self._cache_size)

        self._event_loop = asyncio.get_event_loop()

    async def request(self, url, **kwargs):
        """
        Make a request to the ASNDB API, respecting its retry-after mechanism.
        """
        start = time.time()
        retry_after = 10
        try:
            while True:
                elapsed = time.time() - start
                if elapsed > self.timeout:
                    raise ASNDBTimeoutError(f"Timeout after {self.timeout} seconds")

                try:
                    response = await self.client.get(url, headers=self.headers, **kwargs)
                except httpx.TimeoutException:
                    continue
                except httpx.HTTPError as e:
                    raise ASNDBError(f"HTTP error: {e}")

                status_code = getattr(response, "status_code", 0)

                if status_code == 200:
                    try:
                        return response.json()
                    except Exception as e:
                        raise ASNDBError(f"Error parsing JSON: {e}")
                elif status_code == 404:
                    return None
                elif status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 10))
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    raise ASNDBError(f"Unexpected status code: {response.status_code}: {response.text}")

        except Exception as e:
            raise ASNDBError(f"Unexpected error while requesting {url}: {e}")

    async def lookup_ip(self, ip: str):
        """
        Given an IP address, return the ASN data and subnet.

        For convenience, will put the parent subnet of the requested IP in the "subnet" key of the returned ASN data.
        """
        try:
            asn_number, subnet = self._cache_get_ip(ip)
            asn = dict(self._cache_get_asn(asn_number))
            asn["subnet"] = subnet
            return asn
        except KeyError:
            url = f"{self.base_url}/ip/{ip}"
            asn = await self.request(url)
            if asn:
                self._cache_put_asn(asn)
                asn = dict(asn)
                with suppress(KeyError):
                    asn_number, subnet = self._cache_get_ip(ip)
                    asn["subnet"] = subnet
                return asn
        return self.UNKNOWN_ASN

    def lookup_ip_sync(self, ip: str):
        return self._event_loop.run_until_complete(self.lookup_ip(ip))

    async def ip_to_subnet(self, ip: str):
        """
        Given an IP address, return the AS number and subnet it belongs to.
        """
        # first make sure we have the ASN data for the IP
        await self.lookup_ip(ip)
        # then get it from the cache
        result = self._cache_get_ip(ip)
        if result is None:
            raise KeyError(f"IP address {ip} not found in cache")
        asn_number, subnet = result
        return asn_number, subnet

    def ip_to_subnet_sync(self, ip: str):
        return self._event_loop.run_until_complete(self.ip_to_subnet(ip))

    async def lookup_asn(self, asn: str):
        try:
            return self._cache_get_asn(asn)
        except KeyError:
            url = f"{self.base_url}/asn/{asn}"
            asn = await self.request(url)
            if asn:
                self._cache_put_asn(asn)
                return asn
        return self.UNKNOWN_ASN

    def lookup_asn_sync(self, asn: str):
        return self._event_loop.run_until_complete(self.lookup_asn(asn))

    async def lookup_org(self, org: str):
        url = f"{self.base_url}/org/{org}"
        return (await self.request(url)) or []

    def lookup_org_sync(self, org: str):
        return self._event_loop.run_until_complete(self.lookup_org(org))

    def _cache_get_ip(self, ip: str) -> tuple[int, str]:
        """
        ip -> asn, subnet
        """
        result = self._subnet_cache.get(ip)
        if result is None:
            raise KeyError(f"IP address {ip} not found in cache")
        asn, subnet = result
        return asn, subnet

    def _cache_get_asn(self, asn: int) -> dict:
        """
        asn number -> asn data
        """
        return self._asn_cache[asn]

    def _cache_put_asn(self, asn: str):
        asn_number = int(asn["asn"])
        for subnet in asn.get("subnets", []):
            self._subnet_cache.add(subnet, data=(asn_number, subnet))
        self._asn_cache[asn_number] = asn

    async def cleanup(self):
        self._asn_cache.clear()
        await self.client.aclose()


asndb_client = None


def ASNDB():
    global asndb_client
    if asndb_client is None:
        asndb_client = ASNDBClient()
    return asndb_client
