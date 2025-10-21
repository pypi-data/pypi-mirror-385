"""
Webhooks API Routes

Provides webhook management and notification system for:
- Training job status changes
- Deployment status updates
- Model evaluation completion
- System alerts and notifications
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
import logging
import asyncio
import json
import uuid
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response Models
class WebhookConfig(BaseModel):
    """Configuration for a webhook endpoint"""
    url: HttpUrl
    events: List[str] = ["*"]  # Which events to listen for
    active: bool = True
    secret: Optional[str] = None  # For webhook signature verification
    headers: Dict[str, str] = {}  # Custom headers to send

class WebhookRequest(BaseModel):
    """Request to create or update a webhook"""
    name: str
    url: HttpUrl
    events: List[str] = ["training.completed", "deployment.completed", "evaluation.completed"]
    active: bool = True
    secret: Optional[str] = None
    headers: Dict[str, str] = {}

class WebhookPayload(BaseModel):
    """Standard webhook payload format"""
    event: str
    timestamp: str
    data: Dict[str, Any]
    webhook_id: str

class WebhookDelivery(BaseModel):
    """Webhook delivery status"""
    webhook_id: str
    event: str
    status: str  # pending, delivered, failed
    attempts: int = 0
    max_attempts: int = 3
    last_attempt: Optional[str] = None
    response_status: Optional[int] = None
    error_message: Optional[str] = None

# In-memory webhook storage (in production, use database)
webhooks = {}
deliveries = {}

@router.get("/health")
async def webhooks_health():
    """Health check for webhooks service"""
    return {
        "status": "healthy",
        "service": "webhooks",
        "active_webhooks": len([w for w in webhooks.values() if w["active"]]),
        "total_webhooks": len(webhooks)
    }

@router.post("/")
async def create_webhook(request: WebhookRequest):
    """
    Create a new webhook endpoint
    """
    try:
        webhook_id = str(uuid.uuid4())
        
        webhook_config = {
            "id": webhook_id,
            "name": request.name,
            "url": str(request.url),
            "events": request.events,
            "active": request.active,
            "secret": request.secret,
            "headers": request.headers,
            "created_at": datetime.utcnow().isoformat(),
            "last_delivery": None,
            "total_deliveries": 0,
            "failed_deliveries": 0
        }
        
        webhooks[webhook_id] = webhook_config
        
        logger.info(f"Created webhook {webhook_id} for {request.name}")
        
        return {
            "success": True,
            "webhook_id": webhook_id,
            "message": f"Webhook '{request.name}' created successfully",
            "config": webhook_config
        }
        
    except Exception as e:
        logger.error(f"Failed to create webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create webhook: {str(e)}")

@router.get("/")
async def list_webhooks():
    """
    List all configured webhooks
    """
    try:
        webhook_list = []
        
        for webhook_id, config in webhooks.items():
            webhook_summary = {
                "id": webhook_id,
                "name": config["name"],
                "url": config["url"],
                "events": config["events"],
                "active": config["active"],
                "created_at": config["created_at"],
                "total_deliveries": config["total_deliveries"],
                "failed_deliveries": config["failed_deliveries"],
                "last_delivery": config["last_delivery"]
            }
            webhook_list.append(webhook_summary)
        
        return {
            "success": True,
            "webhooks": webhook_list,
            "total_count": len(webhook_list)
        }
        
    except Exception as e:
        logger.error(f"Failed to list webhooks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list webhooks: {str(e)}")

@router.get("/{webhook_id}")
async def get_webhook(webhook_id: str):
    """
    Get detailed information about a specific webhook
    """
    try:
        if webhook_id not in webhooks:
            raise HTTPException(status_code=404, detail=f"Webhook not found: {webhook_id}")
        
        webhook_config = webhooks[webhook_id]
        
        # Get recent deliveries for this webhook
        recent_deliveries = [
            delivery for delivery in deliveries.values() 
            if delivery.get("webhook_id") == webhook_id
        ]
        
        # Sort by timestamp, most recent first
        recent_deliveries.sort(key=lambda x: x.get("last_attempt", ""), reverse=True)
        
        return {
            "success": True,
            "webhook": webhook_config,
            "recent_deliveries": recent_deliveries[:10]  # Last 10 deliveries
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get webhook {webhook_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get webhook: {str(e)}")

@router.put("/{webhook_id}")
async def update_webhook(webhook_id: str, request: WebhookRequest):
    """
    Update an existing webhook configuration
    """
    try:
        if webhook_id not in webhooks:
            raise HTTPException(status_code=404, detail=f"Webhook not found: {webhook_id}")
        
        webhook_config = webhooks[webhook_id]
        
        # Update configuration
        webhook_config.update({
            "name": request.name,
            "url": str(request.url),
            "events": request.events,
            "active": request.active,
            "secret": request.secret,
            "headers": request.headers,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Updated webhook {webhook_id}")
        
        return {
            "success": True,
            "message": f"Webhook '{request.name}' updated successfully",
            "config": webhook_config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update webhook {webhook_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update webhook: {str(e)}")

@router.delete("/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """
    Delete a webhook endpoint
    """
    try:
        if webhook_id not in webhooks:
            raise HTTPException(status_code=404, detail=f"Webhook not found: {webhook_id}")
        
        webhook_name = webhooks[webhook_id]["name"]
        del webhooks[webhook_id]
        
        # Clean up associated deliveries
        deliveries_to_remove = [
            delivery_id for delivery_id, delivery in deliveries.items()
            if delivery.get("webhook_id") == webhook_id
        ]
        
        for delivery_id in deliveries_to_remove:
            del deliveries[delivery_id]
        
        logger.info(f"Deleted webhook {webhook_id} and {len(deliveries_to_remove)} deliveries")
        
        return {
            "success": True,
            "message": f"Webhook '{webhook_name}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete webhook {webhook_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete webhook: {str(e)}")

@router.post("/{webhook_id}/test")
async def test_webhook(webhook_id: str, background_tasks: BackgroundTasks):
    """
    Send a test event to a webhook endpoint
    """
    try:
        if webhook_id not in webhooks:
            raise HTTPException(status_code=404, detail=f"Webhook not found: {webhook_id}")
        
        test_payload = {
            "event": "webhook.test",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "message": "This is a test webhook delivery",
                "webhook_id": webhook_id,
                "test": True
            },
            "webhook_id": webhook_id
        }
        
        # Send webhook in background
        background_tasks.add_task(deliver_webhook, webhook_id, test_payload)
        
        return {
            "success": True,
            "message": f"Test webhook sent to {webhooks[webhook_id]['name']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test webhook {webhook_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test webhook: {str(e)}")

@router.get("/deliveries/")
async def list_deliveries(limit: int = 50, webhook_id: Optional[str] = None):
    """
    List recent webhook deliveries
    """
    try:
        delivery_list = []
        
        for delivery_id, delivery in deliveries.items():
            if webhook_id and delivery.get("webhook_id") != webhook_id:
                continue
                
            delivery_info = {
                "delivery_id": delivery_id,
                "webhook_id": delivery.get("webhook_id"),
                "webhook_name": webhooks.get(delivery.get("webhook_id"), {}).get("name", "Unknown"),
                "event": delivery.get("event"),
                "status": delivery.get("status"),
                "attempts": delivery.get("attempts"),
                "last_attempt": delivery.get("last_attempt"),
                "response_status": delivery.get("response_status"),
                "error_message": delivery.get("error_message")
            }
            delivery_list.append(delivery_info)
        
        # Sort by last attempt, most recent first
        delivery_list.sort(key=lambda x: x.get("last_attempt", ""), reverse=True)
        
        return {
            "success": True,
            "deliveries": delivery_list[:limit],
            "total_count": len(delivery_list)
        }
        
    except Exception as e:
        logger.error(f"Failed to list deliveries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list deliveries: {str(e)}")

# Webhook delivery functions

async def deliver_webhook(webhook_id: str, payload: Dict[str, Any]):
    """
    Deliver a webhook payload to the configured endpoint
    """
    try:
        if webhook_id not in webhooks:
            logger.warning(f"Webhook {webhook_id} not found for delivery")
            return
        
        webhook_config = webhooks[webhook_id]
        
        if not webhook_config["active"]:
            logger.debug(f"Webhook {webhook_id} is inactive, skipping delivery")
            return
        
        # Check if webhook should receive this event
        events = webhook_config.get("events", ["*"])
        event_type = payload.get("event", "")
        
        if "*" not in events and event_type not in events:
            logger.debug(f"Webhook {webhook_id} not configured for event {event_type}")
            return
        
        delivery_id = str(uuid.uuid4())
        delivery_record = {
            "delivery_id": delivery_id,
            "webhook_id": webhook_id,
            "event": event_type,
            "status": "pending",
            "attempts": 0,
            "max_attempts": 3,
            "created_at": datetime.utcnow().isoformat()
        }
        
        deliveries[delivery_id] = delivery_record
        
        # Attempt delivery with retries
        success = await attempt_delivery(webhook_config, payload, delivery_record)
        
        # Update webhook stats
        webhook_config["total_deliveries"] += 1
        webhook_config["last_delivery"] = datetime.utcnow().isoformat()
        
        if not success:
            webhook_config["failed_deliveries"] += 1
        
    except Exception as e:
        logger.error(f"Failed to deliver webhook {webhook_id}: {e}")

async def attempt_delivery(webhook_config: Dict, payload: Dict, delivery_record: Dict):
    """
    Attempt to deliver webhook with retries
    """
    url = webhook_config["url"]
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ISA-Model-Webhooks/1.0",
        **webhook_config.get("headers", {})
    }
    
    # Add signature if secret is provided
    if webhook_config.get("secret"):
        import hmac
        import hashlib
        
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        signature = hmac.new(
            webhook_config["secret"].encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        headers["X-ISA-Signature-256"] = f"sha256={signature}"
    
    max_attempts = delivery_record["max_attempts"]
    
    for attempt in range(max_attempts):
        try:
            delivery_record["attempts"] = attempt + 1
            delivery_record["last_attempt"] = datetime.utcnow().isoformat()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    delivery_record["response_status"] = response.status
                    
                    if response.status < 300:  # 2xx success
                        delivery_record["status"] = "delivered"
                        logger.info(f"Webhook delivered successfully to {url} (attempt {attempt + 1})")
                        return True
                    else:
                        error_text = await response.text()
                        delivery_record["error_message"] = f"HTTP {response.status}: {error_text[:200]}"
                        logger.warning(f"Webhook delivery failed with status {response.status}: {error_text[:100]}")
        
        except Exception as e:
            delivery_record["error_message"] = f"Connection error: {str(e)[:200]}"
            logger.warning(f"Webhook delivery attempt {attempt + 1} failed: {e}")
        
        # Wait before retry (exponential backoff)
        if attempt < max_attempts - 1:
            await asyncio.sleep(2 ** attempt)
    
    # All attempts failed
    delivery_record["status"] = "failed"
    logger.error(f"Webhook delivery failed after {max_attempts} attempts to {url}")
    return False

# Event publishing functions

async def publish_event(event_type: str, data: Dict[str, Any]):
    """
    Publish an event to all matching webhooks
    """
    try:
        payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        # Send to all active webhooks that match the event
        for webhook_id in webhooks:
            asyncio.create_task(deliver_webhook(webhook_id, {**payload, "webhook_id": webhook_id}))
        
        logger.info(f"Published event {event_type} to {len(webhooks)} webhooks")
        
    except Exception as e:
        logger.error(f"Failed to publish event {event_type}: {e}")

# Convenience functions for common events

async def notify_training_completed(job_id: str, job_name: str, status: str, **kwargs):
    """Notify about training job completion"""
    await publish_event("training.completed", {
        "job_id": job_id,
        "job_name": job_name,
        "status": status,
        **kwargs
    })

async def notify_deployment_completed(deployment_id: str, model_id: str, status: str, **kwargs):
    """Notify about deployment completion"""
    await publish_event("deployment.completed", {
        "deployment_id": deployment_id,
        "model_id": model_id,
        "status": status,
        **kwargs
    })

async def notify_evaluation_completed(evaluation_id: str, model_id: str, results: Dict, **kwargs):
    """Notify about evaluation completion"""
    await publish_event("evaluation.completed", {
        "evaluation_id": evaluation_id,
        "model_id": model_id,
        "results": results,
        **kwargs
    })