"""Traffic generator for the Python sample app.

This script continuously sends requests to various endpoints to generate
telemetry data that can be observed in CloudWatch when instrumented with ADOT.
"""
import requests
import time
import random
import sys
from datetime import datetime


class TrafficGenerator:
    def __init__(self, base_url='http://localhost:8080'):
        self.base_url = base_url
        self.endpoints = [
            '/api/users',
            '/api/users/random',
            '/api/products',
            '/api/products/random',
            '/api/error',
            '/api/error/random',
            '/api/slow',
            '/api/slow/random',
            '/health',
        ]
        self.request_count = 0
        self.error_count = 0
        self.success_count = 0

    def make_request(self, endpoint):
        """Make a request to the specified endpoint."""
        url = f'{self.base_url}{endpoint}'
        try:
            start_time = time.time()
            response = requests.get(url, timeout=15)
            duration = time.time() - start_time
            
            self.request_count += 1
            if response.status_code >= 400:
                self.error_count += 1
                status = '❌'
            else:
                self.success_count += 1
                status = '✓'
            
            print(f'[{datetime.now().strftime("%H:%M:%S")}] {status} {endpoint} - '
                  f'Status: {response.status_code}, Duration: {duration:.2f}s')
            
        except requests.exceptions.Timeout:
            self.request_count += 1
            self.error_count += 1
            print(f'[{datetime.now().strftime("%H:%M:%S")}] ⏱ {endpoint} - Timeout')
        except requests.exceptions.RequestException as e:
            self.request_count += 1
            self.error_count += 1
            print(f'[{datetime.now().strftime("%H:%M:%S")}] ❌ {endpoint} - Error: {e}')

    def generate_traffic(self, duration_seconds=None, requests_per_second=1):
        """Generate traffic to the application.
        
        Args:
            duration_seconds: How long to run (None for infinite)
            requests_per_second: Target requests per second
        """
        print(f'Starting traffic generation to {self.base_url}')
        print(f'Target rate: {requests_per_second} requests/second')
        print('-' * 80)
        
        start_time = time.time()
        
        try:
            while True:
                # Check if duration limit reached
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    break
                
                # Select random endpoint
                endpoint = random.choice(self.endpoints)
                self.make_request(endpoint)
                
                # Print stats every 20 requests
                if self.request_count % 20 == 0:
                    print('-' * 80)
                    print(f'Stats: {self.request_count} total, {self.success_count} success, '
                          f'{self.error_count} errors')
                    print('-' * 80)
                
                # Sleep to maintain target rate
                time.sleep(1.0 / requests_per_second)
                
        except KeyboardInterrupt:
            print('\n' + '=' * 80)
            print('Traffic generation stopped by user')
        
        # Final stats
        elapsed = time.time() - start_time
        print('=' * 80)
        print(f'Final Stats:')
        print(f'  Total Requests: {self.request_count}')
        print(f'  Successful: {self.success_count}')
        print(f'  Errors: {self.error_count}')
        print(f'  Duration: {elapsed:.1f}s')
        print(f'  Average Rate: {self.request_count/elapsed:.2f} req/s')
        print('=' * 80)


if __name__ == '__main__':
    # Parse command line arguments
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8080'
    
    generator = TrafficGenerator(base_url)
    
    # Generate traffic continuously at 2 requests per second
    generator.generate_traffic(requests_per_second=2)
