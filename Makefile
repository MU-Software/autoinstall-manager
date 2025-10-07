export DOCKER_DEFAULT_PLATFORM=linux/amd64

INPUT_DIR_NAME := input
OUTPUT_DIR_NAME := output

UBUNTU_ISO_NAME := ubuntu-24.04.3-live-server-amd64.iso
OUTPUT_ISO_NAME := ubuntu-autoinstall.iso

AUTOINSTALL_JSONSCHEMA := autoinstall-schema.json
AUTOINSTALL_PYDANTIC_MODEL := schemas.py

# ================= Path Definitions ==================
MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
PROJECT_DIR := $(dir $(MKFILE_PATH))

DOCKER_INPUT_DIR := /${INPUT_DIR_NAME}/
DOCKER_OUTPUT_DIR := /${OUTPUT_DIR_NAME}/
DOCKER_UBUNTU_ISO := $(DOCKER_INPUT_DIR)$(UBUNTU_ISO_NAME)
DOCKER_OUTPUT_ISO := $(DOCKER_OUTPUT_DIR)$(OUTPUT_ISO_NAME)
DOCKER_AUTOINSTALL_JSONSCHEMA := $(DOCKER_OUTPUT_DIR)$(AUTOINSTALL_JSONSCHEMA)
DOCKER_AUTOINSTALL_PYDANTIC_MODEL := $(DOCKER_OUTPUT_DIR)$(AUTOINSTALL_PYDANTIC_MODEL)

LOCAL_INPUT_DIR := $(PROJECT_DIR)${INPUT_DIR_NAME}/
LOCAL_OUTPUT_DIR := $(PROJECT_DIR)${OUTPUT_DIR_NAME}/
LOCAL_UBUNTU_ISO := $(LOCAL_INPUT_DIR)$(UBUNTU_ISO_NAME)
LOCAL_OUTPUT_ISO := $(LOCAL_OUTPUT_DIR)$(OUTPUT_ISO_NAME)
LOCAL_AUTOINSTALL_JSONSCHEMA := $(LOCAL_OUTPUT_DIR)$(AUTOINSTALL_JSONSCHEMA)
LOCAL_AUTOINSTALL_PYDANTIC_MODEL := $(LOCAL_OUTPUT_DIR)$(AUTOINSTALL_PYDANTIC_MODEL)

AUTOINSTALL_MANAGER_FRONTEND_DIR := $(PROJECT_DIR)frontend/
AUTOINSTALL_MANAGER_BACKEND_DIR := $(PROJECT_DIR)backend/
AUTOINSTALL_MANAGER_BACKEND_SRC_DIR := $(AUTOINSTALL_MANAGER_BACKEND_DIR)src/
AUTOINSTALL_MANAGER_INFRA_DIR := $(PROJECT_DIR)infrastructures/
AUTOINSTALL_MANAGER_INFRA_LOCAL := $(AUTOINSTALL_MANAGER_INFRA_DIR)docker-compose.dev.yaml

DOTENV_DIR := $(PROJECT_DIR)dotenv/
DOTENV_LOCAL := $(DOTENV_DIR).env.local

BIOS := $(LOCAL_INPUT_DIR)DEBUGX64_OVMF.fd
BIOS_DOWNLOAD_URL := https://raw.githubusercontent.com/retrage/edk2-nightly/refs/heads/master/bin/DEBUGX64_OVMF.fd

# ================= Docker Images ==================
tool-build-image:
	@docker build -f ./dockerfiles/image-tools.dockerfile --platform linux/amd64 -t image-tools $(PROJECT_DIR)

# ================= cloud-init ==================
cloudinit-validate-subiquity: tool-build-image
	@docker run --rm \
		--platform linux/amd64 \
		-v $(PROJECT_DIR)/subiquity_autoinstall.yaml:/subiquity_autoinstall.yaml \
		image-tools /subiquity/scripts/validate-autoinstall-user-data.py /subiquity_autoinstall.yaml -vvv

cloudinit-build-jsonschema: tool-build-image
	@rm -f $(LOCAL_AUTOINSTALL_JSONSCHEMA)
	@docker run --rm \
		--platform linux/amd64 \
		-v $(LOCAL_OUTPUT_DIR):/output \
		image-tools cp /subiquity/autoinstall-schema.json $(DOCKER_AUTOINSTALL_JSONSCHEMA)

cloudinit-build-pydantic-model:
	@rm -f $(LOCAL_AUTOINSTALL_PYDANTIC_MODEL)
	@docker run --rm \
		-v $(LOCAL_AUTOINSTALL_JSONSCHEMA):$(DOCKER_AUTOINSTALL_JSONSCHEMA):ro \
		-v $(LOCAL_OUTPUT_DIR):/output \
		koxudaxi/datamodel-code-generator \
			--input $(DOCKER_AUTOINSTALL_JSONSCHEMA) \
			--input-file-type jsonschema \
			--output $(DOCKER_AUTOINSTALL_PYDANTIC_MODEL) \
			--enum-field-as-literal all \
			--field-constraints \
			--use-annotated \
			--use-standard-collections \
			--use-union-operator \
			--use-title-as-name \
			--use-unique-items-as-set

