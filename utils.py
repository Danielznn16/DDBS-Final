# utils.py
import json
from threading import Condition
import subprocess

def load_jsonl(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line:
                yield json.loads(stripped_line)

def dump_jsonl(objects,file_name):
	out_file = open(file_name,'w')
	for obj in objects:
		tmp = out_file.write(json.dumps(obj,ensure_ascii=False)+"\n")
		out_file.flush()


class StreamDumpBuffer:
    def __init__(self):
        self.condition = Condition()
        self.values = []
        self.stop_iteration = False

    def __call__(self, value):
        with self.condition:
            if self.stop_iteration:
                return  # Ignore new values if stopping
            self.values.append(value)
            self.condition.notify()

    def done(self):
        with self.condition:
            self.stop_iteration = True
            self.condition.notify_all()  # Wake up all waiting threads

    def __iter__(self):
        while True:
            with self.condition:
                while not self.values and not self.stop_iteration:
                    self.condition.wait()
                
                if self.stop_iteration:
                    break  # Exit the loop if stop flag is set

                value = self.values.pop(0)
                yield value
                
def get_container_names(prefix):
    result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error getting container names")
        return []

    return [name for name in result.stdout.splitlines() if name.startswith(prefix)]
