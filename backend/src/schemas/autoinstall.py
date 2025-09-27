from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BaseModel, ConfigDict, Field


class Reporting(BaseModel):
    type: str

    model_config = ConfigDict(extra="allow")


class RefreshInstaller(BaseModel):
    update: bool | None = None
    channel: str | None = None

    model_config = ConfigDict(extra="forbid")


class KernelCase1(BaseModel):
    package: str | None = None
    flavor: str


class KernelCase2(BaseModel):
    package: str
    flavor: str | None = None


class KernelCrashDumps(BaseModel):
    enabled: bool

    model_config = ConfigDict(extra="forbid")


class Keyboard(BaseModel):
    layout: str
    variant: str | None = None
    toggle: str | None = None

    model_config = ConfigDict(extra="forbid")


class Zdev(BaseModel):
    id: str | None = None
    enabled: bool | None = None


class Source(BaseModel):
    search_drivers: bool | None = None
    id: str | None = None


class Match(BaseModel):
    name: str | None = None
    macaddress: str | None = None
    driver: str | None = None

    model_config = ConfigDict(extra="forbid")


class Ethernets(BaseModel):
    match: Match | None = None


class Wifis(BaseModel):
    match: Match | None = None


class Network(BaseModel):
    version: Literal[2]
    ethernets: Ethernets | None = None
    wifis: Wifis | None = None
    bridges: dict[str, Any] | None = None
    bonds: dict[str, Any] | None = None
    tunnels: dict[str, Any] | None = None
    vlans: dict[str, Any] | None = None


class Ethernets1(BaseModel):
    match: Match | None = None


class Wifis1(BaseModel):
    match: Match | None = None


class Network2(BaseModel):
    version: Literal[2]
    ethernets: Ethernets1 | None = None
    wifis: Wifis1 | None = None
    bridges: dict[str, Any] | None = None
    bonds: dict[str, Any] | None = None
    tunnels: dict[str, Any] | None = None
    vlans: dict[str, Any] | None = None


class Network1(BaseModel):
    network: Network2


class UbuntuPro(BaseModel):
    token: Annotated[
        str | None,
        Field(
            description=(
                "A valid token starts with a C and is followed by 23 to 29 Base58 characters.\n"
                "See https://pkg.go.dev/github.com/btcsuite/btcutil/base58#CheckEncode"
            ),
            max_length=30,
            min_length=24,
            pattern="^C[1-9A-HJ-NP-Za-km-z]+$",
        ),
    ] = None


class Primary(BaseModel):
    uri: str
    arches: list[str] | None = None


class MirrorSelection(BaseModel):
    primary: list[Literal["country-mirror"] | Primary] | None = None


class Preference(BaseModel):
    package: str
    pin: str
    pin_priority: Annotated[int, Field(alias="pin-priority")]


class Apt(BaseModel):
    preserve_sources_list: bool | None = None
    primary: list | None = None
    mirror_selection: Annotated[MirrorSelection | None, Field(alias="mirror-selection")] = None
    geoip: bool | None = None
    sources: dict[str, Any] | None = None
    disable_components: list[Literal["universe", "multiverse", "restricted", "contrib", "non-free"]] | None = None
    preferences: list[Preference] | None = None
    fallback: Literal["abort", "continue-anyway", "offline-install"] | None = None


class Identity(BaseModel):
    realname: str | None = None
    username: str
    hostname: str
    password: str

    model_config = ConfigDict(extra="forbid")


class Ssh(BaseModel):
    install_server: Annotated[bool | None, Field(alias="install-server")] = None
    authorized_keys: Annotated[list[str] | None, Field(alias="authorized-keys")] = None
    allow_pw: Annotated[bool | None, Field(alias="allow-pw")] = None


class Snap(BaseModel):
    name: str
    channel: str | None = None
    classic: bool | None = None

    model_config = ConfigDict(extra="forbid")


class ActiveDirectory(BaseModel):
    admin_name: Annotated[str | None, Field(alias="admin-name")] = None
    domain_name: Annotated[str | None, Field(alias="domain-name")] = None

    model_config = ConfigDict(extra="forbid")


class Codecs(BaseModel):
    install: bool | None = None


class Drivers(BaseModel):
    install: bool | None = None


class Oem(BaseModel):
    install: bool | Literal["auto"]


class Autoinstall(BaseModel):
    version: Literal[1]

    interactive_sections: Annotated[list[str] | None, Field(alias="interactive-sections")] = None
    early_commands: Annotated[list[list[str]] | None, Field(alias="early-commands")] = None
    error_commands: Annotated[list[list[str]] | None, Field(alias="error-commands")] = None
    late_commands: Annotated[list[list[str]] | None, Field(alias="late-commands")] = None
    refresh_installer: Annotated[RefreshInstaller | None, Field(alias="refresh-installer")] = None

    kernel_crash_dumps: Annotated[KernelCrashDumps | None, Field(alias="kernel-crash-dumps")] = None
    reporting: dict[str, Reporting] | None = None
    shutdown: Literal["reboot", "poweroff"] | None = None

    timezone: str | None = None
    locale: str | None = None
    keyboard: Keyboard | None = None

    packages: list[str] | None = None
    debconf_selections: Annotated[str | None, Field(alias="debconf-selections")] = None
    apt: Apt | None = None
    snaps: list[Snap] | None = None
    source: Source | None = None
    codecs: Codecs | None = None
    drivers: Drivers | None = None
    oem: Oem | None = None
    updates: Literal["security", "all"] | None = None
    kernel: KernelCase1 | KernelCase2 | None = None

    network: Network | Network1 | None = None
    proxy: AnyUrl | None = None

    storage: dict[str, Any] | None = None
    zdevs: list[Zdev] | None = None

    user_data: Annotated[dict[str, Any] | None, Field(alias="user-data")] = None

    identity: Identity | None = None
    ssh: Ssh | None = None
    active_directory: Annotated[ActiveDirectory | None, Field(alias="active-directory")] = None

    ubuntu_pro: Annotated[UbuntuPro | None, Field(alias="ubuntu-pro")] = None

    model_config = ConfigDict(extra="allow")

    def export(self, mode: Literal["json", "python"] = "python") -> dict[str, Any]:
        return self.model_dump(mode=mode, by_alias=True, exclude_none=True, exclude_unset=True)