# ================= ISO Build ==================
bios-download:
	mkdir -p $(LOCAL_INPUT_DIR)
	if [ ! -f "$(BIOS)" ]; then curl -L -o "$(BIOS)" "$(BIOS_DOWNLOAD_URL)"; \
	else echo "$(BIOS) already exists, skipping download."; \
	fi

iso-build: tool-build-image
	@docker run --privileged --rm -it \
		--platform linux/amd64 \
	    -v $(PROJECT_DIR)/subiquity_autoinstall.yaml:/user-data:ro \
	    -v $(LOCAL_UBUNTU_ISO):$(DOCKER_UBUNTU_ISO):ro \
	    -v $(LOCAL_OUTPUT_DIR):$(DOCKER_OUTPUT_DIR):rw \
		-e UBUNTU_ISO_PATH=$(DOCKER_UBUNTU_ISO) \
		-e OUTPUT_ISO_PATH=$(DOCKER_OUTPUT_ISO) \
		image-tools /ubuntu_iso_builder.sh

iso-report-original-el-torito: tool-build-image
	@docker run --privileged --rm -it -v $(LOCAL_UBUNTU_ISO):$(DOCKER_UBUNTU_ISO):ro image-tools xorriso -indev $(DOCKER_UBUNTU_ISO) -report_el_torito

iso-report-modified-el-torito: tool-build-image
	@docker run --privileged --rm -it -v $(LOCAL_OUTPUT_ISO):$(DOCKER_OUTPUT_ISO):ro image-tools xorriso -indev $(DOCKER_OUTPUT_ISO) -report_el_torito

iso-boot-original: bios-download
	@qemu-system-x86_64 \
		-device ich9-ahci,id=sata \
		-drive id=cdrom,if=none,format=raw,media=cdrom,file="$(LOCAL_UBUNTU_ISO)" \
		-device ide-cd,bus=sata.2,drive=cdrom \
		-bios $(BIOS) -m 4096 -boot order=d -machine q35 -serial stdio -smbios type=1,serial=ABC123456789

iso-boot-modified: bios-download
	@qemu-system-x86_64 \
		-debugcon file:ovmf.log -global isa-debugcon.iobase=0x402 \
		-device ich9-ahci,id=sata \
		-drive id=cdrom,if=none,format=raw,media=cdrom,file="$(LOCAL_OUTPUT_ISO)" \
		-device ide-cd,bus=sata.2,drive=cdrom \
		-bios $(BIOS) -m 4096 -boot order=d -machine q35 -serial stdio -smbios type=1,serial=ABC123456789

# ================= Autoinstall manager project ==================
local-lint:
	@uv run pre-commit run --all-files

local-mypy:
	@uv run pre-commit run mypy --all-files

# ================= Autoinstall manager backend ==================
MIGRATION_MESSAGE ?= `date +"%Y%m%d_%H%M%S"`
UPGRADE_VERSION ?= head
DOWNGRADE_VERSION ?= -1

ifeq (makemigration,$(firstword $(MAKECMDGOALS)))
  MIGRATION_MESSAGE := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(MIGRATION_MESSAGE):;@:)
endif
MIGRATION_MESSAGE := $(if $(MIGRATION_MESSAGE),$(MIGRATION_MESSAGE),migration)

local-infra-up:
	@docker compose --env-file $(DOTENV_LOCAL) -f $(AUTOINSTALL_MANAGER_INFRA_LOCAL) up -d

local-infra-down:
	@docker compose --env-file $(DOTENV_LOCAL) -f $(AUTOINSTALL_MANAGER_INFRA_LOCAL) down

local-infra-rm: local-infra-down
	@docker compose --env-file $(DOTENV_LOCAL) -f $(AUTOINSTALL_MANAGER_INFRA_LOCAL) rm

local-backend-db-drop: local-infra-up
	@ENV_FILE=$(DOTENV_LOCAL) uv run alembic downgrade base

local-backend-db-makemigration: local-infra-up
	@ENV_FILE=$(DOTENV_LOCAL) uv run alembic revision --autogenerate -m $(MIGRATION_MESSAGE)

local-backend-db-upgrade: local-infra-up
	@ENV_FILE=$(DOTENV_LOCAL) uv run alembic upgrade $(UPGRADE_VERSION)

local-backend-db-downgrade: local-infra-up
	@ENV_FILE=$(DOTENV_LOCAL) uv run alembic downgrade $(DOWNGRADE_VERSION)

local-backend-hook-install:
	@uv run pre-commit install

local-backend-hook-upgrade:
	@uv run pre-commit run autoupdate

local-backend-run:
	@ENV_FILE=$(DOTENV_LOCAL) uv run python -m backend

local-backend-cli:
	@ENV_FILE=$(DOTENV_LOCAL) uv run python -m backend.cli --help

# Usage: make local-backend-cli-<command> [-- <args...>]
# Example: make local-backend-cli-db-reset -- --create-tables
local-backend-cli-%:
	@if [[ -z "$*" || "$*" == '.o' ]]; then echo "Usage: make local-backend-cli-<command> [-- <args...>]"; exit 1; fi
	@ENV_FILE=$(DOTENV_LOCAL) uv run python -m backend.cli $* $(filter-out $@ --,$(MAKECMDGOALS))

# ================= Autoinstall manager frontend ==================
local-frontend-install:
	@pnpm install

local-frontend-run:
	@pnpm run dev

local-frontend-build:
	@pnpm run build
