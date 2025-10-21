"""
Analytics API Routes

Provides comprehensive analytics data for the ISA Model Platform including
usage statistics, cost analysis, model performance, and user activity metrics.
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timedelta, date
import asyncpg
import os
from collections import defaultdict

from ....core.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Database connection configuration
config_manager = ConfigManager()
DATABASE_URL = os.getenv("DATABASE_URL", config_manager.get_global_config().database.default_database_url)

class AnalyticsDateRange(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period: Optional[str] = "7d"  # 1d, 7d, 30d, 90d

class UsageStats(BaseModel):
    total_requests: int
    total_cost_usd: float
    total_tokens: int
    unique_models: int
    period_label: str

class ModelUsageStats(BaseModel):
    model_id: str
    provider: str
    service_type: str
    total_requests: int
    total_cost_usd: float
    total_tokens: int
    avg_daily_requests: float

class ServiceTypeStats(BaseModel):
    service_type: str
    total_requests: int
    total_cost_usd: float
    total_tokens: int
    model_count: int

async def get_db_connection():
    """Get database connection"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def parse_date_range(period: str) -> tuple:
    """Parse period string into start and end dates"""
    end_date = date.today()
    
    if period == "1d":
        start_date = end_date - timedelta(days=1)
    elif period == "7d":
        start_date = end_date - timedelta(days=7)
    elif period == "30d":
        start_date = end_date - timedelta(days=30)
    elif period == "90d":
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=7)
    
    return start_date, end_date

