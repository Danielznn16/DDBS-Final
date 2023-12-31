import subprocess
from tqdm import tqdm

print("Distributing Files By Hash")
for i in tqdm(range(10000)):
	subprocess.run(['cp', '-r', f'db-generation/articles/article{i}', f"dfs_{i%2+1}_data/"])