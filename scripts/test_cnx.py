import sys
try:
    from zk import ZK
except ImportError:
    print("❌ pyzk not installed. Run: pip install pyzk")
    sys.exit(1)

IP = '192.168.1.201'
PORT = 4370

print(f"🔄 Attempting to connect to {IP}:{PORT}...")

# TCP Test
print("\n[TCP] Testing...")
try:
    zk = ZK(IP, port=PORT, timeout=5, force_udp=False, ommit_ping=True)
    conn = zk.connect()
    print("✅ TCP Connection Successful!")
    print(f"   Firmware: {conn.get_firmware_version()}")
    conn.disconnect()
except Exception as e:
    print(f"❌ TCP Failed: {e}")

# UDP Test
print("\n[UDP] Testing...")
try:
    zk = ZK(IP, port=PORT, timeout=5, force_udp=True, ommit_ping=True)
    conn = zk.connect()
    print("✅ UDP Connection Successful!")
    print(f"   Firmware: {conn.get_firmware_version()}")
    conn.disconnect()
except Exception as e:
    print(f"❌ UDP Failed: {e}")
