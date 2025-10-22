#!/usr/bin/env python3
"""Test the IPS API client."""

import asyncio
import sys
import os

# Add parent directory to path so we can import ips_api
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ips_api import IPSClient


async def main():
    """Test the IPS client."""

    # Load credentials from .env
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    env = {}

    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key.strip()] = value.strip()

    username = env.get('IPS_EMAIL')
    password = env.get('IPS_PASSWORD')

    if not username or not password:
        print("❌ Set IPS_EMAIL and IPS_PASSWORD in .env file")
        return

    print("=" * 80)
    print("TESTING IPS API CLIENT")
    print("=" * 80)

    async with IPSClient(username, password) as client:
        print("\n1️⃣  Testing login...")
        await client.login()
        print("   ✅ Login successful")

        print("\n2️⃣  Getting controllers list...")
        controllers = await client.get_controllers()
        print(f"   ✅ Found {len(controllers)} controller(s)")

        for controller in controllers:
            print(f"\n   📊 Controller: {controller.name}")
            print(f"      ID: {controller.controller_id}")
            print(f"      Status: {controller.status}")

            if controller.current_reading:
                print(f"      pH: {controller.current_reading.ph}")
                print(f"      ORP: {controller.current_reading.orp} mV")
                print(f"      Temperature: {controller.current_reading.temperature}°F")
                print(f"      PPM: {controller.current_reading.ppm}")

            if controller.last_reading_time:
                print(f"      Last Reading: {controller.last_reading_time}")

            print(f"\n3️⃣  Getting detailed reading for {controller.name}...")
            detail = await client.get_controller_detail(controller.controller_id)
            print(f"   ✅ Retrieved detailed reading")
            print(f"      pH: {detail.ph}")
            print(f"      ORP: {detail.orp} mV")
            print(f"      Temperature: {detail.temperature}")
            print(f"      pH State: {detail.ph_state}")
            print(f"      pH Setpoint: {detail.ph_setpoint}")
            print(f"      Timestamp: {detail.timestamp}")

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
