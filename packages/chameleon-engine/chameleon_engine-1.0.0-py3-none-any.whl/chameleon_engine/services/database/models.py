"""
Database models for fingerprint storage and management.

This module contains SQLAlchemy models for storing browser fingerprint data,
validation results, and collection logs in the database.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Text, Boolean, JSON,
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class FingerprintRecord(Base):
    """Main table for storing browser fingerprint records."""

    __tablename__ = "fingerprints"

    # Primary key and identifiers
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(String(100), unique=True, index=True, nullable=False)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)

    # Browser and system information
    browser_type = Column(String(50), index=True, nullable=False)
    browser_version = Column(String(50), nullable=False)
    operating_system = Column(String(50), index=True, nullable=False)
    user_agent = Column(Text, nullable=False)

    # Profile data stored as JSON
    browser_profile = Column(JSON, nullable=False)

    # Collection metadata
    source_type = Column(String(50), nullable=False)  # "real_world", "synthetic", "hybrid"
    collection_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    collection_metadata = Column(JSON, nullable=True)

    # Quality and validation metrics
    coherence_score = Column(Float, nullable=False)
    detection_risk_score = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False)
    validation_score = Column(Float, nullable=True)

    # Usage tracking
    is_active = Column(Boolean, default=True, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime(timezone=True), nullable=True)
    last_validated = Column(DateTime(timezone=True), nullable=True)

    # Expiration and lifecycle
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    validation_results = relationship("FingerprintValidation", back_populates="fingerprint", cascade="all, delete-orphan")
    usage_logs = relationship("FingerprintUsageLog", back_populates="fingerprint", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_fingerprints_browser_os', 'browser_type', 'operating_system'),
        Index('idx_fingerprints_quality', 'coherence_score', 'quality_score'),
        Index('idx_fingerprints_active_expires', 'is_active', 'expires_at'),
        Index('idx_fingerprints_collection_date', 'collection_date'),
        CheckConstraint('coherence_score >= 0.0 AND coherence_score <= 1.0', name='check_coherence_score'),
        CheckConstraint('detection_risk_score >= 0.0 AND detection_risk_score <= 1.0', name='check_detection_risk'),
        CheckConstraint('quality_score >= 0.0 AND quality_score <= 1.0', name='check_quality_score'),
        CheckConstraint('usage_count >= 0', name='check_usage_count'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'uuid': str(self.uuid) if self.uuid else None,
            'browser_type': self.browser_type,
            'browser_version': self.browser_version,
            'operating_system': self.operating_system,
            'user_agent': self.user_agent,
            'browser_profile': self.browser_profile,
            'source_type': self.source_type,
            'collection_date': self.collection_date.isoformat() if self.collection_date else None,
            'collection_metadata': self.collection_metadata,
            'coherence_score': self.coherence_score,
            'detection_risk_score': self.detection_risk_score,
            'quality_score': self.quality_score,
            'validation_score': self.validation_score,
            'is_active': self.is_active,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'last_validated': self.last_validated.isoformat() if self.last_validated else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FingerprintRecord":
        """Create model from dictionary."""
        return cls(
            profile_id=data.get('profile_id'),
            browser_type=data.get('browser_type'),
            browser_version=data.get('browser_version'),
            operating_system=data.get('operating_system'),
            user_agent=data.get('user_agent'),
            browser_profile=data.get('browser_profile'),
            source_type=data.get('source_type'),
            collection_metadata=data.get('collection_metadata'),
            coherence_score=data.get('coherence_score', 0.0),
            detection_risk_score=data.get('detection_risk_score', 0.0),
            quality_score=data.get('quality_score', 0.0),
            validation_score=data.get('validation_score'),
            is_active=data.get('is_active', True),
            usage_count=data.get('usage_count', 0)
        )


class FingerprintValidation(Base):
    """Table for storing fingerprint validation results."""

    __tablename__ = "fingerprint_validations"

    # Primary key and relationships
    id = Column(Integer, primary_key=True, index=True)
    fingerprint_id = Column(Integer, ForeignKey("fingerprints.id"), nullable=False)

    # Validation information
    validation_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    test_type = Column(String(50), nullable=False)  # "antibot_service", "real_world_test", "synthetic_test"
    test_name = Column(String(100), nullable=True)

    # Results
    result = Column(String(20), nullable=False)  # "passed", "failed", "partial", "warning"
    score = Column(Float, nullable=True)  # 0.0 to 1.0
    confidence = Column(Float, nullable=True)  # Confidence in the result

    # Detailed information
    details = Column(JSON, nullable=True)  # Detailed test results
    error_message = Column(Text, nullable=True)
    warnings = Column(JSON, nullable=True)  # List of warnings

    # Test environment
    test_environment = Column(JSON, nullable=True)  # Environment where test was run
    test_duration_ms = Column(Integer, nullable=True)

    # Relationships
    fingerprint = relationship("FingerprintRecord", back_populates="validation_results")

    # Constraints
    __table_args__ = (
        Index('idx_validations_fingerprint_date', 'fingerprint_id', 'validation_date'),
        Index('idx_validations_test_type_result', 'test_type', 'result'),
        CheckConstraint("result IN ('passed', 'failed', 'partial', 'warning')", name='check_validation_result'),
        CheckConstraint('score >= 0.0 AND score <= 1.0', name='check_validation_score'),
        CheckConstraint('confidence >= 0.0 AND confidence <= 1.0', name='check_validation_confidence'),
        CheckConstraint('test_duration_ms >= 0', name='check_test_duration'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'fingerprint_id': self.fingerprint_id,
            'validation_date': self.validation_date.isoformat() if self.validation_date else None,
            'test_type': self.test_type,
            'test_name': self.test_name,
            'result': self.result,
            'score': self.score,
            'confidence': self.confidence,
            'details': self.details,
            'error_message': self.error_message,
            'warnings': self.warnings,
            'test_environment': self.test_environment,
            'test_duration_ms': self.test_duration_ms
        }


class FingerprintUsageLog(Base):
    """Table for logging fingerprint usage."""

    __tablename__ = "fingerprint_usage_logs"

    # Primary key and relationships
    id = Column(Integer, primary_key=True, index=True)
    fingerprint_id = Column(Integer, ForeignKey("fingerprints.id"), nullable=False)

    # Usage information
    usage_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    session_id = Column(String(100), nullable=True)  # Optional session identifier

    # Context information
    request_context = Column(JSON, nullable=True)  # Information about the request
    user_agent = Column(Text, nullable=True)  # Actual user agent used
    target_domain = Column(String(255), nullable=True)  # Target website/domain

    # Performance metrics
    success = Column(Boolean, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    # Detection information
    detected_as_bot = Column(Boolean, nullable=True)
    detection_reasons = Column(JSON, nullable=True)  # List of detection reasons

    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional metadata

    # Relationships
    fingerprint = relationship("FingerprintRecord", back_populates="usage_logs")

    # Constraints
    __table_args__ = (
        Index('idx_usage_logs_fingerprint_date', 'fingerprint_id', 'usage_date'),
        Index('idx_usage_logs_success_date', 'success', 'usage_date'),
        Index('idx_usage_logs_target_domain', 'target_domain'),
        CheckConstraint('response_time_ms >= 0', name='check_response_time'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'fingerprint_id': self.fingerprint_id,
            'usage_date': self.usage_date.isoformat() if self.usage_date else None,
            'session_id': self.session_id,
            'request_context': self.request_context,
            'user_agent': self.user_agent,
            'target_domain': self.target_domain,
            'success': self.success,
            'response_time_ms': self.response_time_ms,
            'error_message': self.error_message,
            'detected_as_bot': self.detected_as_bot,
            'detection_reasons': self.detection_reasons,
            'metadata': self.metadata
        }


class DataCollectionLog(Base):
    """Table for logging data collection activities."""

    __tablename__ = "data_collection_logs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Collection information
    collection_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source = Column(String(100), nullable=False)  # Source of collection

    # Statistics
    records_collected = Column(Integer, default=0, nullable=False)
    records_processed = Column(Integer, default=0, nullable=False)
    records_stored = Column(Integer, default=0, nullable=False)
    success_rate = Column(Float, nullable=True)

    # Performance metrics
    duration_seconds = Column(Float, nullable=True)
    avg_processing_time_ms = Column(Float, nullable=True)

    # Error handling
    errors = Column(JSON, nullable=True)  # List of errors encountered
    warnings = Column(JSON, nullable=True)  # List of warnings

    # Collection configuration
    collection_config = Column(JSON, nullable=True)  # Configuration used
    data_sources = Column(JSON, nullable=True)  # Data sources used

    # Quality metrics
    avg_quality_score = Column(Float, nullable=True)
    quality_distribution = Column(JSON, nullable=True)  # Distribution of quality scores

    # Metadata
    collection_type = Column(String(50), nullable=False)  # "user_agents", "hardware", "network"
    collection_method = Column(String(100), nullable=True)  # Method used for collection
    metadata = Column(JSON, nullable=True)  # Additional metadata

    # Constraints
    __table_args__ = (
        Index('idx_collection_logs_date_source', 'collection_date', 'source'),
        Index('idx_collection_logs_type_date', 'collection_type', 'collection_date'),
        Index('idx_collection_logs_success_rate', 'success_rate'),
        CheckConstraint('records_collected >= 0', name='check_records_collected'),
        CheckConstraint('records_processed >= 0', name='check_records_processed'),
        CheckConstraint('records_stored >= 0', name='check_records_stored'),
        CheckConstraint('duration_seconds >= 0', name='check_duration_seconds'),
        CheckConstraint('success_rate >= 0.0 AND success_rate <= 1.0', name='check_success_rate'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'collection_date': self.collection_date.isoformat() if self.collection_date else None,
            'source': self.source,
            'records_collected': self.records_collected,
            'records_processed': self.records_processed,
            'records_stored': self.records_stored,
            'success_rate': self.success_rate,
            'duration_seconds': self.duration_seconds,
            'avg_processing_time_ms': self.avg_processing_time_ms,
            'errors': self.errors,
            'warnings': self.warnings,
            'collection_config': self.collection_config,
            'data_sources': self.data_sources,
            'avg_quality_score': self.avg_quality_score,
            'quality_distribution': self.quality_distribution,
            'collection_type': self.collection_type,
            'collection_method': self.collection_method,
            'metadata': self.metadata
        }


class BrowserProfileStats(Base):
    """Table for storing aggregated statistics about browser profiles."""

    __tablename__ = "browser_profile_stats"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Dimensions
    browser_type = Column(String(50), nullable=False)
    operating_system = Column(String(50), nullable=False)
    version_range = Column(String(50), nullable=False)  # e.g., "120.x", "119.x"

    # Time period
    stats_date = Column(DateTime(timezone=True), nullable=False)
    period_type = Column(String(20), nullable=False)  # "daily", "weekly", "monthly"

    # Counts and metrics
    total_profiles = Column(Integer, default=0, nullable=False)
    active_profiles = Column(Integer, default=0, nullable=False)
    avg_coherence_score = Column(Float, nullable=True)
    avg_detection_risk = Column(Float, nullable=True)
    avg_quality_score = Column(Float, nullable=True)

    # Usage statistics
    total_usage_count = Column(Integer, default=0, nullable=False)
    success_rate = Column(Float, nullable=True)
    avg_response_time_ms = Column(Float, nullable=True)

    # Validation statistics
    validation_pass_rate = Column(Float, nullable=True)
    detection_rate = Column(Float, nullable=True)

    # Metadata
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    metadata = Column(JSON, nullable=True)

    # Constraints
    __table_args__ = (
        Index('idx_profile_stats_browser_os_date', 'browser_type', 'operating_system', 'stats_date'),
        Index('idx_profile_stats_period_date', 'period_type', 'stats_date'),
        UniqueConstraint('browser_type', 'operating_system', 'version_range', 'stats_date', 'period_type',
                        name='uq_profile_stats_dimensions'),
        CheckConstraint('total_profiles >= 0', name='check_total_profiles'),
        CheckConstraint('active_profiles >= 0', name='check_active_profiles'),
        CheckConstraint('avg_coherence_score >= 0.0 AND avg_coherence_score <= 1.0', name='check_avg_coherence'),
        CheckConstraint('avg_detection_risk >= 0.0 AND avg_detection_risk <= 1.0', name='check_avg_detection_risk'),
        CheckConstraint('avg_quality_score >= 0.0 AND avg_quality_score <= 1.0', name='check_avg_quality'),
        CheckConstraint('total_usage_count >= 0', name='check_total_usage'),
        CheckConstraint('success_rate >= 0.0 AND success_rate <= 1.0', name='check_success_rate'),
        CheckConstraint('validation_pass_rate >= 0.0 AND validation_pass_rate <= 1.0', name='check_validation_pass'),
        CheckConstraint('detection_rate >= 0.0 AND detection_rate <= 1.0', name='check_detection_rate'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'browser_type': self.browser_type,
            'operating_system': self.operating_system,
            'version_range': self.version_range,
            'stats_date': self.stats_date.isoformat() if self.stats_date else None,
            'period_type': self.period_type,
            'total_profiles': self.total_profiles,
            'active_profiles': self.active_profiles,
            'avg_coherence_score': self.avg_coherence_score,
            'avg_detection_risk': self.avg_detection_risk,
            'avg_quality_score': self.avg_quality_score,
            'total_usage_count': self.total_usage_count,
            'success_rate': self.success_rate,
            'avg_response_time_ms': self.avg_response_time_ms,
            'validation_pass_rate': self.validation_pass_rate,
            'detection_rate': self.detection_rate,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'metadata': self.metadata
        }


class SystemConfiguration(Base):
    """Table for storing system configuration and settings."""

    __tablename__ = "system_configuration"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Configuration keys and values
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(JSON, nullable=False)
    config_type = Column(String(50), nullable=False)  # "string", "number", "boolean", "json"

    # Metadata
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # "collection", "validation", "performance"
    is_sensitive = Column(Boolean, default=False, nullable=False)  # For sensitive config

    # Versioning and change tracking
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(String(100), nullable=True)

    # Validation
    validation_rules = Column(JSON, nullable=True)  # JSON schema for validation
    default_value = Column(JSON, nullable=True)

    # Constraints
    __table_args__ = (
        Index('idx_system_config_category', 'category'),
        Index('idx_system_config_updated', 'updated_at'),
        CheckConstraint('version >= 1', name='check_config_version'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'config_type': self.config_type,
            'description': self.description,
            'category': self.category,
            'is_sensitive': self.is_sensitive,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by,
            'validation_rules': self.validation_rules,
            'default_value': self.default_value
        }