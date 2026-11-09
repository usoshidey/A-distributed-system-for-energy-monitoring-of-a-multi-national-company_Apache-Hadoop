#!/usr/bin/env python3
"""
Hadoop Streaming Reducer: reducer.py
Aggregates country consumption metrics from sorted key-value stream.
Computes Total kWh, Average kWh, and Count for each multinational operating region.
"""

import sys

def main():
    current_country = None
    current_total = 0.0
    current_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 2:
            continue

        country, consumption_str = parts[0].strip(), parts[1].strip()
        try:
            consumption = float(consumption_str)
        except ValueError:
            continue

        if current_country == country:
            current_total += consumption
            current_count += 1
        else:
            if current_country:
                avg = current_total / current_count if current_count > 0 else 0.0
                print(f"{current_country}\tTotal: {current_total:.2f} kWh\tAvg: {avg:.2f} kWh\tReadings: {current_count}")

            current_country = country
            current_total = consumption
            current_count = 1

    # Emit last group
    if current_country:
        avg = current_total / current_count if current_count > 0 else 0.0
        print(f"{current_country}\tTotal: {current_total:.2f} kWh\tAvg: {avg:.2f} kWh\tReadings: {current_count}")

if __name__ == "__main__":
    main()

