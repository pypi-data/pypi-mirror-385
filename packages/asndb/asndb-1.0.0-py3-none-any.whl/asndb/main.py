import re
import json
import typer
from contextlib import contextmanager

from asndb.asndb import ASNDB


app = typer.Typer()

asn_regex = re.compile(r"^(?:AS)?(\d+)$", re.IGNORECASE)


@contextmanager
def asndb_cli_context():
    client = ASNDB()
    try:
        yield client
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command(help="Lookup ASN by IP address")
def ip(
    ip_or_asn: str = typer.Argument(..., help="IP address to lookup"),
):
    with asndb_cli_context() as client:
        asn = client.lookup_ip_sync(ip_or_asn)
        print(json.dumps(asn, indent=2))


@app.command(help="Lookup ASN by AS number")
def asn(
    asn: str = typer.Argument(..., help="AS number to lookup"),
):
    as_number = int(asn_regex.match(asn).group(1))
    with asndb_cli_context() as client:
        asn = client.lookup_asn_sync(as_number)
        print(json.dumps(asn, indent=2))


@app.command(help="Get all the ASNs for an organization, by its registered organization ID, e.g. GOGL-ARIN")
def org(
    org: str = typer.Argument(..., help="Organization to lookup, e.g. GOGL-ARIN or CLOUD14-ARIN"),
):
    with asndb_cli_context() as client:
        org = client.lookup_org_sync(org)
        print(json.dumps(org, indent=2))


def main():
    app()


if __name__ == "__main__":
    main()
