import tkinter as tk
import time

class DataRateMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Rate Monitor")

        self.outgoing_label = tk.Label(root, text="Outgoing KB/s: 0.00")
        self.outgoing_label.pack()
        
        self.incoming_label = tk.Label(root, text="Incoming KB/s: 0.00")
        self.incoming_label.pack()

        self.update_data_rates()

    def update_data_rates(self):
        start_time = time.time()
        bytes_sent = 0
        bytes_received = 0

        while True:
            # Simulated data transfer, replace with actual data sent/received
            bytes_sent += 1024  # Simulated data sent in bytes
            bytes_received += 2048  # Simulated data received in bytes

            elapsed_time = time.time() - start_time

            if elapsed_time > 0:  # Avoid division by zero
                outgoing_kbps = bytes_sent / elapsed_time
                incoming_kbps = bytes_received / elapsed_time

                self.outgoing_label.config(text="Outgoing KB/s: {:.2f}".format(outgoing_kbps))
                self.incoming_label.config(text="Incoming KB/s: {:.2f}".format(incoming_kbps))

            self.root.update()  # Update the Tkinter GUI

            time.sleep(1)  # Update rates every 1 second

if __name__ == "__main__":
    root = tk.Tk()
    app = DataRateMonitor(root)
    root.mainloop()
