from hashlib import sha256
from operator import itemgetter
from pathlib import Path
from typing import Literal, TypedDict

from httpx import AsyncClient, AsyncHTTPTransport

UBUNTU_SERIES_LIST_URL = "https://api.launchpad.net/devel/ubuntu/series"

transport = AsyncHTTPTransport(retries=3)


class UbuntuSeriesEntry(TypedDict):
    # There are more fields, but we only care about these
    version: str  # e.g., "23.04", "22.04", etc.
    description: str
    name: str  # short codename. e.g., "questing", "plucky", etc.
    title: str  # full codename. e.g., "The Questing Quokka", "The Plucky Puffin", etc.
    status: Literal["Current Stable Release", "Obsolete", "Pre-release Freeze", "Supported"] | str


class UbuntuSeriesAPIResponse(TypedDict):
    start: int
    total_size: int
    entries: list[UbuntuSeriesEntry]


async def list_ubuntu_iso_versions(lts: bool = False) -> list[str]:
    async with AsyncClient(transport=transport) as client:
        resp: UbuntuSeriesAPIResponse = (await client.get("https://api.launchpad.net/devel/ubuntu/series")).raise_for_status().json()

    versions = [
        entry["version"]
        for entry in resp["entries"]
        if entry["status"] in ("Current Stable Release", "Supported")
        # LTS versions are released every 2 years in April
        and (not lts or (entry["version"].endswith(".04") and int(entry["version"].split(".")[0]) % 2 == 0))
    ]
    return sorted(versions, reverse=True)


async def download_latest_ubuntu_iso(destination: Path, lts: bool = True, print_progress: bool = False) -> Path:
    calculated_sha256 = sha256()
    destination.mkdir(parents=True, exist_ok=True)

    if not (versions := await list_ubuntu_iso_versions(lts=lts)):
        raise Exception("No supported Ubuntu versions found.")

    target_lts_version = versions[0]
    target_lts_sha256sums_url = f"https://releases.ubuntu.com/{target_lts_version}/SHA256SUMS"

    async with AsyncClient(transport=transport) as client:
        target_lts_sha256sums_resp = (await client.get(target_lts_sha256sums_url)).raise_for_status()
        target_lts_sha256sums_lines = [line for line in target_lts_sha256sums_resp.text.splitlines() if "live-server-amd64" in line]
        target_lts_sha256sums: list[list[str]] = sorted(map(str.split, target_lts_sha256sums_lines), key=itemgetter(1), reverse=True)

        target_iso_sha256, target_iso_filename = target_lts_sha256sums[0]
        target_iso_filename = target_iso_filename.replace("*", "").strip()

        iso_url = f"https://releases.ubuntu.com/{target_lts_version}/{target_iso_filename}"
        iso_path: Path = destination / target_iso_filename

        if iso_path.exists():
            print(f"{target_iso_filename} already exists. Verifying checksum...")
            with iso_path.open("rb") as f:
                while chunk := f.read(8192):
                    calculated_sha256.update(chunk)
        else:
            async with client.stream("GET", iso_url) as response:
                total = int(response.headers["Content-Length"])
                if print_progress:
                    print(f"Downloading {target_iso_filename} ({total} bytes)...")

                async for chunk in response.aiter_bytes(chunk_size=8192):
                    with iso_path.open("ab") as f:
                        f.write(chunk)

                    calculated_sha256.update(chunk)

                    if print_progress:
                        percent = response.num_bytes_downloaded / total * 100
                        print(f"\r{percent:.2f}%", end="", flush=True)

    print(f"{calculated_sha256.hexdigest()=}  {target_iso_sha256=}")
    if calculated_sha256.hexdigest() != target_iso_sha256:
        iso_path.unlink(missing_ok=True)
        raise Exception("SHA256 checksum mismatch. Download may be corrupted. File has been deleted.")

    return iso_path
