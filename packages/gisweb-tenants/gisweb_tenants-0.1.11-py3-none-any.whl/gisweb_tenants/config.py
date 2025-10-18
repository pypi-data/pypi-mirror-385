# gisweb_tenants/config.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from sqlalchemy.engine import make_url
from pathlib import Path
import os

Mode = Literal["development", "testing", "production"]

@dataclass(frozen=True, slots=True)
class TenantsConfig:
    tenants_file: Path                 # path a tenants.yml
    mode: Mode = "development"
    # Verrà usato come application_name: "<APP_NAME_PREFIX>:<tenant>"
    app_name_prefix: str = "fastapi"
    # Il nome database user e pws verranno sovrascritto per-tenant dal registry quando presente.
    async_database_uri: str = "postgresql+asyncpg://postgres:postgres@localhost:6432/postgres"
    echo_sql: bool = False
    pool_size: int = 10
    tenant_header: str = "X-Tenant"
    default_tenant: str = "istanze"
    allowed_tenants_csv: str = "" # "a,b,c"
    strict_whitelist: bool = False  # se True -> 403 se non in allowed
      
    def drivername(self) -> str:
        """
        Ritorna lo scheme del driver, es.:
        - 'postgresql+asyncpg'
        - 'postgresql+psycopg'
        Serve a scegliere dove mettere application_name (server_settings vs connect_args).
        """
        return make_url(self.async_database_uri).drivername
    

@dataclass(frozen=True, slots=True)
class CryptoConfig:
    encrypt_key: bytes  # 32 bytes
    
@dataclass(frozen=True, slots=True)
class DbDefaults:
    scheme: str = "postgresql+asyncpg"
    host: str = "localhost"
    port: int = 6432