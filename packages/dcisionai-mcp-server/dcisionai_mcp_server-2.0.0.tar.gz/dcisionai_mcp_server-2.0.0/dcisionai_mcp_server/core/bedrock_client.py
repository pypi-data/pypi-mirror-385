#!/usr/bin/env python3
"""
Bedrock Client with Multi-Region Failover and Rate Limiting
"""

import asyncio
import json
import logging
import time
from collections import deque
from typing import List

import boto3

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        async with self.lock:
            now = time.time()
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()
            while len(self.calls) >= self.max_calls:
                await asyncio.sleep(0.1)
                now = time.time()
                while self.calls and self.calls[0] < now - self.period:
                    self.calls.popleft()
            self.calls.append(now)


class BedrockClient:
    """AWS Bedrock client with multi-region failover and rate limiting"""
    
    def __init__(self, regions: List[str] = None):
        self.regions = regions or ['us-east-1', 'us-west-2']
        self.current = 0
        self.clients = {}
        
        for r in self.regions:
            try:
                self.clients[r] = boto3.client('bedrock-runtime', region_name=r)
            except Exception as e:
                logger.error(f"Failed to init {r}: {e}")
        
        self.limiters = {
            'haiku': RateLimiter(10, 1.0),
            'sonnet': RateLimiter(5, 1.0)
        }
    
    async def invoke(self, model_id: str, prompt: str, max_tokens: int = 4000) -> str:
        """Invoke Bedrock model with failover and rate limiting"""
        limiter = self.limiters['haiku' if 'haiku' in model_id.lower() else 'sonnet']
        await limiter.acquire()
        
        for attempt in range(len(self.regions)):
            region = self.regions[self.current]
            client = self.clients.get(region)
            if not client:
                self.current = (self.current + 1) % len(self.regions)
                continue
            
            try:
                # Clean prompt to ensure JSON serializability
                def clean_for_json(obj):
                    if isinstance(obj, dict):
                        return {k: clean_for_json(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [clean_for_json(item) for item in obj]
                    elif isinstance(obj, (str, int, float, bool, type(None))):
                        return obj
                    else:
                        return str(obj)
                
                cleaned_prompt = clean_for_json(prompt)
                
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": 0.1,
                    "messages": [{"role": "user", "content": cleaned_prompt}]
                })
                
                resp = await asyncio.to_thread(
                    client.invoke_model,
                    modelId=model_id,
                    body=body,
                    contentType="application/json"
                )
                
                data = json.loads(resp['body'].read())
                if 'content' in data:
                    return data['content'][0]['text']
                elif 'completion' in data:
                    return data['completion']
                raise ValueError("Unexpected response")
                
            except Exception as e:
                if "ServiceUnavailable" in str(e) or "Throttling" in str(e):
                    self.current = (self.current + 1) % len(self.regions)
                    if attempt < len(self.regions) - 1:
                        continue
                raise
        
        raise RuntimeError("All regions failed")
