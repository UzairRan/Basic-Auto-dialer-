import time
import random
from datetime import datetime
import streamlit as st

class DialerSimulator:
    """Simulates auto-dialer functionality with Single and Power modes"""
    
    def __init__(self):
        self.current_call = None
        self.active_calls = []  # For power mode: stores multiple simultaneous calls
        self.call_history = []
        self.is_dialing = False
        self.redial_count = 0
        self.max_redials = 2  # Default: triple dial (1 initial + 2 redials)
        self.dialing_mode = "single"  # "single" or "power"
        self.power_batch_size = 10  # Number of simultaneous calls in power mode
    
    def set_dialing_mode(self, mode="single"):
        """Set dialing mode: 'single' or 'power'"""
        self.dialing_mode = mode
        if mode == "power":
            self.active_calls = []  # Reset active calls
    
    def start_dialing(self, contact, max_redials=2, mode="single"):
        """Start dialing a contact - supports both single and power modes"""
        self.dialing_mode = mode
        self.max_redials = max_redials
        
        if mode == "single":
            self._start_single_dialing(contact)
        elif mode == "power":
            self._start_power_dialing(contact)
    
    def _start_single_dialing(self, contact):
        """Start single contact dialing"""
        self.redial_count = 0
        self.is_dialing = True
        self.current_call = {
            'contact': contact,
            'start_time': datetime.now(),
            'status': 'dialing',
            'attempts': [],
            'answered': False,
            'mode': 'single'
        }
        self._make_single_dial_attempt()
    
    def _start_power_dialing(self, contacts):
        """Start power dialing with multiple contacts"""
        if not isinstance(contacts, list):
            contacts = [contacts]
        
        self.is_dialing = True
        
        # Clear previous active calls
        self.active_calls = []
        
        # Create call objects for each contact (max 10)
        for i, contact in enumerate(contacts[:self.power_batch_size]):
            call = {
                'contact': contact,
                'start_time': datetime.now(),
                'status': 'dialing',
                'attempts': [],
                'answered': False,
                'call_id': f"power_{i}",
                'mode': 'power'
            }
            self.active_calls.append(call)
        
        # Start all calls simultaneously
        for call in self.active_calls:
            self._make_power_dial_attempt(call)
    
    def _make_single_dial_attempt(self):
        """Simulate a single dial attempt"""
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
            self._log_call(self.current_call)
        elif self.redial_count < self.max_redials:
            self.current_call['status'] = f'redialing ({self.redial_count + 1}/{self.max_redials})'
            self.redial_count += 1
        else:
            self.current_call['status'] = 'failed'
            self.is_dialing = False
            self._log_call(self.current_call)
    
    def _make_power_dial_attempt(self, call):
        """Simulate a power dial attempt (no redials)"""
        if not call:
            return
        
        attempt = {
            'time': datetime.now(),
            'number': call['contact']['phone'],
            'result': None
        }
        
        # Simulate call outcome (random for demo)
        outcomes = ['answered', 'no_answer', 'busy', 'failed']
        weights = [0.3, 0.4, 0.2, 0.1]  # 30% answer rate for demo
        
        outcome = random.choices(outcomes, weights=weights)[0]
        attempt['result'] = outcome
        call['attempts'].append(attempt)
        
        # Update call status
        if outcome == 'answered':
            call['status'] = 'answered'
            call['answered'] = True
        else:
            call['status'] = 'failed'
        
        # Log immediately for power mode (no redials)
        call['end_time'] = datetime.now()
        call['duration'] = (call['end_time'] - call['start_time']).total_seconds()
        self.call_history.append(call.copy())
    
    def update_power_calls_status(self):
        """Update status of all active power calls"""
        if self.dialing_mode != "power":
            return
        
        # Check if all power calls are completed
        active_calls = [call for call in self.active_calls if call['status'] == 'dialing']
        
        if len(active_calls) == 0:
            self.is_dialing = False
            # Clear active calls after a delay
            time.sleep(1)
            self.active_calls = []
    
    def get_active_power_calls(self):
        """Get currently active power calls"""
        return [call for call in self.active_calls if call['status'] == 'dialing']
    
    def get_completed_power_calls(self):
        """Get completed power calls from current batch"""
        return [call for call in self.active_calls if call['status'] in ['answered', 'failed']]
    
    def _log_call(self, call):
        """Log completed call to history"""
        call_record = call.copy()
        call_record['end_time'] = datetime.now()
        if 'duration' not in call_record:
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
            'avg_duration': sum(c.get('duration', 0) for c in self.call_history) / total_calls if total_calls > 0 else 0
        }
    
    def reset(self):
        """Reset dialer state"""
        self.current_call = None
        self.active_calls = []
        self.is_dialing = False
        self.redial_count = 0 