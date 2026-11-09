"""
Database initialization and data loading script.
Creates tables, seeds master reference data (Users, Company, Countries, Branches, Meters, Tariffs),
and ingests generated energy readings with anomaly detection.
"""

import os
import sys
import csv
from datetime import datetime

# Add project root to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import engine, SessionLocal, Base
from backend.models import (
    User, Company, Country, Branch, EnergyMeter,
    EnergyReading, ElectricityTariff, EnergyAlert, HadoopJobLog
)


def init_database(load_readings=True, max_readings=12000):
    print("Dropping existing tables and creating fresh schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Company
        company = db.query(Company).filter_by(company_code="COMP-001").first()
        if not company:
            company = Company(
                company_code="COMP-001",
                name="Apex Global Industries",
                industry="Global Conglomerate & Advanced Manufacturing"
            )
            db.add(company)
            db.flush()
            print("Seeded Company: Apex Global Industries")

        # 2. Seed Users
        users_data = [
            ("admin", "admin@apexglobal.com", "Admin@123", "Chief Technical Officer", "admin", None),
            ("manager_in", "manager.in@apexglobal.com", "Manager@123", "Rohan Mehta", "country_manager", "India"),
            ("manager_us", "manager.us@apexglobal.com", "Manager@123", "Sarah Jenkins", "country_manager", "USA"),
            ("manager_de", "manager.de@apexglobal.com", "Manager@123", "Hans Mueller", "country_manager", "Germany"),
            ("manager_jp", "manager.jp@apexglobal.com", "Manager@123", "Kenji Sato", "country_manager", "Japan"),
        ]

        for username, email, pwd, fname, role, country in users_data:
            existing_user = db.query(User).filter_by(username=username).first()
            if not existing_user:
                u = User(
                    username=username,
                    email=email,
                    full_name=fname,
                    role=role,
                    assigned_country=country
                )
                u.set_password(pwd)
                db.add(u)
        db.flush()
        print("Seeded default users (admin & country managers)")

        # 3. Seed Countries & Tariffs
        # Tariffs as specified: India: 8 INR, USA: 0.15 USD, Germany: 0.30 EUR, Japan: 30 JPY
        countries_data = [
            ("IND", "India", "INR", "₹", 8.0, 0.012),
            ("USA", "USA", "USD", "$", 0.15, 1.0),
            ("DEU", "Germany", "EUR", "€", 0.30, 1.08),
            ("JPN", "Japan", "JPY", "¥", 30.0, 0.0067)
        ]

        country_map = {}
        for code, name, curr_code, curr_sym, tariff_rate, usd_rate in countries_data:
            c = db.query(Country).filter_by(code=code).first()
            if not c:
                c = Country(
                    code=code,
                    name=name,
                    currency_code=curr_code,
                    currency_symbol=curr_sym,
                    usd_exchange_rate=usd_rate
                )
                db.add(c)
                db.flush()

                # Add active tariff
                t = ElectricityTariff(
                    country_id=c.id,
                    tariff_rate=tariff_rate,
                    currency_code=curr_code,
                    currency_symbol=curr_sym,
                    is_active=True
                )
                db.add(t)
            country_map[name] = c
        db.flush()
        print("Seeded Countries & Tariffs")

        # 4. Seed Branches
        branches_data = [
            # India
            ("Kolkata Office", "India", "office", "Kolkata", "Park Street IT Park, Kolkata"),
            ("Mumbai Factory", "India", "factory", "Mumbai", "MIDC Industrial Estate, Andheri East, Mumbai"),
            ("Delhi Office", "India", "office", "Delhi", "Connaught Place Financial Tower, New Delhi"),
            # USA
            ("New York Office", "USA", "office", "New York", "Midtown Manhattan Tech Hub, NY"),
            ("California Factory", "USA", "factory", "Fremont", "Silicon Valley Advanced Mfg Park, CA"),
            # Germany
            ("Berlin Office", "Germany", "office", "Berlin", "Potsdamer Platz Innovationszentrum, Berlin"),
            ("Munich Factory", "Germany", "factory", "Munich", "Bavaria Automotive & Robotics Plant, Munich"),
            # Japan
            ("Tokyo Office", "Japan", "office", "Tokyo", "Marunouchi Business Center, Chiyoda-ku, Tokyo"),
            ("Osaka Factory", "Japan", "factory", "Osaka", "Yodogawa Precision Electronics Complex, Osaka"),
        ]

        branch_map = {}
        for bname, cname, btype, city, addr in branches_data:
            b = db.query(Branch).filter_by(name=bname).first()
            if not b:
                b = Branch(
                    company_id=company.id,
                    country_id=country_map[cname].id,
                    name=bname,
                    branch_type=btype,
                    city=city,
                    address=addr
                )
                db.add(b)
                db.flush()
            branch_map[bname] = b
        print("Seeded Branches")

        # 5. Seed Meters
        meters_config = {
            "Kolkata Office": ["MTR-IND-KOL-01", "MTR-IND-KOL-02"],
            "Mumbai Factory": ["MTR-IND-BOM-01", "MTR-IND-BOM-02", "MTR-IND-BOM-03"],
            "Delhi Office": ["MTR-IND-DEL-01", "MTR-IND-DEL-02"],
            "New York Office": ["MTR-USA-NYC-01", "MTR-USA-NYC-02", "MTR-USA-NYC-03"],
            "California Factory": ["MTR-USA-CAL-01", "MTR-USA-CAL-02", "MTR-USA-CAL-03", "MTR-USA-CAL-04"],
            "Berlin Office": ["MTR-DEU-BER-01", "MTR-DEU-BER-02"],
            "Munich Factory": ["MTR-DEU-MUC-01", "MTR-DEU-MUC-02", "MTR-DEU-MUC-03"],
            "Tokyo Office": ["MTR-JPN-TYO-01", "MTR-JPN-TYO-02"],
            "Osaka Factory": ["MTR-JPN-OSA-01", "MTR-JPN-OSA-02", "MTR-JPN-OSA-03"],
        }

        meter_map = {}
        for bname, mlist in meters_config.items():
            b = branch_map[bname]
            for mcode in mlist:
                m = db.query(EnergyMeter).filter_by(meter_code=mcode).first()
                if not m:
                    m = EnergyMeter(
                        meter_code=mcode,
                        branch_id=b.id,
                        meter_type="smart_digital_iot",
                        is_active=True
                    )
                    db.add(m)
                    db.flush()
                meter_map[mcode] = m
        print("Seeded Energy Meters")

        db.commit()

        # 6. Ingest CSV Data if requested
        csv_path = os.path.join(BASE_DIR, "data", "energy_data.csv")
        if load_readings and os.path.exists(csv_path):
            print(f"Loading energy readings from {csv_path}...")
            count = 0
            batch = []

            # First pass: calculate branch averages from CSV for fast anomaly determination
            branch_totals = {}
            branch_counts = {}

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    b_name = row["branch_name"]
                    kwh = float(row["energy_kwh"])
                    branch_totals[b_name] = branch_totals.get(b_name, 0.0) + kwh
                    branch_counts[b_name] = branch_counts.get(b_name, 0) + 1

            branch_avgs = {b: branch_totals[b] / branch_counts[b] for b in branch_totals}

            alerts_to_add = []

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if count >= max_readings:
                        break

                    b_name = row["branch_name"]
                    m_code = row["meter_id"]
                    if b_name not in branch_map or m_code not in meter_map:
                        continue

                    branch = branch_map[b_name]
                    meter = meter_map[m_code]
                    kwh = float(row["energy_kwh"])
                    ts = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")

                    reading = EnergyReading(
                        reading_id=row["reading_id"],
                        meter_id=meter.id,
                        branch_id=branch.id,
                        timestamp=ts,
                        energy_kwh=kwh,
                        voltage=float(row["voltage"]),
                        current=float(row["current"]),
                        power_factor=float(row["power_factor"])
                    )
                    batch.append(reading)

                    # Anomaly rule: if current consumption > 1.5 * average consumption of the same branch
                    avg_kwh = branch_avgs.get(b_name, 200.0)
                    if kwh > 1.5 * avg_kwh:
                        ratio = kwh / avg_kwh
                        severity = "Critical" if ratio >= 2.0 else ("High" if ratio >= 1.7 else "Warning")
                        alert = EnergyAlert(
                            reading_id=row["reading_id"],
                            branch_id=branch.id,
                            country_name=branch.country_rel.name,
                            current_kwh=kwh,
                            average_kwh=avg_kwh,
                            ratio=ratio,
                            severity=severity,
                            status="Pending",
                            timestamp=ts
                        )
                        alerts_to_add.append(alert)

                    count += 1
                    if len(batch) >= 1000:
                        db.bulk_save_objects(batch)
                        db.commit()
                        batch = []

            if batch:
                db.bulk_save_objects(batch)
                db.commit()

            if alerts_to_add:
                # Add alerts (sample top 100 for fast UI response, keep recent)
                alerts_to_add.sort(key=lambda a: a.timestamp, reverse=True)
                sample_alerts = alerts_to_add[:120]
                for alt in sample_alerts:
                    db.add(alt)
                db.commit()

            print(f"Successfully ingested {count} energy readings and generated {len(sample_alerts)} anomaly alerts.")

        # Seed initial Hadoop job log record
        sample_log = HadoopJobLog(
            job_id="job_20261110_0001",
            job_type="MapReduce",
            status="SUCCESS",
            execution_engine="Apache Hadoop YARN / MapReduce",
            input_path="/energy-monitoring/raw-data/energy_data.csv",
            output_path="/energy-monitoring/processed-data/country_summary",
            duration_seconds=14.8,
            records_processed=12000,
            details="Country-wise aggregate MapReduce completed with 4 map tasks and 2 reduce tasks."
        )
        db.add(sample_log)
        db.commit()
        print("Database initialized successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    init_database()

