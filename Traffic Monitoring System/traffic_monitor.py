import threading
import time
from tkinter import *
from tkinter import ttk
from scapy.all import sniff, IP, TCP, UDP
from scapy.packet import Raw

packet_count = 0
sniffing = False

def packet_callback(packet):
    global packet_count
    if IP in packet:
        packet_count += 1
        timestamp = time.strftime('%H:%M:%S')
        src = packet[IP].src
        dst = packet[IP].dst
        proto = "TCP" if TCP in packet else "UDP" if UDP in packet else "OTHER"
        sport = packet.sport if (TCP in packet or UDP in packet) else ""
        dport = packet.dport if (TCP in packet or UDP in packet) else ""
        data = ""

        if Raw in packet:
            try:
                data = bytes(packet[Raw].load).decode('utf-8', errors='ignore')[:30] + "..."
            except:
                data = "Unable to decode"

        tree.insert('', 'end', values=(packet_count, timestamp, src, dst, proto, sport, dport, data))
        tree.yview_moveto(1.0)

def stop_sniff_filter(packet):
    return not sniffing

def monitor_traffic(iface, ip, port=None):
    global sniffing
    filter_expression = f"host {ip}"
    if port:
        filter_expression += f" and port {port}"
    try:
        sniff(iface=iface, filter=filter_expression, prn=packet_callback, store=0, stop_filter=stop_sniff_filter)
    except Exception as e:
        print(f"\nError: {e}")

def start_sniffing():
    global sniffing
    sniffing = True
    ip = ip_entry.get()
    port = port_entry.get()
    iface = iface_entry.get()

    if not ip or not iface:
        print("Interface and IP are required.")
        return

    port_val = int(port) if port else None
    thread = threading.Thread(target=monitor_traffic, args=(iface, ip, port_val), daemon=True)
    thread.start()

def stop_sniffing():
    global sniffing
    sniffing = False

# GUI Setup
window = Tk()
window.title("Traffic Monitoring System")
window.geometry("1400x600")

frame_top = Frame(window)
frame_top.pack(pady=10)

Label(frame_top, text="Interface:").grid(row=0, column=0)
iface_entry = Entry(frame_top)
iface_entry.insert(0, "Wi-Fi")
iface_entry.grid(row=0, column=1)

Label(frame_top, text="Host IP:").grid(row=0, column=2)
ip_entry = Entry(frame_top)
ip_entry.grid(row=0, column=3)

Label(frame_top, text="Port (optional):").grid(row=0, column=4)
port_entry = Entry(frame_top)
port_entry.grid(row=0, column=5)

Button(frame_top, text="Start Sniffing", command=start_sniffing).grid(row=0, column=6, padx=5)
Button(frame_top, text="Stop Sniffing", command=stop_sniffing).grid(row=0, column=7, padx=5)

# Table setup
columns = ("No.", "Time", "Source IP", "Destination IP", "Protocol", "Src Port", "Dst Port", "Data")
tree = ttk.Treeview(window, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120 if col != "Data" else 300)
tree.pack(fill=BOTH, expand=True)

# Scrollbar
scroll = Scrollbar(window, orient=VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scroll.set)
scroll.pack(side=RIGHT, fill=Y)

window.mainloop()