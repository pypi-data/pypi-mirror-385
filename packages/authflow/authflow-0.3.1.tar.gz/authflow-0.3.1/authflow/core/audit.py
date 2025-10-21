"""Audit logging service using Redis for storage."""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

import redis.asyncio as aioredis

from authflow.models.audit import AuditLog, AuditLogCreate, AuditLogFilters, AuditLogStats

logger = logging.getLogger(__name__)


class AuditService:
    """Service for managing audit logs with Redis backend.

    Uses Redis Sorted Sets for time-series data and Hash sets for log details.
    This provides fast querying by time range and efficient storage.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/1", retention_days: int = 90):
        """Initialize audit service.

        Args:
            redis_url: Redis connection URL
            retention_days: Number of days to retain audit logs
        """
        self.redis_url = redis_url
        self.retention_days = retention_days
        self._redis: Optional[aioredis.Redis] = None

        # Redis key prefixes
        self.AUDIT_LOG_PREFIX = "audit:log:"
        self.AUDIT_INDEX_KEY = "audit:index"  # Sorted set for time-based indexing
        self.AUDIT_STATS_KEY = "audit:stats"  # Hash for statistics

    async def _get_redis(self) -> aioredis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            try:
                self._redis = await aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                logger.info("Connected to Redis for audit logging")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise

        return self._redis

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    async def log_event(
        self,
        event_type: str,
        resource_type: str,
        action: str,
        status: str = "success",
        actor_id: Optional[str] = None,
        actor_username: Optional[str] = None,
        actor_ip: Optional[str] = None,
        actor_user_agent: Optional[str] = None,
        resource_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        team_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """Create an audit log entry.

        Args:
            event_type: Type of event (e.g., "user.login", "role.assigned")
            resource_type: Type of resource (e.g., "user", "role")
            action: Action performed (e.g., "create", "update", "delete")
            status: Status of action ("success", "failure", "pending")
            actor_id: ID of user who performed the action
            actor_username: Username of actor
            actor_ip: IP address of actor
            actor_user_agent: User agent of actor
            resource_id: ID of affected resource
            organization_id: Organization context
            team_id: Team context
            details: Additional event details
            error_message: Error message if action failed

        Returns:
            Created audit log entry
        """
        try:
            redis = await self._get_redis()

            # Generate unique ID and timestamp
            log_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()

            # Create audit log entry
            audit_log = AuditLog(
                id=log_id,
                timestamp=timestamp,
                event_type=event_type,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                actor_id=actor_id,
                actor_username=actor_username,
                actor_ip=actor_ip,
                actor_user_agent=actor_user_agent,
                status=status,
                details=details or {},
                error_message=error_message,
                organization_id=organization_id,
                team_id=team_id,
            )

            # Store log entry as hash
            log_key = f"{self.AUDIT_LOG_PREFIX}{log_id}"
            log_data = audit_log.model_dump()

            # Convert datetime to ISO string for Redis storage
            log_data["timestamp"] = timestamp.isoformat()

            # Convert details dict to JSON string
            log_data["details"] = json.dumps(log_data["details"])

            await redis.hset(log_key, mapping=log_data)  # type: ignore

            # Add to sorted set index (score = timestamp as unix timestamp)
            timestamp_score = timestamp.timestamp()
            await redis.zadd(self.AUDIT_INDEX_KEY, {log_id: timestamp_score})  # type: ignore

            # Set expiration
            expiration_seconds = self.retention_days * 24 * 60 * 60
            await redis.expire(log_key, expiration_seconds)

            # Update statistics
            await self._update_stats(redis, event_type, action, status)

            logger.debug(f"Logged audit event: {event_type} - {action} - {status}")

            return audit_log

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            # Don't raise - audit logging should not break the application
            return audit_log

    async def _update_stats(
        self,
        redis: aioredis.Redis,
        event_type: str,
        action: str,
        status: str
    ):
        """Update audit statistics."""
        try:
            await redis.hincrby(f"{self.AUDIT_STATS_KEY}:event_type", event_type, 1)
            await redis.hincrby(f"{self.AUDIT_STATS_KEY}:action", action, 1)
            await redis.hincrby(f"{self.AUDIT_STATS_KEY}:status", status, 1)
            await redis.incr(f"{self.AUDIT_STATS_KEY}:total")
        except Exception as e:
            logger.warning(f"Failed to update audit stats: {e}")

    async def get_logs(
        self,
        filters: AuditLogFilters
    ) -> tuple[List[AuditLog], int]:
        """Get audit logs with filtering and pagination.

        Args:
            filters: Filter and pagination parameters

        Returns:
            Tuple of (logs, total_count)
        """
        try:
            redis = await self._get_redis()

            # Get time range
            start_score = filters.start_date.timestamp() if filters.start_date else 0
            end_score = filters.end_date.timestamp() if filters.end_date else datetime.utcnow().timestamp()

            # Get log IDs from sorted set within time range
            log_ids = await redis.zrevrangebyscore(
                self.AUDIT_INDEX_KEY,
                max=end_score,
                min=start_score,
            )

            if not log_ids:
                return [], 0

            # Fetch log details
            logs = []
            for log_id in log_ids:
                log_key = f"{self.AUDIT_LOG_PREFIX}{log_id}"
                log_data = await redis.hgetall(log_key)

                if not log_data:
                    continue

                # Apply filters
                if filters.event_type and log_data.get("event_type") != filters.event_type:
                    continue
                if filters.resource_type and log_data.get("resource_type") != filters.resource_type:
                    continue
                if filters.resource_id and log_data.get("resource_id") != filters.resource_id:
                    continue
                if filters.action and log_data.get("action") != filters.action:
                    continue
                if filters.actor_id and log_data.get("actor_id") != filters.actor_id:
                    continue
                if filters.actor_username and log_data.get("actor_username") != filters.actor_username:
                    continue
                if filters.status and log_data.get("status") != filters.status:
                    continue
                if filters.organization_id and log_data.get("organization_id") != filters.organization_id:
                    continue
                if filters.team_id and log_data.get("team_id") != filters.team_id:
                    continue

                # Parse details from JSON
                log_data["details"] = json.loads(log_data.get("details", "{}"))

                # Convert timestamp string back to datetime
                log_data["timestamp"] = datetime.fromisoformat(log_data["timestamp"])

                logs.append(AuditLog(**log_data))

            total = len(logs)

            # Apply pagination
            start_idx = (filters.page - 1) * filters.page_size
            end_idx = start_idx + filters.page_size
            paginated_logs = logs[start_idx:end_idx]

            return paginated_logs, total

        except Exception as e:
            logger.error(f"Failed to get audit logs: {e}")
            return [], 0

    async def get_stats(self) -> AuditLogStats:
        """Get audit log statistics.

        Returns:
            Audit log statistics
        """
        try:
            redis = await self._get_redis()

            # Get totals
            total = await redis.get(f"{self.AUDIT_STATS_KEY}:total") or 0

            # Get event type counts
            events_by_type = await redis.hgetall(f"{self.AUDIT_STATS_KEY}:event_type") or {}

            # Get action counts
            events_by_action = await redis.hgetall(f"{self.AUDIT_STATS_KEY}:action") or {}

            # Get status counts
            events_by_status = await redis.hgetall(f"{self.AUDIT_STATS_KEY}:status") or {}

            # Get recent failures count (last 24 hours)
            yesterday = (datetime.utcnow() - timedelta(days=1)).timestamp()
            recent_logs = await redis.zrevrangebyscore(
                self.AUDIT_INDEX_KEY,
                max=datetime.utcnow().timestamp(),
                min=yesterday,
            )

            recent_failures = 0
            for log_id in recent_logs:
                log_data = await redis.hgetall(f"{self.AUDIT_LOG_PREFIX}{log_id}")
                if log_data.get("status") == "failure":
                    recent_failures += 1

            return AuditLogStats(
                total_events=int(total),
                events_by_type={k: int(v) for k, v in events_by_type.items()},
                events_by_action={k: int(v) for k, v in events_by_action.items()},
                events_by_status={k: int(v) for k, v in events_by_status.items()},
                top_actors=[],  # TODO: Implement top actors tracking
                recent_failures=recent_failures,
            )

        except Exception as e:
            logger.error(f"Failed to get audit stats: {e}")
            return AuditLogStats(
                total_events=0,
                events_by_type={},
                events_by_action={},
                events_by_status={},
                top_actors=[],
                recent_failures=0,
            )

    async def cleanup_old_logs(self):
        """Clean up old audit logs beyond retention period."""
        try:
            redis = await self._get_redis()

            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            cutoff_score = cutoff_date.timestamp()

            # Get old log IDs
            old_log_ids = await redis.zrangebyscore(
                self.AUDIT_INDEX_KEY,
                min=0,
                max=cutoff_score,
            )

            if old_log_ids:
                # Remove from index
                await redis.zremrangebyscore(self.AUDIT_INDEX_KEY, 0, cutoff_score)

                # Delete log entries
                for log_id in old_log_ids:
                    await redis.delete(f"{self.AUDIT_LOG_PREFIX}{log_id}")

                logger.info(f"Cleaned up {len(old_log_ids)} old audit logs")

        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")
