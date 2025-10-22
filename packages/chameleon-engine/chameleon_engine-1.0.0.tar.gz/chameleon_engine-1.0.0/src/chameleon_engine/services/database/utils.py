"""
Database utilities and helper functions.

This module provides utility functions for common database operations
including queries, aggregations, and data management tasks.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from .models import (
    FingerprintRecord, FingerprintValidation, FingerprintUsageLog,
    DataCollectionLog, BrowserProfileStats
)


class FingerprintQueryHelper:
    """Helper class for common fingerprint queries."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def find_best_profile(
        self,
        browser_type: str,
        operating_system: str,
        min_coherence: float = 0.7,
        max_risk: float = 0.5,
        exclude_used_recently: bool = True
    ) -> Optional[FingerprintRecord]:
        """Find the best matching fingerprint profile."""
        query = self.db.query(FingerprintRecord).filter(
            and_(
                FingerprintRecord.browser_type == browser_type,
                FingerprintRecord.operating_system == operating_system,
                FingerprintRecord.is_active == True,
                FingerprintRecord.coherence_score >= min_coherence,
                FingerprintRecord.detection_risk_score <= max_risk
            )
        )

        # Exclude recently used profiles if requested
        if exclude_used_recently:
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            query = query.filter(
                or_(
                    FingerprintRecord.last_used.is_(None),
                    FingerprintRecord.last_used < recent_cutoff
                )
            )

        # Order by quality score and usage count
        query = query.order_by(
            desc(FingerprintRecord.quality_score),
            asc(FingerprintRecord.usage_count)
        )

        return query.first()

    def get_profiles_by_quality(
        self,
        browser_type: Optional[str] = None,
        operating_system: Optional[str] = None,
        min_quality: float = 0.0,
        limit: int = 100
    ) -> List[FingerprintRecord]:
        """Get profiles sorted by quality score."""
        query = self.db.query(FingerprintRecord).filter(
            and_(
                FingerprintRecord.is_active == True,
                FingerprintRecord.quality_score >= min_quality
            )
        )

        if browser_type:
            query = query.filter(FingerprintRecord.browser_type == browser_type)
        if operating_system:
            query = query.filter(FingerprintRecord.operating_system == operating_system)

        return query.order_by(desc(FingerprintRecord.quality_score)).limit(limit).all()

    def get_expired_profiles(self, days_ahead: int = 7) -> List[FingerprintRecord]:
        """Get profiles that will expire soon."""
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)

        return self.db.query(FingerprintRecord).filter(
            and_(
                FingerprintRecord.is_active == True,
                FingerprintRecord.expires_at.is_not(None),
                FingerprintRecord.expires_at <= cutoff_date
            )
        ).all()

    def get_overused_profiles(self, max_usage: int = 100) -> List[FingerprintRecord]:
        """Get profiles that have been used too many times."""
        return self.db.query(FingerprintRecord).filter(
            FingerprintRecord.usage_count >= max_usage
        ).all()

    def update_profile_usage(self, profile_id: int, success: bool = True) -> bool:
        """Update profile usage statistics."""
        try:
            profile = self.db.query(FingerprintRecord).filter(
                FingerprintRecord.id == profile_id
            ).first()

            if profile:
                profile.usage_count += 1
                profile.last_used = datetime.utcnow()

                # If usage failed, potentially mark as less reliable
                if not success:
                    profile.quality_score = max(0.1, profile.quality_score - 0.05)

                self.db.commit()
                return True

            return False

        except Exception:
            self.db.rollback()
            raise

    def cleanup_old_profiles(self, days_old: int = 30) -> int:
        """Clean up old inactive profiles."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        deleted_count = self.db.query(FingerprintRecord).filter(
            and_(
                FingerprintRecord.is_active == False,
                FingerprintRecord.updated_at < cutoff_date
            )
        ).delete()

        self.db.commit()
        return deleted_count


class ValidationQueryHelper:
    """Helper class for validation queries."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_validation_stats(
        self,
        fingerprint_id: int,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get validation statistics for a fingerprint."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        validations = self.db.query(FingerprintValidation).filter(
            and_(
                FingerprintValidation.fingerprint_id == fingerprint_id,
                FingerprintValidation.validation_date >= cutoff_date
            )
        ).all()

        if not validations:
            return {}

        total_validations = len(validations)
        passed_count = sum(1 for v in validations if v.result == 'passed')
        failed_count = sum(1 for v in validations if v.result == 'failed')
        partial_count = sum(1 for v in validations if v.result == 'partial')

        avg_score = sum(v.score or 0 for v in validations) / total_validations
        avg_confidence = sum(v.confidence or 0 for v in validations) / total_validations

        return {
            'total_validations': total_validations,
            'pass_rate': passed_count / total_validations,
            'fail_rate': failed_count / total_validations,
            'partial_rate': partial_count / total_validations,
            'avg_score': avg_score,
            'avg_confidence': avg_confidence,
            'last_validation': max(v.validation_date for v in validations).isoformat()
        }

    def get_failing_validations(self, min_fail_rate: float = 0.3) -> List[int]:
        """Get fingerprint IDs with high failure rates."""
        subquery = self.db.query(
            FingerprintValidation.fingerprint_id,
            func.count(FingerprintValidation.id).label('total'),
            func.sum(func.case([(FingerprintValidation.result == 'failed', 1)], else_=0)).label('failed')
        ).group_by(FingerprintValidation.fingerprint_id).subquery()

        failing_ids = self.db.query(subquery.c.fingerprint_id).filter(
            subquery.c.failed / subquery.c.total >= min_fail_rate
        ).all()

        return [fid[0] for fid in failing_ids]


