# worker-core-lib/src/core_lib/core_lib_auth/credentials_service.py
import json
import logging
import re
from typing import NamedTuple, Dict, Any

from sqlalchemy.orm import Session, joinedload

from .crypto import decrypt
from ..core_lib_db.models import StorageConnection

logger = logging.getLogger(__name__)


def to_snake_case(name: str) -> str:
    """Converts a camelCase string to snake_case."""
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class Credential(NamedTuple):
    """A generic container for credentials."""
    # Google Drive / OAuth
    access_token: str = None
    refresh_token: str = None
    token_type: str = None
    expiry_date: Any = None  # Changed from int to Any for flexibility
    scope: str = None
    # Can hold the full token dictionary for libraries that need it
    token: Dict[str, Any] = None

    # SFTP / Basic Auth
    username: str = None
    password: str = None
    private_key: str = None
    
    # S3 / AWS
    access_key: str = None
    secret_key: str = None


class CredentialsService:
    """
    A service to fetch and decrypt credentials from the database for a given storage connection.
    """
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_credentials_for_connection(self, storage_connection_id: str) -> Credential:
        """
        Fetches and decrypts credentials for a given storage connection ID.
        """
        logger.info(f"Fetching credentials for storage connection ID: {storage_connection_id}")

        connection = (
            self.db_session.query(StorageConnection)
            .options(joinedload(StorageConnection.config))
            .filter(StorageConnection.id == storage_connection_id)
            .one_or_none()
        )

        if not connection:
            raise ValueError(f"StorageConnection with ID '{storage_connection_id}' not found.")
        
        if not connection.config:
            raise ValueError(f"StorageProviderConfig not found for connection ID '{storage_connection_id}'.")

        encrypted_creds = connection.config.encryptedCredentials
        if not encrypted_creds:
            raise ValueError(f"Missing encrypted credentials for connection ID '{storage_connection_id}'.")

        logger.debug(f"Found encrypted credentials: {encrypted_creds}")

        if isinstance(encrypted_creds, str):
            try:
                encrypted_creds = json.loads(encrypted_creds)
            except json.JSONDecodeError:
                raise ValueError("Encrypted credentials are not valid JSON.")
        
        decrypted_creds = {}
        for key, value in encrypted_creds.items():
            if isinstance(value, str):
                try:
                    decrypted_creds[key] = decrypt(value)
                except (ValueError, TypeError) as e:  # Catch TypeError from fromhex
                    logger.error(f"Fatal: Could not decrypt value for key '{key}'. Error: {e}")
                    raise ValueError(f"Decryption failed for key '{key}' in connection '{storage_connection_id}'") from e
            else:
                decrypted_creds[key] = value
        
        # For Google Drive, the entire token object is often stored encrypted.
        if connection.provider == 'google_drive' and 'token' in decrypted_creds and isinstance(decrypted_creds['token'], str):
            try:
                token_data = json.loads(decrypted_creds['token'])
                return Credential(token=token_data)
            except json.JSONDecodeError:
                logger.warning(f"The 'token' field for connection {storage_connection_id} could not be parsed as JSON after decryption.")
        
        # Convert all keys from camelCase to snake_case to match Python model
        snake_case_creds = {to_snake_case(k): v for k, v in decrypted_creds.items()}
        
        # Get the set of valid field names for the Credential NamedTuple
        valid_keys = set(Credential._fields)
        
        # Filter the dictionary to only include keys that are valid fields
        filtered_creds = {k: v for k, v in snake_case_creds.items() if k in valid_keys}
        
        logger.info(f"Successfully decrypted credentials for connection {storage_connection_id}.")
        return Credential(**filtered_creds)