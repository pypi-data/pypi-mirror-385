import uuid
from sqlalchemy import Column, String, ForeignKey, JSON, Text, Integer, BigInteger, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from dataclasses import dataclass
from typing import Dict

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    storage_connections = relationship("StorageConnection", back_populates="user")

class StorageProviderConfig(Base):
    __tablename__ = "storage_provider_configs"
    id = Column(UUID(as_uuid=True), primary_key=True)
    encryptedCredentials = Column('encryptedCredentials', JSON, nullable=False, default={})

class StorageConnection(Base):
    __tablename__ = "storage_connections"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column('providerType', String)
    user_id = Column('userId', UUID(as_uuid=True), ForeignKey("users.id"))
    storage_provider_config_id = Column('storageProviderConfigId', UUID(as_uuid=True), ForeignKey("storage_provider_configs.id"))
    host = Column(String)
    port = Column(Integer)
    
    user = relationship("User", back_populates="storage_connections")
    config = relationship("StorageProviderConfig")

class Model(Base):
    __tablename__ = 'models'
    id = Column(UUID(as_uuid=True), primary_key=True)
    storage_connection_id = Column(UUID(as_uuid=True), ForeignKey('storage_connections.id'))
    thumbnail_url = Column('thumbnailUrl', String)
    metamodel = Column('metamodel', JSON)

    storage_connection = relationship("StorageConnection")

class StorageItem(Base):
    __tablename__ = 'storage_items'
    id = Column(UUID(as_uuid=True), primary_key=True)
    provider_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    connection_id = Column(UUID(as_uuid=True), ForeignKey('storage_connections.id'))
    platform_model_id = Column(UUID(as_uuid=True), ForeignKey('models.id'))
    size = Column(BigInteger)
    last_modified = Column('lastModified', DateTime)


# Dataclasses for job data remain useful
@dataclass
class FilePath:
    value: str


@dataclass
class DownloadJobData:
    modelId: str
    storageConnectionId: str
    filePath: Dict
    originalJobName: str