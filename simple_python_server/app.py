from flask import Flask, jsonify
import signal
import threading
import time
import os

app = Flask(__name__)

shutdown_flag = threading.Event()


@app.route('/')
def home():
    return "Hi there!"


@app.route('/ready')
def ready():
    if not shutdown_flag.is_set():
        return jsonify({"status": 'Ready'}), 200
    else:
        return jsonify({"status": 'NotReady'}), 503


def shutdown_server():
    shutdown_flag.set()

    print('Handling the last server requests...')
    time.sleep(30)
    print('Serve now should not receive any new incoming requests')

    print('Disconnecting from database..')
    time.sleep(3)
    print('Performing other cleanup tasks...')
    time.sleep(7)
    os._exit(0)


def handle_sigterm(signum, frame):
    print(f"SIGTERM received. {signum} {frame}. Shutting down in 30 seconds...")
    threading.Thread(target=shutdown_server).start()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_sigterm)
    print(f'Server PID={os.getpid()}')

    app.run(host='0.0.0.0', port=8080)
