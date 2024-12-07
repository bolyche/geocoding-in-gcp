import os
import csv
import json
from pathlib import Path
from typing import Generator, Any

from geocode.geocoder import GeocodeIPs


def yield_ips_from_csv() -> Generator[list[str], Any, None]:
    with open(Path(os.getcwd(), "data/ip_addresses.csv"), "r", newline="") as ips:
        csv_reader = csv.reader(ips)
        for ip in csv_reader:
            yield (ip)


def process_ips(generate_ips) -> None:
    geo = GeocodeIPs()

    with open(Path(os.getcwd(), "data/ip_addresses_output.jsonl"), "a+") as outfile:
        for ip in generate_ips():
            ip_geo = geo.get_ip_geo_unfiltered(*ip)
            if ip_geo:
                json.dump(ip_geo, outfile)
                outfile.write("\n")
                print(ip_geo, "\n")


if __name__ == "__main__":
    process_ips(yield_ips_from_csv)
