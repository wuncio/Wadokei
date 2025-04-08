from flask import Flask, jsonify, render_template
import time

app = Flask(__name__)

# Time scaling factor (for fast time simulation)
time_scale_factor = (10 * 60) / 30  # 10 minutes pass in 30 seconds


@app.route('/')
def index():
    return render_template('index.html')  # This will load the frontend HTML


@app.route('/time')
def get_time():
    # Get current time in seconds
    current_time = time.time()

    # Scale time (10 minutes = 30 seconds)
    scaled_time = (current_time * time_scale_factor) % 60
    scaled_minutes = (current_time * time_scale_factor // 60) % 60
    scaled_hours = (current_time * time_scale_factor // 3600) % 12

    return jsonify({
        'hours': scaled_hours,
        'minutes': scaled_minutes,
        'seconds': scaled_time
    })


if __name__ == "__main__":
    app.run(debug=True)