@router.get("/overview")
async def get_analytics_overview(
    period: str = Query("7d", description="Time period (1d, 7d, 30d, 90d)")
):
    """Get high-level analytics overview"""
    try:
        start_date, end_date = parse_date_range(period)
        
        conn = await get_db_connection()
        try:
            # Get overall statistics
            stats_query = """
            SELECT 
                SUM(total_requests) as total_requests,
                SUM(total_cost_usd) as total_cost_usd,
                SUM(total_tokens) as total_tokens,
                COUNT(DISTINCT model_id) as unique_models,
                COUNT(DISTINCT provider) as unique_providers,
                COUNT(DISTINCT service_type) as unique_services
            FROM dev.model_statistics 
            WHERE date >= $1 AND date <= $2
            """
            
            stats_result = await conn.fetchrow(stats_query, start_date, end_date)
            
            # Get daily trend data
            trend_query = """
            SELECT 
                date,
                SUM(total_requests) as daily_requests,
                SUM(total_cost_usd) as daily_cost,
                SUM(total_tokens) as daily_tokens
            FROM dev.model_statistics 
            WHERE date >= $1 AND date <= $2
            GROUP BY date
            ORDER BY date
            """
            
            trend_results = await conn.fetch(trend_query, start_date, end_date)
            
            # Format response
            overview = {
                "summary": {
                    "total_requests": int(stats_result["total_requests"] or 0),
                    "total_cost_usd": float(stats_result["total_cost_usd"] or 0),
                    "total_tokens": int(stats_result["total_tokens"] or 0),
                    "unique_models": int(stats_result["unique_models"] or 0),
                    "unique_providers": int(stats_result["unique_providers"] or 0),
                    "unique_services": int(stats_result["unique_services"] or 0),
                    "period": period,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "daily_trends": [
                    {
                        "date": row["date"].isoformat(),
                        "requests": int(row["daily_requests"] or 0),
                        "cost_usd": float(row["daily_cost"] or 0),
                        "tokens": int(row["daily_tokens"] or 0)
                    }
                    for row in trend_results
                ]
            }
            
            return overview
            
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics overview: {str(e)}")

@router.get("/models")
async def get_model_analytics(
    period: str = Query("7d", description="Time period"),
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    limit: int = Query(20, description="Limit number of results")
):
    """Get model usage analytics"""
    try:
        start_date, end_date = parse_date_range(period)
        
        conn = await get_db_connection()
        try:
            # Build query with optional service type filter
            where_clause = "WHERE date >= $1 AND date <= $2"
            params = [start_date, end_date]
            
            if service_type:
                where_clause += " AND service_type = $3"
                params.append(service_type)
            
            # Calculate days for average calculation
            days_in_period = (end_date - start_date).days + 1
            
            if service_type:
                query = """
                SELECT 
                    model_id,
                    provider,
                    service_type,
                    SUM(total_requests) as total_requests,
                    SUM(total_cost_usd) as total_cost_usd,
                    SUM(total_tokens) as total_tokens,
                    ROUND(SUM(total_requests)::numeric / $4, 2) as avg_daily_requests
                FROM dev.model_statistics 
                WHERE date >= $1 AND date <= $2 AND service_type = $3
                GROUP BY model_id, provider, service_type
                ORDER BY total_requests DESC
                LIMIT $5
                """
                params = [start_date, end_date, service_type, days_in_period, limit]
            else:
                query = """
                SELECT 
                    model_id,
                    provider,
                    service_type,
                    SUM(total_requests) as total_requests,
                    SUM(total_cost_usd) as total_cost_usd,
                    SUM(total_tokens) as total_tokens,
                    ROUND(SUM(total_requests)::numeric / $3, 2) as avg_daily_requests
                FROM dev.model_statistics 
                WHERE date >= $1 AND date <= $2
                GROUP BY model_id, provider, service_type
                ORDER BY total_requests DESC
                LIMIT $4
                """
                params = [start_date, end_date, days_in_period, limit]
            
            results = await conn.fetch(query, *params)
            
            models = [
                {
                    "model_id": row["model_id"],
                    "provider": row["provider"],
                    "service_type": row["service_type"],
                    "total_requests": int(row["total_requests"] or 0),
                    "total_cost_usd": float(row["total_cost_usd"] or 0),
                    "total_tokens": int(row["total_tokens"] or 0),
                    "avg_daily_requests": float(row["avg_daily_requests"] or 0)
                }
                for row in results
            ]
            
            return {
                "models": models,
                "period": period,
                "service_type_filter": service_type,
                "total_models": len(models)
            }
            
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Error getting model analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model analytics: {str(e)}")

@router.get("/services")
async def get_service_analytics(
    period: str = Query("7d", description="Time period")
):
    """Get service type analytics"""
    try:
        start_date, end_date = parse_date_range(period)
        
        conn = await get_db_connection()
        try:
            query = """
            SELECT 
                service_type,
                SUM(total_requests) as total_requests,
                SUM(total_cost_usd) as total_cost_usd,
                SUM(total_tokens) as total_tokens,
                COUNT(DISTINCT model_id) as model_count,
                COUNT(DISTINCT provider) as provider_count
            FROM dev.model_statistics 
            WHERE date >= $1 AND date <= $2
            GROUP BY service_type
            ORDER BY total_requests DESC
            """
            
            results = await conn.fetch(query, start_date, end_date)
            
            services = [
                {
                    "service_type": row["service_type"],
                    "total_requests": int(row["total_requests"] or 0),
                    "total_cost_usd": float(row["total_cost_usd"] or 0),
                    "total_tokens": int(row["total_tokens"] or 0),
                    "model_count": int(row["model_count"] or 0),
                    "provider_count": int(row["provider_count"] or 0)
                }
                for row in results
            ]
            
            return {
                "services": services,
                "period": period,
                "total_services": len(services)
            }
            
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Error getting service analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get service analytics: {str(e)}")

@router.get("/costs")
async def get_cost_analytics(
    period: str = Query("7d", description="Time period"),
    breakdown: str = Query("daily", description="Breakdown type (daily, service, model, provider)")
):
    """Get detailed cost analytics"""
    try:
        start_date, end_date = parse_date_range(period)
        
        conn = await get_db_connection()
        try:
            if breakdown == "daily":
                query = """
                SELECT 
                    date,
                    SUM(total_cost_usd) as total_cost,
                    SUM(total_requests) as total_requests
                FROM dev.model_statistics 
                WHERE date >= $1 AND date <= $2
                GROUP BY date
                ORDER BY date
                """
                
            elif breakdown == "service":
                query = """
                SELECT 
                    service_type as category,
                    SUM(total_cost_usd) as total_cost,
                    SUM(total_requests) as total_requests
                FROM dev.model_statistics 
                WHERE date >= $1 AND date <= $2
                GROUP BY service_type
                ORDER BY total_cost DESC
                """
                
            elif breakdown == "model":
                query = """
                SELECT 
                    model_id as category,
                    SUM(total_cost_usd) as total_cost,
                    SUM(total_requests) as total_requests
                FROM dev.model_statistics 
                WHERE date >= $1 AND date <= $2
                GROUP BY model_id
                ORDER BY total_cost DESC
                LIMIT 10
                """
                
            elif breakdown == "provider":
                query = """
                SELECT 
                    provider as category,
                    SUM(total_cost_usd) as total_cost,
                    SUM(total_requests) as total_requests
                FROM dev.model_statistics 
                WHERE date >= $1 AND date <= $2
                GROUP BY provider
                ORDER BY total_cost DESC
                """
                
            else:
                raise HTTPException(status_code=400, detail="Invalid breakdown type")
            
            results = await conn.fetch(query, start_date, end_date)
            
            cost_data = []
            for row in results:
                if breakdown == "daily":
                    cost_data.append({
                        "date": row["date"].isoformat(),
                        "total_cost": float(row["total_cost"] or 0),
                        "total_requests": int(row["total_requests"] or 0)
                    })
                else:
                    cost_data.append({
                        "category": row["category"],
                        "total_cost": float(row["total_cost"] or 0),
                        "total_requests": int(row["total_requests"] or 0)
                    })
            
            return {
                "cost_data": cost_data,
                "breakdown": breakdown,
                "period": period,
                "total_entries": len(cost_data)
            }
            
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Error getting cost analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cost analytics: {str(e)}")

@router.get("/users")
async def get_user_analytics(
    period: str = Query("7d", description="Time period"),
    limit: int = Query(10, description="Limit number of results")
):
    """Get user activity analytics"""
    try:
        start_date, end_date = parse_date_range(period)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        conn = await get_db_connection()
        try:
            # Get user usage statistics
            user_query = """
            SELECT 
                user_id,
                COUNT(*) as total_requests,
                SUM(cost_usd) as total_cost,
                SUM(tokens_used) as total_tokens,
                COUNT(DISTINCT DATE(created_at)) as active_days
            FROM dev.user_usage_records 
            WHERE created_at >= $1 AND created_at <= $2
            GROUP BY user_id
            ORDER BY total_requests DESC
            LIMIT $3
            """
            
            user_results = await conn.fetch(user_query, start_datetime, end_datetime, limit)
            
            # Get daily user activity
            daily_query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(DISTINCT user_id) as active_users,
                COUNT(*) as total_requests
            FROM dev.user_usage_records 
            WHERE created_at >= $1 AND created_at <= $2
            GROUP BY DATE(created_at)
            ORDER BY date
            """
            
            daily_results = await conn.fetch(daily_query, start_datetime, end_datetime)
            
            users = [
                {
                    "user_id": row["user_id"],
                    "total_requests": int(row["total_requests"] or 0),
                    "total_cost": float(row["total_cost"] or 0),
                    "total_tokens": int(row["total_tokens"] or 0),
                    "active_days": int(row["active_days"] or 0)
                }
                for row in user_results
            ]
            
            daily_activity = [
                {
                    "date": row["date"].isoformat(),
                    "active_users": int(row["active_users"] or 0),
                    "total_requests": int(row["total_requests"] or 0)
                }
                for row in daily_results
            ]
            
            return {
                "top_users": users,
                "daily_activity": daily_activity,
                "period": period,
                "total_users_shown": len(users)
            }
            
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user analytics: {str(e)}")

@router.get("/health")
async def analytics_health():
    """Health check for analytics service"""
    try:
        conn = await get_db_connection()
        try:
            # Test database connectivity
            result = await conn.fetchval("SELECT COUNT(*) FROM dev.model_statistics")
            
            return {
                "status": "healthy",
                "service": "analytics",
                "total_model_records": result,
                "database": "connected"
            }
            
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Analytics health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "analytics",
            "error": str(e)
        }