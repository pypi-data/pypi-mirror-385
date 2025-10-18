import json
import pytest
from asndb.asndb import ASNDBClient


class ASNDBTestClient(ASNDBClient):
    def __init__(self, *args, **kwargs):
        self.requested_urls = []
        super().__init__(*args, **kwargs)

    async def request(self, url, **kwargs):
        self.requested_urls.append(url)
        return await super().request(url, **kwargs)


@pytest.mark.asyncio
async def test_asndb():
    asndb = ASNDBTestClient()

    # IP lookup
    asn = await asndb.lookup_ip("1.1.1.1")
    assert asn["asn"] == 13335
    assert asn["asn_name"] == "CLOUDFLARENET"
    assert asn["subnet"] == "1.1.1.0/24"
    assert asndb.requested_urls == ["https://asndb.api.bbot.io/v1/ip/1.1.1.1"]

    # IP to subnet lookup
    asn_number, subnet = await asndb.ip_to_subnet("1.1.1.1")
    assert asn_number == 13335
    assert subnet == "1.1.1.0/24"

    # Bad IP
    asn = await asndb.lookup_ip("127.0.0.1")
    assert asn == ASNDBClient.UNKNOWN_ASN
    assert asndb.requested_urls == [
        "https://asndb.api.bbot.io/v1/ip/1.1.1.1",
        "https://asndb.api.bbot.io/v1/ip/127.0.0.1",
    ]

    # IP lookup with cache
    asn = await asndb.lookup_ip("1.1.1.2")
    assert asn["asn"] == 13335
    assert asn["asn_name"] == "CLOUDFLARENET"
    assert asn["subnet"] == "1.1.1.0/24"
    assert len(asndb.requested_urls) == 2

    # ASN Lookup
    asn = await asndb.lookup_asn(13335)
    assert asn["asn"] == 13335
    assert asn["asn_name"] == "CLOUDFLARENET"
    # we should not have made a second request
    assert len(asndb.requested_urls) == 2

    # Organization Lookup
    org = await asndb.lookup_org("CLOUD14-ARIN")
    assert org["asns"] == [13335, 14789, 395747, 394536]


def test_asndb_sync():
    asndb = ASNDBTestClient()

    # IP lookup
    asn = asndb.lookup_ip_sync("1.1.1.1")
    assert asn["asn"] == 13335
    assert asn["asn_name"] == "CLOUDFLARENET"
    assert asn["subnet"] == "1.1.1.0/24"
    assert len(asndb.requested_urls) == 1

    # IP to subnet lookup
    asn_number, subnet = asndb.ip_to_subnet_sync("1.1.1.1")
    assert asn_number == 13335
    assert subnet == "1.1.1.0/24"

    # Bad IP
    asn = asndb.lookup_ip_sync("127.0.0.1")
    assert asn == ASNDBClient.UNKNOWN_ASN
    assert len(asndb.requested_urls) == 2

    # IP lookup with cache
    asn = asndb.lookup_ip_sync("1.1.1.2")
    assert asn["asn"] == 13335
    assert asn["subnet"] == "1.1.1.0/24"
    assert len(asndb.requested_urls) == 2

    # ASN Lookup
    asn = asndb.lookup_asn_sync(13335)
    assert asn["asn"] == 13335
    assert asn["asn_name"] == "CLOUDFLARENET"
    assert len(asndb.requested_urls) == 2

    # Organization Lookup
    org = asndb.lookup_org_sync("CLOUD14-ARIN")
    assert org["asns"] == [13335, 14789, 395747, 394536]


def test_asndb_cli(monkeypatch, capsys):
    from asndb.main import main
    import sys

    # patch sys.exit to prevent the CLI from actually exiting
    def mock_exit(code=0):
        pass

    monkeypatch.setattr(sys, "exit", mock_exit)

    # patch sys.argv to include the command
    monkeypatch.setattr("sys.argv", ["asndb", "ip", "1.1.1.1"])
    # run the CLI
    main()
    # capture the output
    out, err = capsys.readouterr()
    out_json = json.loads(out.strip())
    assert err == ""
    assert out_json["asn"] == 13335
    assert out_json["asn_name"] == "CLOUDFLARENET"
    assert out_json["subnet"] == "1.1.1.0/24"

    # look up asn
    monkeypatch.setattr("sys.argv", ["asndb", "asn", "13335"])
    main()
    out, err = capsys.readouterr()
    out_json = json.loads(out.strip())
    assert err == ""
    assert out_json["asn"] == 13335
    assert out_json["asn_name"] == "CLOUDFLARENET"

    # look up org
    monkeypatch.setattr("sys.argv", ["asndb", "org", "CLOUD14-ARIN"])
    main()
    out, err = capsys.readouterr()
    out_json = json.loads(out.strip())
    assert err == ""
    assert out_json["asns"] == [13335, 14789, 395747, 394536]
