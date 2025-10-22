"""AgentBill LangChain Callback Handler"""

import time
import hashlib
import json
from typing import Any, Dict, List, Optional
from uuid import UUID

try:
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import LLMResult
except ImportError:
    raise ImportError(
        "langchain is not installed. Install with: pip install langchain"
    )

import requests


class AgentBillCallback(BaseCallbackHandler):
    """LangChain callback handler that sends usage data to AgentBill.
    
    Example:
        callback = AgentBillCallback(
            api_key="agb_your_key",
            base_url="https://your-instance.supabase.co",
            customer_id="customer-123"
        )
        
        llm = ChatOpenAI(callbacks=[callback])
        result = llm.invoke("Hello!")
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        customer_id: Optional[str] = None,
        account_id: Optional[str] = None,
        debug: bool = False,
        batch_size: int = 10,
        flush_interval: float = 5.0
    ):
        """Initialize AgentBill callback.
        
        Args:
            api_key: AgentBill API key (get from dashboard)
            base_url: AgentBill base URL (e.g., https://xxx.supabase.co)
            customer_id: Optional customer ID for tracking
            account_id: Optional account ID for tracking
            debug: Enable debug logging
            batch_size: Number of signals to batch before sending
            flush_interval: Seconds between automatic flushes
        """
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.customer_id = customer_id
        self.account_id = account_id
        self.debug = debug
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        # Track active LLM calls
        self._active_runs: Dict[str, Dict[str, Any]] = {}
        
        # Batch queue
        self._signal_queue: List[Dict[str, Any]] = []
        self._last_flush = time.time()
        
        if self.debug:
            print(f"[AgentBill] Initialized with base_url={self.base_url}")
    
    def _hash_prompt(self, text: str) -> str:
        """Hash prompt for privacy."""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def _extract_provider(self, serialized: Dict[str, Any]) -> str:
        """Extract provider from LLM serialization."""
        # Check id field
        for id_item in serialized.get("id", []):
            if "openai" in id_item.lower():
                return "openai"
            if "anthropic" in id_item.lower():
                return "anthropic"
            if "cohere" in id_item.lower():
                return "cohere"
            if "bedrock" in id_item.lower():
                return "bedrock"
        
        # Check kwargs
        kwargs = serialized.get("kwargs", {})
        if "openai" in str(kwargs).lower():
            return "openai"
        if "anthropic" in str(kwargs).lower():
            return "anthropic"
        
        return "unknown"
    
    def _extract_model(self, serialized: Dict[str, Any]) -> str:
        """Extract model name from LLM serialization."""
        # Try model_name in kwargs
        kwargs = serialized.get("kwargs", {})
        if "model_name" in kwargs:
            return kwargs["model_name"]
        if "model" in kwargs:
            return kwargs["model"]
        
        # Try id field
        for id_item in serialized.get("id", []):
            if "gpt" in id_item.lower():
                return id_item
            if "claude" in id_item.lower():
                return id_item
        
        return "unknown"
    
    def _send_signal(self, signal: Dict[str, Any]) -> None:
        """Send signal to AgentBill."""
        try:
            url = f"{self.base_url}/functions/v1/record-signals"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
            }
            
            if self.debug:
                print(f"[AgentBill] Sending signal: {signal.get('event_name')}")
            
            response = requests.post(url, json=[signal], headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"[AgentBill] Error sending signal: {response.status_code} {response.text}")
            elif self.debug:
                print(f"[AgentBill] Signal sent successfully")
                
        except Exception as e:
            if self.debug:
                print(f"[AgentBill] Error sending signal: {e}")
    
    def _queue_signal(self, signal: Dict[str, Any]) -> None:
        """Add signal to queue and flush if needed."""
        self._signal_queue.append(signal)
        
        # Flush if batch size reached or interval exceeded
        now = time.time()
        should_flush = (
            len(self._signal_queue) >= self.batch_size or
            (now - self._last_flush) >= self.flush_interval
        )
        
        if should_flush:
            self.flush()
    
    def flush(self) -> None:
        """Flush queued signals to AgentBill."""
        if not self._signal_queue:
            return
        
        try:
            url = f"{self.base_url}/functions/v1/record-signals"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
            }
            
            if self.debug:
                print(f"[AgentBill] Flushing {len(self._signal_queue)} signals")
            
            response = requests.post(
                url,
                json=self._signal_queue,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self._signal_queue.clear()
                self._last_flush = time.time()
                if self.debug:
                    print(f"[AgentBill] Flush successful")
            else:
                print(f"[AgentBill] Flush error: {response.status_code} {response.text}")
                
        except Exception as e:
            if self.debug:
                print(f"[AgentBill] Flush error: {e}")
    
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any
    ) -> None:
        """Called when LLM starts."""
        run_id = kwargs.get("run_id") or str(UUID(int=0))
        
        # Extract metadata
        provider = self._extract_provider(serialized)
        model = self._extract_model(serialized)
        
        # Store run info
        self._active_runs[str(run_id)] = {
            "start_time": time.time(),
            "prompts": prompts,
            "provider": provider,
            "model": model,
            "prompt_hash": self._hash_prompt(prompts[0]) if prompts else None,
            "prompt_sample": prompts[0][:200] if prompts else None,
        }
        
        if self.debug:
            print(f"[AgentBill] LLM started: {model} ({provider})")
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM ends."""
        run_id = str(kwargs.get("run_id", ""))
        run_info = self._active_runs.pop(run_id, None)
        
        if not run_info:
            return
        
        # Calculate latency
        latency_ms = int((time.time() - run_info["start_time"]) * 1000)
        
        # Extract token usage
        llm_output = response.llm_output or {}
        token_usage = llm_output.get("token_usage", {})
        
        prompt_tokens = token_usage.get("prompt_tokens", 0)
        completion_tokens = token_usage.get("completion_tokens", 0)
        total_tokens = token_usage.get("total_tokens", prompt_tokens + completion_tokens)
        
        # Build signal
        signal = {
            "event_name": "langchain_llm_call",
            "model": run_info["model"],
            "provider": run_info["provider"],
            "prompt_hash": run_info["prompt_hash"],
            "prompt_sample": run_info["prompt_sample"],
            "metrics": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
            "latency_ms": latency_ms,
            "data_source": "langchain",
        }
        
        # Add customer/account if provided
        if self.customer_id:
            signal["account_external_id"] = self.customer_id
        if self.account_id:
            signal["account_id"] = self.account_id
        
        # Queue signal
        self._queue_signal(signal)
        
        if self.debug:
            print(f"[AgentBill] LLM ended: {total_tokens} tokens, {latency_ms}ms")
    
    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when LLM errors."""
        run_id = str(kwargs.get("run_id", ""))
        self._active_runs.pop(run_id, None)
        
        if self.debug:
            print(f"[AgentBill] LLM error: {error}")
    
    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any
    ) -> None:
        """Called when chain starts."""
        if self.debug:
            chain_name = serialized.get("id", ["unknown"])[-1]
            print(f"[AgentBill] Chain started: {chain_name}")
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Called when chain ends."""
        if self.debug:
            print(f"[AgentBill] Chain ended")
    
    def track_revenue(
        self,
        event_name: str,
        revenue: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track revenue for profitability analysis.
        
        Args:
            event_name: Event name (e.g., "chat_completion")
            revenue: Revenue amount (what you charged)
            metadata: Additional metadata
        """
        signal = {
            "event_name": event_name,
            "conversion_value": revenue,
            "revenue_source": "langchain",
            "data": metadata or {},
        }
        
        if self.customer_id:
            signal["account_external_id"] = self.customer_id
        if self.account_id:
            signal["account_id"] = self.account_id
        
        self._queue_signal(signal)
        
        if self.debug:
            print(f"[AgentBill] Revenue tracked: ${revenue}")
    
    def __del__(self):
        """Flush on cleanup."""
        self.flush()
