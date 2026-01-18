import time
import random
from datetime import datetime
import streamlit as st

class DialerSimulator:
    """Simulates auto-dialer functionality"""
    
    def __init__(self):
        self.current_call = None
        self.call_history = []
        self.is_dialing = False
        self.redial_count = 0
        self.max_redials = 2  # Default: triple dial (1 initial + 2 redials)
    
    def start_dialing(self, contact, max_redials=2):
        """Start dialing a contact"""
        self.max_redials = max_redials
        self.redial_count = 0
        self.is_dialing = True
        self.current_call = {
            'contact': contact,
            'start_time': datetime.now(),
            'status': 'dialing',
            'attempts': [],
            'answered': False
        }
        self._make_dial_attempt()
    
    def _make_dial_attempt(self):
        """Simulate a dial attempt"""
        if not self.current_call:
            return
        
        attempt = {
            'time': datetime.now(),
            'number': self.current_call['contact']['phone'],
            'result': None
        }
        
        # Simulate call outcome (random for demo)
        outcomes = ['answered', 'no_answer', 'busy', 'failed']
        weights = [0.3, 0.4, 0.2, 0.1]  # 30% answer rate for demo
        
        outcome = random.choices(outcomes, weights=weights)[0]
        attempt['result'] = outcome
        
        self.current_call['attempts'].append(attempt)
        
        if outcome == 'answered':
            self.current_call['status'] = 'answered'
            self.current_call['answered'] = True
            self.is_dialing = False
            self._log_call()
        elif self.redial_count < self.max_redials:
            self.current_call['status'] = f'redialing ({self.redial_count + 1}/{self.max_redials})'
            self.redial_count += 1
        else:
            self.current_call['status'] = 'failed'
            self.is_dialing = False
            self._log_call()
    
    def _log_call(self):
        """Log completed call to history"""
        if self.current_call:
            call_record = self.current_call.copy()
            call_record['end_time'] = datetime.now()
            call_record['duration'] = (call_record['end_time'] - call_record['start_time']).total_seconds()
            self.call_history.append(call_record)
    
    def get_call_stats(self):
        """Get call statistics"""
        total_calls = len(self.call_history)
        answered_calls = len([c for c in self.call_history if c['answered']])
        success_rate = (answered_calls / total_calls * 100) if total_calls > 0 else 0
        
        return {
            'total_calls': total_calls,
            'answered_calls': answered_calls,
            'success_rate': success_rate,
            'avg_duration': sum(c['duration'] for c in self.call_history) / total_calls if total_calls > 0 else 0
        }
    
    def reset(self):
        """Reset dialer state"""
        self.current_call = None
        self.is_dialing = False
        self.redial_count = 0 