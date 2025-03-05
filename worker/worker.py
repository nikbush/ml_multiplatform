import redis
import time

# Connect to Redis
r = redis.Redis(host='redis', port=6379, decode_responses=True)

print("Initializing....")
while True:
    # Block until a task is available (with a timeout of 5 seconds)
    task = r.brpop('default', timeout=5)
    if task:
        _, task_id = task  # task is a tuple (list_name, task_id)
        task_key = f"task:{task_id}"
        task_data = r.hgetall(task_key)
        if task_data and task_data.get("status") == "Queued":
            r.hset(task_key, "status", "In Progress")
            sleep_time = int(task_data.get("sleep_time", 60))
            print(f"Processing task {task_id}: sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            r.hset(task_key, "status", "Completed")
            print(f"Task {task_id} completed.")
        else:
            print(f"Task {task_id} not found or already processed.")
    else:
        # No tasks available, sleep briefly before checking again
        print('Sleep...')
        time.sleep(1)
