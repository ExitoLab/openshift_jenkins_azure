import subprocess
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/run-maven', methods=['GET'])
def run_maven():
    try:
        # Run your docker image with mvn install, mount current directory if needed
        cmd = [
            "docker", "run", "--rm",
            "talk2toks/testng-automation:v1.1.3",
            "mvn", "install"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return jsonify({
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
