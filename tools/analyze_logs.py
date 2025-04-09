#!/usr/bin/env python3
import json
import sys
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

def read_json_logs(log_file):
    """Đọc file log định dạng JSON và chuyển thành DataFrame"""
    records = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                log_entry = json.loads(line.strip())
                records.append(log_entry)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse line: {line[:50]}...")
    
    return pd.DataFrame(records)

def analyze_api_logs(log_file):
    """Phân tích API logs và hiển thị thống kê"""
    df = read_json_logs(log_file)
    
    # Thống kê cơ bản
    print(f"Total API calls: {len(df)}")
    print(f"Average response time: {df['data'].apply(lambda x: x.get('duration_ms', 0)).mean():.2f} ms")
    
    # Thống kê theo status code
    status_counts = df['data'].apply(lambda x: x.get('status_code')).value_counts()
    print("\nStatus Code Distribution:")
    print(status_counts)
    
    # Biểu đồ thời gian phản hồi
    plt.figure(figsize=(10, 6))
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df['data'].apply(lambda x: x.get('duration_ms', 0)).resample('1H').mean().plot()
    plt.title('Average API Response Time by Hour')
    plt.ylabel('Response Time (ms)')
    plt.savefig('api_response_time.png')
    print("\nSaved response time chart to api_response_time.png")

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_logs.py <log_file>")
        sys.exit(1)
    
    log_file = sys.argv[1]
    if not os.path.exists(log_file):
        print(f"Error: Log file {log_file} not found")
        sys.exit(1)
    
    if 'api' in log_file:
        analyze_api_logs(log_file)
    else:
        print("Generic log analysis not implemented yet")

if __name__ == "__main__":
    main()