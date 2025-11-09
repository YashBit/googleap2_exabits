#!/usr/bin/env python3
"""
AP2 Transaction Executor - Makes requests to the running AP2 agents
Using proper A2A message format
"""

import requests
import time
import sys
import uuid
from pathlib import Path

# Add AP2 to path
AP2_PATH = Path(__file__).parent.parent.parent / "AP2"
sys.path.insert(0, str(AP2_PATH / "samples" / "python" / "src"))

try:
    from a2a import types as a2a_types
except ImportError:
    print("Installing a2a-sdk...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "a2a-sdk"])
    from a2a import types as a2a_types


class AP2TransactionExecutor:
    """Execute AP2 shopping transactions against running agents"""
    
    def __init__(self):
        self.merchant_url = "http://localhost:8001/a2a/merchant_agent"
        self.credentials_url = "http://localhost:8002/a2a/credentials_provider_agent"
        self.payment_processor_url = "http://localhost:8003/a2a/merchant_payment_processor_agent"
        self.context_id = uuid.uuid4().hex
    
    def execute_transaction(self, scenario="normal", timeout=30):
        """
        Execute a complete shopping transaction
        
        Returns dict with:
            - success: bool
            - duration: float
            - steps: int
            - error: str (if failed)
        """
        start_time = time.time()
        steps = 0
        
        try:
            if scenario == "normal":
                result = self._normal_transaction()
                steps = result.get('steps', 0)
                success = result.get('success', False)
                error = result.get('error', '')
            
            elif scenario == "infinite_loop":
                result = self._infinite_loop_transaction(timeout)
                steps = result.get('steps', 0)
                success = result.get('success', False)
                error = result.get('error', '')
            
            elif scenario == "retry_storm":
                result = self._retry_storm_transaction(timeout)
                steps = result.get('steps', 0)
                success = result.get('success', False)
                error = result.get('error', '')
            
            else:
                raise ValueError(f"Unknown scenario: {scenario}")
            
            duration = time.time() - start_time
            
            return {
                'success': success,
                'duration': duration,
                'steps': steps,
                'error': error
            }
        
        except Exception as e:
            duration = time.time() - start_time
            return {
                'success': False,
                'duration': duration,
                'steps': steps,
                'error': str(e)
            }
    
    def _build_a2a_message(self, text):
        """Build a proper A2A message"""
        message = a2a_types.Message(
            message_id=uuid.uuid4().hex,
            context_id=self.context_id,
            parts=[
                a2a_types.Part(root=a2a_types.TextPart(text=text))
            ],
            role=a2a_types.Role.user
        )
        return message.model_dump()
    
    def _send_message(self, url, text, timeout=10):
        """Send A2A message and return response"""
        message = self._build_a2a_message(text)
        response = requests.post(url, json=message, timeout=timeout)
        return response
    
    def _normal_transaction(self):
        """Normal successful purchase flow"""
        steps = 0
        
        try:
            # Step 1: Query merchant for products
            response = self._send_message(
                self.merchant_url,
                "Show me coffee mugs under $15"
            )
            steps += 1
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'steps': steps,
                    'error': f'Merchant query failed: {response.status_code}'
                }
            
            time.sleep(0.5)  # Simulate user browsing
            
            # Step 2: Get payment methods
            response = self._send_message(
                self.credentials_url,
                "List my available payment methods"
            )
            steps += 1
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'steps': steps,
                    'error': f'Payment methods failed: {response.status_code}'
                }
            
            time.sleep(0.5)  # Simulate user selecting
            
            # Step 3: Initiate payment
            response = self._send_message(
                self.payment_processor_url,
                "Process payment for $12.99 using saved card"
            )
            steps += 1
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'steps': steps,
                    'error': f'Payment failed: {response.status_code}'
                }
            
            return {'success': True, 'steps': steps}
            
        except Exception as e:
            return {'success': False, 'steps': steps, 'error': str(e)}
    
    def _infinite_loop_transaction(self, timeout):
        """
        Simulate infinite loop: contradictory product requirements
        """
        start = time.time()
        retry_count = 0
        max_retries = 20
        
        while (time.time() - start) < timeout and retry_count < max_retries:
            try:
                # Query for impossible product (red AND blue)
                response = self._send_message(
                    self.merchant_url,
                    "Find me a coffee mug that is simultaneously bright red and deep blue",
                    timeout=3
                )
                
                retry_count += 1
                time.sleep(0.3)
                
                # Check if agent gives up
                if response.status_code == 404:
                    return {'success': True, 'steps': retry_count}
                
                response_text = response.text.lower()
                if "cannot find" in response_text or "impossible" in response_text:
                    return {'success': True, 'steps': retry_count}
                
            except requests.Timeout:
                retry_count += 1
                continue
            except Exception:
                retry_count += 1
                continue
        
        # Reached max retries or timeout
        return {
            'success': False,
            'steps': retry_count,
            'error': f'Timeout after {retry_count} retries (contradictory mandate)'
        }
    
    def _retry_storm_transaction(self, timeout):
        """
        Simulate payment retry storm
        """
        start = time.time()
        
        # Normal shopping first
        try:
            self._send_message(self.merchant_url, "Show me coffee mugs", timeout=5)
        except:
            pass
        
        time.sleep(0.3)
        
        # Payment retry storm
        retry_count = 0
        max_retries = 15
        
        while (time.time() - start) < timeout and retry_count < max_retries:
            try:
                self._send_message(
                    self.payment_processor_url,
                    f"Process payment for $12.99 (attempt {retry_count})",
                    timeout=2
                )
                retry_count += 1
                time.sleep(0.2)
                
            except:
                retry_count += 1
                time.sleep(0.2)
                continue
        
        return {
            'success': False,
            'steps': retry_count + 1,
            'error': f'Payment retry limit exceeded ({retry_count} retries)'
        }


if __name__ == "__main__":
    executor = AP2TransactionExecutor()
    
    print("Testing normal transaction...")
    result = executor.execute_transaction("normal")
    print(f"Result: {result}\n")
