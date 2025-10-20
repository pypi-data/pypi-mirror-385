"""Account management example."""

import os

from legnext import Client

client = Client(api_key=os.environ.get("LEGNEXT_API_KEY"))

# Get account information
print("Account Information:")
print("-" * 50)
info = client.account.get_info()

print(f"Account ID: {info.account_id}")
print(f"Email: {info.email}")
print(f"Plan: {info.plan}")
print(f"Status: {info.status}")
print(f"\nBalance: {info.balance}")
print(f"Used: {info.used}")

if info.quota:
    print(f"\nQuota:")
    print(f"  Monthly limit: {info.quota.monthly_limit}")
    print(f"  Remaining: {info.quota.remaining}")
    print(f"  Resets at: {info.quota.reset_at}")

print(f"\nAccount created: {info.created_at}")
print(f"Last updated: {info.updated_at}")

# Get active tasks
print("\n\nActive Tasks:")
print("-" * 50)
active = client.account.get_active_tasks()

print(f"Total active: {active.total_active}/{active.concurrent_limit}")
print(f"Updated at: {active.updated_at}")

if active.tasks:
    print("\nTasks:")
    for task in active.tasks:
        print(f"\n  Job ID: {task.job_id}")
        print(f"  Type: {task.task_type}")
        print(f"  Status: {task.status}")
        print(f"  Progress: {task.progress}%")
        print(f"  Created: {task.created_at}")
        if task.estimated_time:
            print(f"  Estimated time remaining: {task.estimated_time}s")
else:
    print("\nNo active tasks")
