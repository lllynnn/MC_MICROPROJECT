from flask import Flask, jsonify, render_template
import serial
import serial.tools.list_ports
import threading
import time

app = Flask(__name__)

BAUD_RATE = 9600

latest_value = 0
latest_status = "CONNECTING..."


def find_arduino():
    """Find a likely Arduino serial port automatically."""

    ports = list(serial.tools.list_ports.comports())

    for port in ports:
        description = (port.description or "").lower()
        manufacturer = (port.manufacturer or "").lower()

        # Common Arduino / USB-serial identifiers
        keywords = [
            "arduino",
            "ch340",
            "ch341",
            "usb serial",
            "usb-serial",
            "ftdi",
        ]

        if any(keyword in description or keyword in manufacturer
               for keyword in keywords):
            return port.device

    # Fallback: if there is only one serial device, use it
    if len(ports) == 1:
        return ports[0].device

    return None


def read_arduino():
    global latest_value, latest_status

    while True:
        port = find_arduino()

        if port is None:
            latest_status = "ARDUINO DISCONNECTED"
            print("Arduino not found. Waiting...")
            time.sleep(2)
            continue

        try:
            print(f"Connecting to Arduino on {port}...")

            with serial.Serial(port, BAUD_RATE, timeout=1) as ser:
                time.sleep(2)

                print(f"Connected to Arduino on {port}")

                while True:
                    line = ser.readline().decode(
                        "utf-8",
                        errors="ignore"
                    ).strip()

                    if not line:
                        continue

                    print(line)

                    try:
                        # Expected:
                        # VALUE:134,STATUS:GOOD

                        parts = line.split(",")

                        value = int(parts[0].split(":")[1])
                        status = parts[1].split(":")[1]

                        latest_value = value
                        latest_status = status

                    except (ValueError, IndexError):
                        print("Could not parse:", line)

        except serial.SerialException as e:
            latest_status = "ARDUINO DISCONNECTED"
            print(f"Serial connection lost: {e}")
            time.sleep(2)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/data")
def data():
    return jsonify({
        "value": latest_value,
        "status": latest_status
    })


if __name__ == "__main__":

    thread = threading.Thread(
        target=read_arduino,
        daemon=True
    )

    thread.start()

    print("\n===================================")
    print("     AIR QUALITY MONITOR")
    print("===================================")
    print("Open: http://127.0.0.1:5050")
    print("===================================\n")

    app.run(
        host="127.0.0.1",
        port=5050,
        debug=False
    )
