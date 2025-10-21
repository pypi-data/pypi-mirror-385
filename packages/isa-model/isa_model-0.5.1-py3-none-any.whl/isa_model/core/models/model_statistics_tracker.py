"""
Model Statistics Tracker - Aggregated Usage Tracking

Replaces the detailed ModelBillingTracker with efficient daily aggregation.
Instead of storing every individual request, we aggregate usage by model per day.
"""

import logging
from datetime import datetime, timezone, date
from typing import Dict, Any, Optional, List
from decimal import Decimal

logger = logging.getLogger(__name__)

class ModelStatisticsTracker:
    """Tracks aggregated model usage statistics efficiently"""
    
    def __init__(self, model_registry=None):
        """Initialize the statistics tracker"""
        self.model_registry = model_registry
        self._daily_cache = {}  # Cache for today's statistics
        
    def track_usage(self,
                   model_id: str,
                   provider: str,
                   service_type: str,
                   operation_type: str = "inference",
                   operation: str = "",
                   input_tokens: Optional[int] = None,
                   output_tokens: Optional[int] = None,
                   total_tokens: Optional[int] = None,
                   input_units: Optional[float] = None,
                   output_units: Optional[float] = None,
                   cost_usd: float = 0.0,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Track model usage by updating daily aggregated statistics
        
        Args:
            model_id: Model identifier
            provider: Provider name (openai, anthropic, etc.)
            service_type: Type of service (llm, vision, embedding, etc.)
            operation_type: Type of operation (usually "inference")
            operation: Specific operation name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens  
            total_tokens: Total tokens (input + output)
            input_units: Input units for non-token services
            output_units: Output units for non-token services
            cost_usd: Cost in USD
            metadata: Additional metadata
            
        Returns:
            bool: True if tracking succeeded
        """
        try:
            today = date.today()
            cache_key = f"{model_id}_{provider}_{service_type}_{operation_type}_{today}"
            
            # Get current stats from cache or database
            if cache_key not in self._daily_cache:
                self._daily_cache[cache_key] = self._get_daily_stats(
                    model_id, provider, service_type, operation_type, today
                )
            
            # Update statistics
            stats = self._daily_cache[cache_key]
            stats['total_requests'] += 1
            stats['total_input_tokens'] += input_tokens or 0
            stats['total_output_tokens'] += output_tokens or 0
            stats['total_tokens'] += total_tokens or (input_tokens or 0) + (output_tokens or 0)
            stats['total_input_units'] += Decimal(str(input_units or 0))
            stats['total_output_units'] += Decimal(str(output_units or 0))
            stats['total_cost_usd'] += Decimal(str(cost_usd))
            stats['last_updated'] = datetime.now(timezone.utc)
            
            # Save to database immediately (upsert)
            self._save_daily_stats(stats)
            
            logger.debug(f"Tracked usage: {model_id} - {operation_type} - ${cost_usd:.6f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track model usage: {e}")
            return False
    
    def _get_daily_stats(self, model_id: str, provider: str, service_type: str, 
                        operation_type: str, target_date: date) -> Dict[str, Any]:
        """Get or create daily statistics record"""
        try:
            if not self.model_registry or not hasattr(self.model_registry, 'supabase_client'):
                # Return empty stats if no database connection
                return self._create_empty_stats(model_id, provider, service_type, operation_type, target_date)
            
            result = self.model_registry.supabase_client.table('model_statistics').select('*').eq(
                'model_id', model_id
            ).eq('provider', provider).eq('service_type', service_type).eq(
                'operation_type', operation_type
            ).eq('date', target_date.isoformat()).execute()
            
            if result.data and len(result.data) > 0:
                # Convert to proper types
                stats = result.data[0].copy()
                stats['total_input_units'] = Decimal(str(stats.get('total_input_units', 0)))
                stats['total_output_units'] = Decimal(str(stats.get('total_output_units', 0)))
                stats['total_cost_usd'] = Decimal(str(stats.get('total_cost_usd', 0)))
                return stats
            else:
                # Create new record
                return self._create_empty_stats(model_id, provider, service_type, operation_type, target_date)
                
        except Exception as e:
            logger.error(f"Failed to get daily stats: {e}")
            return self._create_empty_stats(model_id, provider, service_type, operation_type, target_date)
    
    def _create_empty_stats(self, model_id: str, provider: str, service_type: str, 
                           operation_type: str, target_date: date) -> Dict[str, Any]:
        """Create empty statistics record"""
        return {
            'model_id': model_id,
            'provider': provider,
            'service_type': service_type,
            'operation_type': operation_type,
            'date': target_date.isoformat(),
            'total_requests': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_tokens': 0,
            'total_input_units': Decimal('0'),
            'total_output_units': Decimal('0'),
            'total_cost_usd': Decimal('0'),
            'last_updated': datetime.now(timezone.utc),
            'created_at': datetime.now(timezone.utc)
        }
    
    def _save_daily_stats(self, stats: Dict[str, Any]) -> bool:
        """Save daily statistics to database"""
        try:
            if not self.model_registry or not hasattr(self.model_registry, 'supabase_client'):
                logger.warning("No Supabase client available for statistics saving")
                return False
            
            # Convert Decimal to float for JSON serialization
            save_data = stats.copy()
            save_data['total_input_units'] = float(stats['total_input_units'])
            save_data['total_output_units'] = float(stats['total_output_units'])
            save_data['total_cost_usd'] = float(stats['total_cost_usd'])
            # Handle datetime conversion for last_updated
            if isinstance(stats['last_updated'], str):
                save_data['last_updated'] = stats['last_updated']
            else:
                save_data['last_updated'] = stats['last_updated'].isoformat()
            
            # Handle datetime conversion for created_at
            created_at = stats.get('created_at', datetime.now(timezone.utc))
            if isinstance(created_at, str):
                save_data['created_at'] = created_at
            else:
                save_data['created_at'] = created_at.isoformat()
            
            # Upsert to handle duplicates
            result = self.model_registry.supabase_client.table('model_statistics').upsert(
                save_data,
                on_conflict='model_id,provider,service_type,operation_type,date'
            ).execute()
            
            if result.data:
                logger.debug(f"Updated statistics for {stats['model_id']} on {stats['date']}")
                return True
            else:
                logger.warning("Failed to save statistics to database")
                return False
                
        except Exception as e:
            logger.error(f"Failed to save daily statistics: {e}")
            return False
    
    def get_model_summary(self, model_id: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get usage summary for a model or all models"""
        try:
            if not self.model_registry or not hasattr(self.model_registry, 'supabase_client'):
                return []
            
            query = self.model_registry.supabase_client.table('model_statistics').select('*')
            
            if model_id:
                query = query.eq('model_id', model_id)
            
            if days > 0:
                from datetime import timedelta
                start_date = (date.today() - timedelta(days=days)).isoformat()
                query = query.gte('date', start_date)
            
            result = query.order('date', desc=True).execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Failed to get model summary: {e}")
            return []
    
    def get_daily_totals(self, target_date: date = None) -> Dict[str, Any]:
        """Get total usage for a specific date"""
        if target_date is None:
            target_date = date.today()
            
        try:
            if not self.model_registry or not hasattr(self.model_registry, 'supabase_client'):
                return {}
            
            result = self.model_registry.supabase_client.table('model_statistics').select(
                'total_requests,total_input_tokens,total_output_tokens,total_cost_usd'
            ).eq('date', target_date.isoformat()).execute()
            
            if not result.data:
                return {'total_requests': 0, 'total_cost': 0.0}
            
            totals = {
                'total_requests': sum(row.get('total_requests', 0) for row in result.data),
                'total_input_tokens': sum(row.get('total_input_tokens', 0) for row in result.data),
                'total_output_tokens': sum(row.get('total_output_tokens', 0) for row in result.data),
                'total_cost': sum(float(row.get('total_cost_usd', 0)) for row in result.data),
                'date': target_date.isoformat()
            }
            
            return totals
            
        except Exception as e:
            logger.error(f"Failed to get daily totals: {e}")
            return {'total_requests': 0, 'total_cost': 0.0}
    
    def clear_cache(self):
        """Clear the daily cache"""
        self._daily_cache.clear()
        logger.debug("Statistics cache cleared")