# -*- coding: utf-8 -*-


import hashlib
import platform
import socket
import subprocess
import uuid


def get_system_uuid():
    """
    Tries to get the hardware/system UUID.
    This is the most reliable identifier.
    """
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            command = "ioreg -d2 -c IOPlatformExpertDevice | awk -F\"'\" '/IOPlatformUUID/ {print $(NF-1)}'"
            process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, text=True)
            uuid_str, _ = process.communicate()
            if process.returncode == 0 and uuid_str.strip():
                return uuid_str.strip()
        elif system == "Linux":
            # Try DMI product_uuid first
            try:
                with open("/sys/class/dmi/id/product_uuid", "r") as f:
                    uuid_str = f.readline().strip()
                    if uuid_str:
                        return uuid_str
            except IOError:
                pass  # File not found, proceed to the next method

            # Fallback to /etc/machine-id on Linux
            try:
                with open("/etc/machine-id", "r") as f:
                    machine_id = f.readline().strip()
                    if machine_id:
                        return machine_id
            except IOError:
                pass # File not found
    except Exception:
        return None
    return None


def get_mac_address():
    """
    Gets the MAC address of the first network interface.
    uuid.getnode() is a reliable cross-platform way to get a MAC address.
    """
    try:
        mac_num = uuid.getnode()
        mac = ':'.join(('%012X' % mac_num)[i:i+2] for i in range(0, 12, 2))
        if mac != "00:00:00:00:00:00":
            return mac
    except Exception:
        return None
    return None


def get_machine_id():
    """
    Generates a stable, unique machine ID.
    It tries methods in order of reliability:
    1. System/Hardware UUID
    2. MAC Address
    3. Hostname (as a last resort)
    The final ID is a SHA256 hash of the collected identifier.
    """
    # 1. Try System UUID (most reliable)
    identifier = get_system_uuid()

    # 2. Fallback to MAC Address
    if not identifier:
        identifier = get_mac_address()

    # 3. Fallback to hostname (least reliable, but better than nothing)
    if not identifier:
        try:
            identifier = socket.gethostname()
        except Exception:
            # If all fails, use a random fallback (not ideal for stability)
            identifier = "could_not_determine_id"

    # Hash the identifier to create a consistent, anonymous ID
    hashed_id = hashlib.sha256(identifier.encode('utf-8')).hexdigest()

    # You can print the source for debugging if you want
    # print(f"Source of ID: {source}")

    return hashed_id


if __name__ == "__main__":
    machine_id = get_machine_id()
    print(machine_id)
