#!/usr/bin/env python3
"""
Hadoop Streaming Mapper: mapper.py
Reads CSV energy records from standard input.
Extracts country and energy_kwh.
Emits tab-separated Key-Value pair: <Country>\t<Consumption>
"""

import sys

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        # Skip CSV header
        if line.startswith("reading_id") or "energy_kwh" in line:
            continue

        tokens = line.split(",")
        # Format: reading_id,meter_id,company_id,branch_name,country,timestamp,energy_kwh,voltage,current,power_factor
        if len(tokens) >= 7:
            try:
                country = tokens[4].strip()
                consumption = float(tokens[6].strip())
                if country:
                    print(f"{country}\t{consumption:.2f}")
            except ValueError:
                # Discard corrupted records
                continue

if __name__ == "__main__":
    main()

