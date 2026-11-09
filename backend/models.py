"""
SQLAlchemy ORM models for Energy Monitoring System.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(50), nullable=False, default="country_manager")  # 'admin' or 'country_manager'
    assigned_country = Column(String(80), nullable=True)  # NULL for global admin, e.g. 'India' for country manager
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "assigned_country": self.assigned_country,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    industry = Column(String(100), default="Conglomerate / High-Tech Manufacturing")
    created_at = Column(DateTime, default=datetime.utcnow)

    branches = relationship("Branch", back_populates="company", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "company_code": self.company_code,
            "name": self.name,
            "industry": self.industry
        }


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(80), unique=True, nullable=False, index=True)
    currency_code = Column(String(10), nullable=False)
    currency_symbol = Column(String(10), nullable=False)
    usd_exchange_rate = Column(Float, nullable=False, default=1.0)  # For global consolidated expenditure calculation

    branches = relationship("Branch", back_populates="country_rel", cascade="all, delete-orphan", lazy="joined")
    tariffs = relationship("ElectricityTariff", back_populates="country_rel", cascade="all, delete-orphan", lazy="joined")

    def to_dict(self):
        active_tariff = next((t for t in self.tariffs if t.is_active), None) if self.tariffs else None
        branch_count = len(self.branches) if self.branches else 0
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "currency_code": self.currency_code,
            "currency_symbol": self.currency_symbol,
            "tariff_rate": active_tariff.tariff_rate if active_tariff else 0.0,
            "usd_exchange_rate": self.usd_exchange_rate,
            "branch_count": branch_count
        }


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    name = Column(String(100), unique=True, nullable=False, index=True)
    branch_type = Column(String(50), nullable=False)  # 'office' or 'factory'
    city = Column(String(80), nullable=False)
    address = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="branches")
    country_rel = relationship("Country", back_populates="branches", lazy="joined")
    meters = relationship("EnergyMeter", back_populates="branch", cascade="all, delete-orphan", lazy="joined")
    readings = relationship("EnergyReading", back_populates="branch_rel")
    alerts = relationship("EnergyAlert", back_populates="branch_rel")

    def to_dict(self):
        cname = ""
        ccode = ""
        csym = "$"
        try:
            if self.country_rel:
                cname = self.country_rel.name
                ccode = self.country_rel.code
                csym = self.country_rel.currency_symbol
        except Exception:
            pass

        meter_cnt = 0
        try:
            if self.meters:
                meter_cnt = len(self.meters)
        except Exception:
            pass

        return {
            "id": self.id,
            "name": self.name,
            "country": cname,
            "country_code": ccode,
            "currency_symbol": csym,
            "branch_type": self.branch_type,
            "city": self.city,
            "address": self.address,
            "meter_count": meter_cnt
        }


class EnergyMeter(Base):
    __tablename__ = "energy_meters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meter_code = Column(String(50), unique=True, nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    meter_type = Column(String(50), default="main_meter")
    is_active = Column(Boolean, default=True)
    installed_at = Column(DateTime, default=datetime.utcnow)

    branch = relationship("Branch", back_populates="meters")
    readings = relationship("EnergyReading", back_populates="meter_rel")

    def to_dict(self):
        return {
            "id": self.id,
            "meter_code": self.meter_code,
            "branch_id": self.branch_id,
            "branch_name": self.branch.name if self.branch else "",
            "meter_type": self.meter_type,
            "is_active": self.is_active
        }


class EnergyReading(Base):
    __tablename__ = "energy_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reading_id = Column(String(50), unique=True, nullable=False, index=True)
    meter_id = Column(Integer, ForeignKey("energy_meters.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    energy_kwh = Column(Float, nullable=False)
    voltage = Column(Float, nullable=False)
    current = Column(Float, nullable=False)
    power_factor = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    meter_rel = relationship("EnergyMeter", back_populates="readings")
    branch_rel = relationship("Branch", back_populates="readings")

    __table_args__ = (
        Index("idx_reading_branch_ts", "branch_id", "timestamp"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "reading_id": self.reading_id,
            "meter_code": self.meter_rel.meter_code if self.meter_rel else "",
            "branch_name": self.branch_rel.name if self.branch_rel else "",
            "country": self.branch_rel.country_rel.name if self.branch_rel and self.branch_rel.country_rel else "",
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else "",
            "energy_kwh": round(self.energy_kwh, 2),
            "voltage": round(self.voltage, 2),
            "current": round(self.current, 2),
            "power_factor": round(self.power_factor, 2)
        }


class ElectricityTariff(Base):
    __tablename__ = "electricity_tariffs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    tariff_rate = Column(Float, nullable=False)
    currency_code = Column(String(10), nullable=False)
    currency_symbol = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)
    effective_date = Column(DateTime, default=datetime.utcnow)

    country_rel = relationship("Country", back_populates="tariffs")

    def to_dict(self):
        return {
            "id": self.id,
            "country_id": self.country_id,
            "country_name": self.country_rel.name if self.country_rel else "",
            "tariff_rate": self.tariff_rate,
            "currency_code": self.currency_code,
            "currency_symbol": self.currency_symbol,
            "is_active": self.is_active,
            "effective_date": self.effective_date.strftime("%Y-%m-%d") if self.effective_date else ""
        }


class EnergyAlert(Base):
    __tablename__ = "energy_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reading_id = Column(String(50), nullable=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    country_name = Column(String(80), nullable=False)
    current_kwh = Column(Float, nullable=False)
    average_kwh = Column(Float, nullable=False)
    ratio = Column(Float, nullable=False)  # current / average
    severity = Column(String(20), nullable=False, default="Warning")  # 'Warning', 'High', 'Critical'
    status = Column(String(30), nullable=False, default="Pending")    # 'Pending', 'Acknowledged'
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    acknowledged_by = Column(String(80), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)

    branch_rel = relationship("Branch", back_populates="alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "reading_id": self.reading_id,
            "branch_id": self.branch_id,
            "branch_name": self.branch_rel.name if self.branch_rel else "",
            "country": self.country_name,
            "current_kwh": round(self.current_kwh, 2),
            "average_kwh": round(self.average_kwh, 2),
            "ratio": round(self.ratio, 2),
            "severity": self.severity,
            "status": self.status,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else "",
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.strftime("%Y-%m-%d %H:%M:%S") if self.acknowledged_at else None
        }


class HadoopJobLog(Base):
    __tablename__ = "hadoop_job_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(80), nullable=False, unique=True, index=True)
    job_type = Column(String(50), nullable=False)  # 'MapReduce', 'Hive', 'HDFS_Upload'
    status = Column(String(30), nullable=False)    # 'SUCCESS', 'RUNNING', 'FAILED'
    execution_engine = Column(String(100), nullable=False)
    input_path = Column(String(255), nullable=True)
    output_path = Column(String(255), nullable=True)
    duration_seconds = Column(Float, default=0.0)
    records_processed = Column(Integer, default=0)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "job_type": self.job_type,
            "status": self.status,
            "execution_engine": self.execution_engine,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "duration_seconds": round(self.duration_seconds, 2),
            "records_processed": self.records_processed,
            "details": self.details,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }
