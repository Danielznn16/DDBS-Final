import subprocess
from tqdm import tqdm

def put_file_to_hadoop(file_index):
    try:
        command = f"docker exec -it namenode bash -c \"hadoop fs -put /buffer/article*{file_index}/* articles/\""
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred with file index {file_index}: {e}")

def main():
    total_files = 10  # Adjust this number if needed
    for file_index in tqdm(range(total_files), desc="Uploading files"):
        put_file_to_hadoop(file_index)

if __name__ == "__main__":
    main()
