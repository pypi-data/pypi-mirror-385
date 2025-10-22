"""
Tests for Database models and SQLAlchemy integration.

Tests the SQLAlchemy models, query helpers, and database utilities to ensure
proper data storage, retrieval, and relationship management.
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Dict, Any, List

from chameleon_engine.services.database.models import (
    Base,
    FingerprintRecord,
    FingerprintValidation,
    FingerprintUsageLog,
    DataCollectionLog,
    BrowserProfileStats,
    SystemConfiguration,
    FingerprintQueryHelper,
    ValidationQueryHelper,
    UsageQueryHelper,
    CollectionQueryHelper,
    get_database_health
)

# Import test fixtures
from tests.conftest import (
    sample_browser_profile,
    sample_fingerprint_request,
    assert_dicts_almost_equal,
    temp_directory
)


@pytest.fixture(scope="function")
def test_db_session():
    """Create a test database session."""
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    # Cleanup
    session.close()


@pytest.fixture
def sample_fingerprint_record(sample_browser_profile):
    """Create a sample fingerprint record for testing."""
    return FingerprintRecord(
        fingerprint_id="test_fp_123",
        browser_type="chrome",
        operating_system="windows",
        profile_data=sample_browser_profile,
        coherence_score=0.95,
        uniqueness_score=0.88,
        detection_risk=0.12,
        generation_method="hybrid",
        quality_score=0.9,
        usage_count=0,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )


@pytest.fixture
def sample_fingerprint_validation():
    """Create a sample fingerprint validation for testing."""
    return FingerprintValidation(
        validation_id="test_val_123",
        fingerprint_id="test_fp_123",
        test_type="anti_bot_detection",
        test_result="passed",
        score=0.85,
        confidence=0.9,
        test_details={
            "detection_system": "bot_detection_suite",
            "test_duration": 2.5,
            "checks_performed": ["fingerprint_consistency", "behavior_analysis", "timing_analysis"]
        },
        tested_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_fingerprint_usage_log():
    """Create a sample fingerprint usage log for testing."""
    return FingerprintUsageLog(
        usage_id="test_usage_123",
        fingerprint_id="test_fp_123",
        session_id="test_session_123",
        target_url="https://example.com",
        action_type="page_load",
        success=True,
        response_time=1.2,
        error_details=None,
        user_context={
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        used_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_data_collection_log():
    """Create a sample data collection log for testing."""
    return DataCollectionLog(
        collection_id="test_coll_123",
        source_type="user_agent_collection",
        source_name="user_agents_online",
        status="completed",
        records_collected=1500,
        records_validated=1425,
        records_imported=1400,
        error_count=5,
        collection_duration=1800.0,
        metadata={
            "collection_method": "web_scraping",
            "validation_rules": ["format_check", "uniqueness_check", "version_check"]
        },
        started_at=datetime.now(timezone.utc) - timedelta(seconds=1800),
        completed_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_browser_profile_stats():
    """Create a sample browser profile stats for testing."""
    return BrowserProfileStats(
        stat_id="test_stat_123",
        date=datetime.now(timezone.utc).date(),
        browser_type="chrome",
        operating_system="windows",
        total_profiles=1000,
        active_profiles=850,
        new_profiles=50,
        expired_profiles=20,
        avg_coherence_score=0.88,
        avg_detection_risk=0.15,
        usage_count=5000,
        success_rate=0.92,
        created_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_system_configuration():
    """Create a sample system configuration for testing."""
    return SystemConfiguration(
        config_id="test_config_123",
        config_key="fingerprint_generation.max_profiles_per_day",
        config_value="5000",
        config_type="integer",
        description="Maximum number of fingerprint profiles that can be generated per day",
        is_active=True,
        version=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


class TestFingerprintRecord:
    """Test FingerprintRecord model."""

    def test_create_fingerprint_record(self, test_db_session: Session, sample_fingerprint_record):
        """Test creating a fingerprint record."""
        test_db_session.add(sample_fingerprint_record)
        test_db_session.commit()
        test_db_session.refresh(sample_fingerprint_record)

        assert sample_fingerprint_record.id is not None
        assert sample_fingerprint_record.fingerprint_id == "test_fp_123"
        assert sample_fingerprint_record.browser_type == "chrome"
        assert sample_fingerprint_record.operating_system == "windows"
        assert sample_fingerprint_record.coherence_score == 0.95
        assert sample_fingerprint_record.usage_count == 0
        assert sample_fingerprint_record.is_active is True

    def test_fingerprint_record_validation(self, test_db_session: Session):
        """Test fingerprint record validation."""
        # Test valid record
        record = FingerprintRecord(
            fingerprint_id="test_fp_124",
            browser_type="firefox",
            operating_system="linux",
            profile_data={"user_agent": "Mozilla/5.0 (X11; Linux x86_64)"},
            coherence_score=0.8,
            uniqueness_score=0.75,
            detection_risk=0.2,
            generation_method="ml",
            quality_score=0.85
        )

        test_db_session.add(record)
        test_db_session.commit()

        assert record.id is not None
        assert record.coherence_score == 0.8

        # Test invalid scores
        with pytest.raises(Exception):  # SQLAlchemy will raise an exception for invalid values
            invalid_record = FingerprintRecord(
                fingerprint_id="test_fp_125",
                browser_type="chrome",
                operating_system="windows",
                profile_data={"user_agent": "Mozilla/5.0"},
                coherence_score=1.5,  # Invalid: > 1.0
                uniqueness_score=0.8,
                detection_risk=0.1,
                generation_method="hybrid",
                quality_score=0.9
            )
            test_db_session.add(invalid_record)
            test_db_session.commit()

    def test_fingerprint_record_relationships(self, test_db_session: Session,
                                            sample_fingerprint_record,
                                            sample_fingerprint_validation,
                                            sample_fingerprint_usage_log):
        """Test fingerprint record relationships."""
        # Add records
        test_db_session.add(sample_fingerprint_record)
        test_db_session.commit()
        test_db_session.refresh(sample_fingerprint_record)

        # Link validation and usage to fingerprint
        sample_fingerprint_validation.fingerprint_id = sample_fingerprint_record.fingerprint_id
        sample_fingerprint_usage_log.fingerprint_id = sample_fingerprint_record.fingerprint_id

        test_db_session.add(sample_fingerprint_validation)
        test_db_session.add(sample_fingerprint_usage_log)
        test_db_session.commit()

        # Test relationships
        assert len(sample_fingerprint_record.validations) == 1
        assert len(sample_fingerprint_record.usage_logs) == 1
        assert sample_fingerprint_record.validations[0].validation_id == "test_val_123"
        assert sample_fingerprint_record.usage_logs[0].usage_id == "test_usage_123"

    def test_fingerprint_record_usage_tracking(self, test_db_session: Session, sample_fingerprint_record):
        """Test usage tracking functionality."""
        test_db_session.add(sample_fingerprint_record)
        test_db_session.commit()
        test_db_session.refresh(sample_fingerprint_record)

        # Test initial usage count
        assert sample_fingerprint_record.usage_count == 0
        assert sample_fingerprint_record.last_used_at is None

        # Increment usage
        sample_fingerprint_record.increment_usage()
        test_db_session.commit()

        assert sample_fingerprint_record.usage_count == 1
        assert sample_fingerprint_record.last_used_at is not None

        # Increment usage multiple times
        for _ in range(5):
            sample_fingerprint_record.increment_usage()
        test_db_session.commit()

        assert sample_fingerprint_record.usage_count == 6

    def test_fingerprint_record_expiration(self, test_db_session: Session, sample_fingerprint_record):
        """Test expiration functionality."""
        test_db_session.add(sample_fingerprint_record)
        test_db_session.commit()
        test_db_session.refresh(sample_fingerprint_record)

        # Test non-expired record
        assert not sample_fingerprint_record.is_expired()

        # Test expired record
        expired_time = datetime.now(timezone.utc) - timedelta(days=1)
        sample_fingerprint_record.expires_at = expired_time
        test_db_session.commit()

        assert sample_fingerprint_record.is_expired()

    def test_fingerprint_record_soft_delete(self, test_db_session: Session, sample_fingerprint_record):
        """Test soft delete functionality."""
        test_db_session.add(sample_fingerprint_record)
        test_db_session.commit()
        test_db_session.refresh(sample_fingerprint_record)

        # Test active record
        assert sample_fingerprint_record.is_active is True

        # Soft delete
        sample_fingerprint_record.soft_delete()
        test_db_session.commit()

        assert sample_fingerprint_record.is_active is False
        assert sample_fingerprint_record.deleted_at is not None

    def test_fingerprint_record_quality_score(self, test_db_session: Session, sample_fingerprint_record):
        """Test quality score calculation."""
        test_db_session.add(sample_fingerprint_record)
        test_db_session.commit()
        test_db_session.refresh(sample_fingerprint_record)

        # Test quality score
        assert sample_fingerprint_record.quality_score == 0.9

        # Update quality score based on components
        new_quality = (sample_fingerprint_record.coherence_score +
                      sample_fingerprint_record.uniqueness_score) / 2
        sample_fingerprint_record.update_quality_score(new_quality)
        test_db_session.commit()

        assert sample_fingerprint_record.quality_score == new_quality


class TestFingerprintValidation:
    """Test FingerprintValidation model."""

    def test_create_fingerprint_validation(self, test_db_session: Session, sample_fingerprint_validation):
        """Test creating a fingerprint validation."""
        test_db_session.add(sample_fingerprint_validation)
        test_db_session.commit()
        test_db_session.refresh(sample_fingerprint_validation)

        assert sample_fingerprint_validation.id is not None
        assert sample_fingerprint_validation.validation_id == "test_val_123"
        assert sample_fingerprint_validation.fingerprint_id == "test_fp_123"
        assert sample_fingerprint_validation.test_type == "anti_bot_detection"
        assert sample_fingerprint_validation.test_result == "passed"
        assert sample_fingerprint_validation.score == 0.85
        assert sample_fingerprint_validation.confidence == 0.9

    def test_fingerprint_validation_validation(self, test_db_session: Session):
        """Test fingerprint validation validation."""
        # Test valid validation
        validation = FingerprintValidation(
            validation_id="test_val_124",
            fingerprint_id="test_fp_124",
            test_type="consistency_check",
            test_result="passed",
            score=0.9,
            confidence=0.95
        )

        test_db_session.add(validation)
        test_db_session.commit()

        assert validation.id is not None
        assert validation.score == 0.9

        # Test invalid scores
        with pytest.raises(Exception):
            invalid_validation = FingerprintValidation(
                validation_id="test_val_125",
                fingerprint_id="test_fp_125",
                test_type="consistency_check",
                test_result="passed",
                score=1.5,  # Invalid: > 1.0
                confidence=0.9
            )
            test_db_session.add(invalid_validation)
            test_db_session.commit()

    def test_validation_result_types(self, test_db_session: Session):
        """Test different validation result types."""
        valid_results = ["passed", "failed", "warning", "error"]

        for result in valid_results:
            validation = FingerprintValidation(
                validation_id=f"test_val_{result}",
                fingerprint_id="test_fp_123",
                test_type="test_type",
                test_result=result,
                score=0.8,
                confidence=0.9
            )
            test_db_session.add(validation)

        test_db_session.commit()

        # Verify all results were saved
        validations = test_db_session.query(FingerprintValidation).filter(
            FingerprintValidation.fingerprint_id == "test_fp_123"
        ).all()

        assert len(validations) == len(valid_results)
        results = [v.test_result for v in validations]
        for result in valid_results:
            assert result in results


class TestFingerprintUsageLog:
    """Test FingerprintUsageLog model."""

    def test_create_fingerprint_usage_log(self, test_db_session: Session, sample_fingerprint_usage_log):
        """Test creating a fingerprint usage log."""
        test_db_session.add(sample_fingerprint_usage_log)
        test_db_session.commit()
        test_db_session.refresh(sample_fingerprint_usage_log)

        assert sample_fingerprint_usage_log.id is not None
        assert sample_fingerprint_usage_log.usage_id == "test_usage_123"
        assert sample_fingerprint_usage_log.fingerprint_id == "test_fp_123"
        assert sample_fingerprint_usage_log.session_id == "test_session_123"
        assert sample_fingerprint_usage_log.target_url == "https://example.com"
        assert sample_fingerprint_usage_log.action_type == "page_load"
        assert sample_fingerprint_usage_log.success is True
        assert sample_fingerprint_usage_log.response_time == 1.2

    def test_usage_log_action_types(self, test_db_session: Session):
        """Test different action types."""
        action_types = ["page_load", "click", "form_submit", "scroll", "screenshot", "download"]

        for action in action_types:
            usage_log = FingerprintUsageLog(
                usage_id=f"test_usage_{action}",
                fingerprint_id="test_fp_123",
                session_id="test_session_123",
                target_url="https://example.com",
                action_type=action,
                success=True,
                response_time=1.0
            )
            test_db_session.add(usage_log)

        test_db_session.commit()

        # Verify all action types were saved
        logs = test_db_session.query(FingerprintUsageLog).filter(
            FingerprintUsageLog.fingerprint_id == "test_fp_123"
        ).all()

        assert len(logs) == len(action_types)
        logged_actions = [log.action_type for log in logs]
        for action in action_types:
            assert action in logged_actions

    def test_usage_log_error_handling(self, test_db_session: Session):
        """Test usage log error handling."""
        error_log = FingerprintUsageLog(
            usage_id="test_usage_error",
            fingerprint_id="test_fp_123",
            session_id="test_session_123",
            target_url="https://example.com",
            action_type="page_load",
            success=False,
            response_time=5.0,
            error_details="Connection timeout",
            user_context={"error_code": "TIMEOUT"}
        )

        test_db_session.add(error_log)
        test_db_session.commit()

        assert error_log.success is False
        assert error_log.error_details == "Connection timeout"
        assert error_log.user_context["error_code"] == "TIMEOUT"


class TestDataCollectionLog:
    """Test DataCollectionLog model."""

    def test_create_data_collection_log(self, test_db_session: Session, sample_data_collection_log):
        """Test creating a data collection log."""
        test_db_session.add(sample_data_collection_log)
        test_db_session.commit()
        test_db_session.refresh(sample_data_collection_log)

        assert sample_data_collection_log.id is not None
        assert sample_data_collection_log.collection_id == "test_coll_123"
        assert sample_data_collection_log.source_type == "user_agent_collection"
        assert sample_data_collection_log.source_name == "user_agents_online"
        assert sample_data_collection_log.status == "completed"
        assert sample_data_collection_log.records_collected == 1500
        assert sample_data_collection_log.records_validated == 1425
        assert sample_data_collection_log.records_imported == 1400
        assert sample_data_collection_log.error_count == 5
        assert sample_data_collection_log.collection_duration == 1800.0

    def test_collection_log_status_types(self, test_db_session: Session):
        """Test different collection status types."""
        status_types = ["started", "running", "completed", "failed", "cancelled"]

        for status in status_types:
            collection_log = DataCollectionLog(
                collection_id=f"test_coll_{status}",
                source_type="test_source",
                source_name="test_name",
                status=status,
                records_collected=100,
                records_validated=95,
                records_imported=90,
                error_count=1 if status == "failed" else 0,
                collection_duration=300.0
            )
            test_db_session.add(collection_log)

        test_db_session.commit()

        # Verify all statuses were saved
        logs = test_db_session.query(DataCollectionLog).all()
        assert len(logs) == len(status_types)
        logged_statuses = [log.status for log in logs]
        for status in status_types:
            assert status in logged_statuses

    def test_collection_log_success_rate(self, test_db_session: Session):
        """Test collection success rate calculation."""
        collection_log = DataCollectionLog(
            collection_id="test_coll_success",
            source_type="test_source",
            source_name="test_name",
            status="completed",
            records_collected=1000,
            records_validated=950,
            records_imported=900,
            error_count=10,
            collection_duration=600.0
        )

        test_db_session.add(collection_log)
        test_db_session.commit()

        # Test success rate calculation
        expected_success_rate = collection_log.records_imported / collection_log.records_collected
        assert collection_log.get_success_rate() == expected_success_rate
        assert collection_log.get_success_rate() == 0.9


class TestBrowserProfileStats:
    """Test BrowserProfileStats model."""

    def test_create_browser_profile_stats(self, test_db_session: Session, sample_browser_profile_stats):
        """Test creating browser profile stats."""
        test_db_session.add(sample_browser_profile_stats)
        test_db_session.commit()
        test_db_session.refresh(sample_browser_profile_stats)

        assert sample_browser_profile_stats.id is not None
        assert sample_browser_profile_stats.stat_id == "test_stat_123"
        assert sample_browser_profile_stats.browser_type == "chrome"
        assert sample_browser_profile_stats.operating_system == "windows"
        assert sample_browser_profile_stats.total_profiles == 1000
        assert sample_browser_profile_stats.active_profiles == 850
        assert sample_browser_profile_stats.new_profiles == 50
        assert sample_browser_profile_stats.expired_profiles == 20
        assert sample_browser_profile_stats.avg_coherence_score == 0.88
        assert sample_browser_profile_stats.avg_detection_risk == 0.15
        assert sample_browser_profile_stats.usage_count == 5000
        assert sample_browser_profile_stats.success_rate == 0.92

    def test_profile_stats_aggregation(self, test_db_session: Session):
        """Test profile stats aggregation."""
        # Create stats for different browser/OS combinations
        combinations = [
            ("chrome", "windows", 1000, 850, 0.88, 0.15, 5000, 0.92),
            ("firefox", "windows", 500, 400, 0.85, 0.18, 2000, 0.89),
            ("chrome", "linux", 300, 280, 0.90, 0.12, 1500, 0.94),
            ("firefox", "linux", 200, 180, 0.87, 0.14, 800, 0.91)
        ]

        today = datetime.now(timezone.utc).date()

        for browser, os, total, active, coherence, risk, usage, success in combinations:
            stats = BrowserProfileStats(
                stat_id=f"stat_{browser}_{os}",
                date=today,
                browser_type=browser,
                operating_system=os,
                total_profiles=total,
                active_profiles=active,
                avg_coherence_score=coherence,
                avg_detection_risk=risk,
                usage_count=usage,
                success_rate=success
            )
            test_db_session.add(stats)

        test_db_session.commit()

        # Test aggregation queries
        total_profiles = test_db_session.query(BrowserProfileStats).filter(
            BrowserProfileStats.date == today
        ).with_entities(
            test_db_session.func.sum(BrowserProfileStats.total_profiles)
        ).scalar()

        assert total_profiles == sum(total for _, _, total, _, _, _, _, _ in combinations)

        # Chrome-specific stats
        chrome_stats = test_db_session.query(BrowserProfileStats).filter(
            BrowserProfileStats.date == today,
            BrowserProfileStats.browser_type == "chrome"
        ).all()

        assert len(chrome_stats) == 2  # chrome windows and chrome linux


class TestSystemConfiguration:
    """Test SystemConfiguration model."""

    def test_create_system_configuration(self, test_db_session: Session, sample_system_configuration):
        """Test creating a system configuration."""
        test_db_session.add(sample_system_configuration)
        test_db_session.commit()
        test_db_session.refresh(sample_system_configuration)

        assert sample_system_configuration.id is not None
        assert sample_system_configuration.config_id == "test_config_123"
        assert sample_system_configuration.config_key == "fingerprint_generation.max_profiles_per_day"
        assert sample_system_configuration.config_value == "5000"
        assert sample_system_configuration.config_type == "integer"
        assert sample_system_configuration.is_active is True
        assert sample_system_configuration.version == 1

    def test_configuration_types(self, test_db_session: Session):
        """Test different configuration types."""
        configs = [
            ("string_setting", "test_value", "string"),
            ("integer_setting", "100", "integer"),
            ("float_setting", "1.5", "float"),
            ("boolean_setting", "true", "boolean"),
            ("json_setting", '{"key": "value"}', "json")
        ]

        for key, value, config_type in configs:
            config = SystemConfiguration(
                config_id=f"config_{key}",
                config_key=key,
                config_value=value,
                config_type=config_type,
                description=f"Test {config_type} configuration"
            )
            test_db_session.add(config)

        test_db_session.commit()

        # Verify all configs were saved
        saved_configs = test_db_session.query(SystemConfiguration).all()
        assert len(saved_configs) == len(configs)

        for config in saved_configs:
            assert config.config_type in ["string", "integer", "float", "boolean", "json"]

    def test_configuration_versioning(self, test_db_session: Session):
        """Test configuration versioning."""
        # Initial configuration
        config_v1 = SystemConfiguration(
            config_id="config_versioned",
            config_key="test.setting",
            config_value="initial_value",
            config_type="string",
            version=1
        )
        test_db_session.add(config_v1)
        test_db_session.commit()

        # Updated configuration
        config_v2 = SystemConfiguration(
            config_id="config_versioned",
            config_key="test.setting",
            config_value="updated_value",
            config_type="string",
            version=2
        )
        test_db_session.add(config_v2)
        test_db_session.commit()

        # Retrieve latest version
        latest_config = test_db_session.query(SystemConfiguration).filter(
            SystemConfiguration.config_key == "test.setting"
        ).order_by(SystemConfiguration.version.desc()).first()

        assert latest_config.version == 2
        assert latest_config.config_value == "updated_value"


class TestQueryHelpers:
    """Test database query helper classes."""

    def test_fingerprint_query_helper(self, test_db_session: Session, sample_fingerprint_record):
        """Test FingerprintQueryHelper functionality."""
        test_db_session.add(sample_fingerprint_record)
        test_db_session.commit()

        helper = FingerprintQueryHelper(test_db_session)

        # Test get by fingerprint ID
        record = helper.get_by_fingerprint_id("test_fp_123")
        assert record is not None
        assert record.fingerprint_id == "test_fp_123"

        # Test get by browser and OS
        records = helper.get_by_browser_os("chrome", "windows")
        assert len(records) == 1
        assert records[0].browser_type == "chrome"

        # Test get active profiles
        active_profiles = helper.get_active_profiles()
        assert len(active_profiles) == 1
        assert active_profiles[0].is_active is True

        # Test get high quality profiles
        high_quality = helper.get_high_quality_profiles(min_quality=0.8)
        assert len(high_quality) == 1
        assert high_quality[0].quality_score >= 0.8

        # Test get low risk profiles
        low_risk = helper.get_low_risk_profiles(max_risk=0.2)
        assert len(low_risk) == 1
        assert low_risk[0].detection_risk <= 0.2

        # Test search by quality score range
        quality_range = helper.search_by_quality_range(0.8, 1.0)
        assert len(quality_range) == 1
        assert 0.8 <= quality_range[0].quality_score <= 1.0

    def test_validation_query_helper(self, test_db_session: Session,
                                   sample_fingerprint_record,
                                   sample_fingerprint_validation):
        """Test ValidationQueryHelper functionality."""
        test_db_session.add(sample_fingerprint_record)
        test_db_session.add(sample_fingerprint_validation)
        test_db_session.commit()

        helper = ValidationQueryHelper(test_db_session)

        # Test get validations by fingerprint
        validations = helper.get_validations_by_fingerprint("test_fp_123")
        assert len(validations) == 1
        assert validations[0].validation_id == "test_val_123"

        # Test get validations by test type
        test_type_validations = helper.get_validations_by_test_type("anti_bot_detection")
        assert len(test_type_validations) == 1
        assert test_type_validations[0].test_type == "anti_bot_detection"

        # Test get passed validations
        passed_validations = helper.get_passed_validations()
        assert len(passed_validations) == 1
        assert passed_validations[0].test_result == "passed"

        # Test get failed validations
        failed_validations = helper.get_failed_validations()
        assert len(failed_validations) == 0  # No failed validations in test data

        # Test get validation statistics
        stats = helper.get_validation_statistics()
        assert stats["total_validations"] == 1
        assert stats["passed_count"] == 1
        assert stats["failed_count"] == 0
        assert stats["average_score"] == 0.85

    def test_usage_query_helper(self, test_db_session: Session,
                              sample_fingerprint_record,
                              sample_fingerprint_usage_log):
        """Test UsageQueryHelper functionality."""
        test_db_session.add(sample_fingerprint_record)
        test_db_session.add(sample_fingerprint_usage_log)
        test_db_session.commit()

        helper = UsageQueryHelper(test_db_session)

        # Test get usage by fingerprint
        usage_logs = helper.get_usage_by_fingerprint("test_fp_123")
        assert len(usage_logs) == 1
        assert usage_logs[0].usage_id == "test_usage_123"

        # Test get usage by session
        session_usage = helper.get_usage_by_session("test_session_123")
        assert len(session_usage) == 1
        assert session_usage[0].session_id == "test_session_123"

        # Test get successful usage
        successful_usage = helper.get_successful_usage()
        assert len(successful_usage) == 1
        assert successful_usage[0].success is True

        # Test get failed usage
        failed_usage = helper.get_failed_usage()
        assert len(failed_usage) == 0  # No failed usage in test data

        # Test get usage statistics
        stats = helper.get_usage_statistics()
        assert stats["total_usage"] == 1
        assert stats["successful_usage"] == 1
        assert stats["failed_usage"] == 0
        assert stats["success_rate"] == 1.0
        assert stats["average_response_time"] == 1.2

    def test_collection_query_helper(self, test_db_session: Session, sample_data_collection_log):
        """Test CollectionQueryHelper functionality."""
        test_db_session.add(sample_data_collection_log)
        test_db_session.commit()

        helper = CollectionQueryHelper(test_db_session)

        # Test get collections by source type
        collections = helper.get_collections_by_source_type("user_agent_collection")
        assert len(collections) == 1
        assert collections[0].source_type == "user_agent_collection"

        # Test get collections by status
        completed_collections = helper.get_collections_by_status("completed")
        assert len(completed_collections) == 1
        assert completed_collections[0].status == "completed"

        # Test get recent collections
        recent_collections = helper.get_recent_collections(days=1)
        assert len(recent_collections) == 1
        assert recent_collections[0].collection_id == "test_coll_123"

        # Test get collection statistics
        stats = helper.get_collection_statistics()
        assert stats["total_collections"] == 1
        assert stats["completed_collections"] == 1
        assert stats["total_records_collected"] == 1500
        assert stats["total_records_imported"] == 1400
        assert stats["overall_success_rate"] == 0.9333333333333333  # 1400/1500


class TestDatabaseHealth:
    """Test database health checking functionality."""

    def test_get_database_health(self, test_db_session: Session,
                               sample_fingerprint_record,
                               sample_fingerprint_validation,
                               sample_fingerprint_usage_log):
        """Test database health checking."""
        # Add test data
        test_db_session.add(sample_fingerprint_record)
        test_db_session.add(sample_fingerprint_validation)
        test_db_session.add(sample_fingerprint_usage_log)
        test_db_session.commit()

        # Get health metrics
        health = get_database_health(test_db_session)

        assert health["overall_health"] == "healthy"
        assert health["fingerprint_records"]["total"] == 1
        assert health["fingerprint_records"]["active"] == 1
        assert health["validations"]["total"] == 1
        assert health["validations"]["success_rate"] == 1.0
        assert health["usage_logs"]["total"] == 1
        assert health["usage_logs"]["success_rate"] == 1.0
        assert health["database_size"]["tables"] == 6  # All tables should exist
        assert health["last_updated"] is not None

    def test_database_health_with_errors(self, test_db_session: Session):
        """Test database health with error conditions."""
        # Add some failing validation records
        failed_validation = FingerprintValidation(
            validation_id="test_val_failed",
            fingerprint_id="test_fp_456",
            test_type="anti_bot_detection",
            test_result="failed",
            score=0.3,
            confidence=0.5
        )
        test_db_session.add(failed_validation)

        # Add some failing usage records
        failed_usage = FingerprintUsageLog(
            usage_id="test_usage_failed",
            fingerprint_id="test_fp_456",
            session_id="test_session_456",
            target_url="https://example.com",
            action_type="page_load",
            success=False,
            response_time=10.0,
            error_details="Connection failed"
        )
        test_db_session.add(failed_usage)
        test_db_session.commit()

        health = get_database_health(test_db_session)

        assert health["overall_health"] == "warning"  # Should be warning due to failures
        assert health["validations"]["success_rate"] == 0.0  # 0% success rate
        assert health["usage_logs"]["success_rate"] == 0.0  # 0% success rate


class TestDatabasePerformance:
    """Test database performance aspects."""

    def test_bulk_insert_performance(self, test_db_session: Session):
        """Test bulk insert performance."""
        import time

        # Create many fingerprint records
        records = []
        for i in range(1000):
            record = FingerprintRecord(
                fingerprint_id=f"bulk_fp_{i}",
                browser_type="chrome" if i % 2 == 0 else "firefox",
                operating_system="windows" if i % 3 == 0 else "linux",
                profile_data={"user_agent": f"Mozilla/5.0 Test {i}"},
                coherence_score=0.8 + (i % 20) * 0.01,
                uniqueness_score=0.7 + (i % 30) * 0.01,
                detection_risk=0.1 + (i % 20) * 0.01,
                generation_method="bulk_test",
                quality_score=0.8 + (i % 20) * 0.01
            )
            records.append(record)

        # Measure bulk insert time
        start_time = time.time()
        test_db_session.bulk_save_objects(records)
        test_db_session.commit()
        bulk_insert_time = time.time() - start_time

        # Bulk insert should be fast (< 1 second for 1000 records)
        assert bulk_insert_time < 1.0

        # Verify records were inserted
        count = test_db_session.query(FingerprintRecord).filter(
            FingerprintRecord.fingerprint_id.like("bulk_fp_%")
        ).count()
        assert count == 1000

    def test_query_performance_with_indexes(self, test_db_session: Session):
        """Test query performance with database indexes."""
        import time

        # Insert test data with different values for indexed columns
        for i in range(500):
            record = FingerprintRecord(
                fingerprint_id=f"query_perf_{i}",
                browser_type=["chrome", "firefox", "safari"][i % 3],
                operating_system=["windows", "linux", "macos"][i % 3],
                profile_data={"user_agent": f"Mozilla/5.0 Test {i}"},
                coherence_score=0.5 + (i % 50) * 0.01,
                uniqueness_score=0.5 + (i % 50) * 0.01,
                detection_risk=0.05 + (i % 30) * 0.01,
                generation_method="performance_test",
                quality_score=0.7 + (i % 30) * 0.01,
                usage_count=i % 10
            )
            test_db_session.add(record)

        test_db_session.commit()

        # Test query performance on indexed columns
        helper = FingerprintQueryHelper(test_db_session)

        start_time = time.time()
        chrome_records = helper.get_by_browser_os("chrome", "windows")
        query_time = time.time() - start_time

        # Query should be fast (< 100ms)
        assert query_time < 0.1
        assert len(chrome_records) > 0

        # Test complex query with multiple conditions
        start_time = time.time()
        complex_results = helper.search_by_quality_range(0.8, 1.0)
        complex_query_time = time.time() - start_time

        # Complex query should still be fast (< 200ms)
        assert complex_query_time < 0.2

    def test_concurrent_access(self, test_db_session: Session):
        """Test concurrent database access."""
        import threading
        import time

        results = []
        errors = []

        def worker(worker_id):
            try:
                # Create a new session for this thread
                Session = sessionmaker(bind=test_db_session.bind)
                thread_session = Session()

                # Perform database operations
                for i in range(10):
                    record = FingerprintRecord(
                        fingerprint_id=f"concurrent_{worker_id}_{i}",
                        browser_type="chrome",
                        operating_system="linux",
                        profile_data={"user_agent": f"Concurrent test {worker_id}-{i}"},
                        coherence_score=0.8,
                        uniqueness_score=0.7,
                        detection_risk=0.1,
                        generation_method="concurrent_test",
                        quality_score=0.75
                    )
                    thread_session.add(record)

                thread_session.commit()

                # Query records
                count = thread_session.query(FingerprintRecord).filter(
                    FingerprintRecord.fingerprint_id.like(f"concurrent_{worker_id}_%")
                ).count()

                results.append((worker_id, count))
                thread_session.close()

            except Exception as e:
                errors.append((worker_id, str(e)))

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5

        for worker_id, count in results:
            assert count == 10, f"Worker {worker_id} expected 10 records, got {count}"

        # Verify all records were inserted
        total_count = test_db_session.query(FingerprintRecord).filter(
            FingerprintRecord.fingerprint_id.like("concurrent_%")
        ).count()
        assert total_count == 50  # 5 workers * 10 records each


if __name__ == "__main__":
    pytest.main([__file__, "-v"])