class UsageQueryHelper:
    """Helper class for usage analytics."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_usage_stats(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get overall usage statistics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        total_usage = self.db.query(FingerprintUsageLog).filter(
            FingerprintUsageLog.usage_date >= cutoff_date
        ).count()

        successful_usage = self.db.query(FingerprintUsageLog).filter(
            and_(
                FingerprintUsageLog.usage_date >= cutoff_date,
                FingerprintUsageLog.success == True
            )
        ).count()

        detected_usage = self.db.query(FingerprintUsageLog).filter(
            and_(
                FingerprintUsageLog.usage_date >= cutoff_date,
                FingerprintUsageLog.detected_as_bot == True
            )
        ).count()

        avg_response_time = self.db.query(
            func.avg(FingerprintUsageLog.response_time_ms)
        ).filter(
            and_(
                FingerprintUsageLog.usage_date >= cutoff_date,
                FingerprintUsageLog.response_time_ms.isnot(None)
            )
        ).scalar() or 0

        return {
            'total_usage': total_usage,
            'successful_usage': successful_usage,
            'success_rate': successful_usage / total_usage if total_usage > 0 else 0,
            'detected_usage': detected_usage,
            'detection_rate': detected_usage / total_usage if total_usage > 0 else 0,
            'avg_response_time_ms': avg_response_time,
            'period_days': days_back
        }

    def get_popular_targets(self, limit: int = 10, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get most frequently targeted domains."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        results = self.db.query(
            FingerprintUsageLog.target_domain,
            func.count(FingerprintUsageLog.id).label('usage_count'),
            func.sum(func.case([(FingerprintUsageLog.success == True, 1)], else_=0)).label('success_count')
        ).filter(
            and_(
                FingerprintUsageLog.usage_date >= cutoff_date,
                FingerprintUsageLog.target_domain.isnot(None)
            )
        ).group_by(FingerprintUsageLog.target_domain).order_by(
            desc('usage_count')
        ).limit(limit).all()

        return [
            {
                'domain': result[0],
                'usage_count': result[1],
                'success_count': result[2],
                'success_rate': result[2] / result[1] if result[1] > 0 else 0
            }
            for result in results
        ]


class CollectionQueryHelper:
    """Helper class for collection analytics."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_collection_stats(self, days_back: int = 30) -> Dict[str, Any]:
        """Get data collection statistics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        collections = self.db.query(DataCollectionLog).filter(
            DataCollectionLog.collection_date >= cutoff_date
        ).all()

        if not collections:
            return {}

        total_collected = sum(c.records_collected for c in collections)
        total_processed = sum(c.records_processed for c in collections)
        total_stored = sum(c.records_stored for c in collections)

        avg_success_rate = sum(c.success_rate or 0 for c in collections) / len(collections)
        avg_duration = sum(c.duration_seconds or 0 for c in collections) / len(collections)

        return {
            'total_collections': len(collections),
            'total_collected': total_collected,
            'total_processed': total_processed,
            'total_stored': total_stored,
            'processing_efficiency': total_processed / total_collected if total_collected > 0 else 0,
            'storage_efficiency': total_stored / total_processed if total_processed > 0 else 0,
            'avg_success_rate': avg_success_rate,
            'avg_duration_seconds': avg_duration,
            'period_days': days_back
        }

    def get_collection_trends(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get daily collection trends."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        daily_stats = self.db.query(
            func.date(DataCollectionLog.collection_date).label('date'),
            func.count(DataCollectionLog.id).label('collections'),
            func.sum(DataCollectionLog.records_collected).label('collected'),
            func.sum(DataCollectionLog.records_stored).label('stored'),
            func.avg(DataCollectionLog.success_rate).label('success_rate')
        ).filter(
            DataCollectionLog.collection_date >= cutoff_date
        ).group_by(func.date(DataCollectionLog.collection_date)).order_by('date').all()

        return [
            {
                'date': stat[0].isoformat(),
                'collections': stat[1],
                'collected': stat[2] or 0,
                'stored': stat[3] or 0,
                'success_rate': stat[4] or 0
            }
            for stat in daily_stats
        ]


def get_database_health(db_session: Session) -> Dict[str, Any]:
    """Get overall database health metrics."""

    # Fingerprint records
    total_fingerprints = db_session.query(FingerprintRecord).count()
    active_fingerprints = db_session.query(FingerprintRecord).filter(
        FingerprintRecord.is_active == True
    ).count()

    # Recent activity
    recent_cutoff = datetime.utcnow() - timedelta(days=7)
    recent_validations = db_session.query(FingerprintValidation).filter(
        FingerprintValidation.validation_date >= recent_cutoff
    ).count()

    recent_usage = db_session.query(FingerprintUsageLog).filter(
        FingerprintUsageLog.usage_date >= recent_cutoff
    ).count()

    # Quality metrics
    avg_quality = db_session.query(
        func.avg(FingerprintRecord.quality_score)
    ).filter(FingerprintRecord.is_active == True).scalar() or 0

    avg_coherence = db_session.query(
        func.avg(FingerprintRecord.coherence_score)
    ).filter(FingerprintRecord.is_active == True).scalar() or 0

    return {
        'fingerprint_records': {
            'total': total_fingerprints,
            'active': active_fingerprints,
            'inactive': total_fingerprints - active_fingerprints
        },
        'recent_activity': {
            'validations_7days': recent_validations,
            'usage_7days': recent_usage
        },
        'quality_metrics': {
            'avg_quality_score': avg_quality,
            'avg_coherence_score': avg_coherence
        },
        'health_score': min(1.0, (avg_quality + avg_coherence) / 2)
    }