from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route("/file", methods=['GET'])
def getHDFS_file():
    # Extract the file_name from query parameters
    file_name = request.args.get('file_name')
    
    if not file_name:
        return "File name is required", 400

    # HDFS Namenode URL and the file path in HDFS
    hdfs_namenode = "http://namenode:50070"
    hdfs_file_path = f"/webhdfs/v1/{file_name}?op=OPEN"

    # Make a request to HDFS Namenode
    try:
        response = requests.get(hdfs_namenode + hdfs_file_path, stream=True)

        # Check if the request was successful
        if response.status_code != 200:
            return f"Error fetching file from HDFS: {response.content}", response.status_code

        # Stream the file content back to the client
        return Response(response.iter_content(chunk_size=1024),
                        content_type=response.headers['Content-Type'])

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8060)
