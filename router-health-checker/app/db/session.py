"""SQLite Database Session and Table Initializer."""
import sqlite3
from contextlib import contextmanager
from typing import Generator
from app.config import settings

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.DATABASE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    """Initialize all SQLite tables safely."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            security_question TEXT DEFAULT 'What is your favorite router brand?',
            security_answer_hash TEXT,
            consent_given INTEGER DEFAULT 0,
            consent_timestamp TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            last_login TEXT,
            failed_attempts INTEGER DEFAULT 0,
            lockout_until TEXT
        );
        """)
        
        # Scan History
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT DEFAULT (datetime('now')),
            gateway_ip TEXT NOT NULL,
            score INTEGER NOT NULL,
            status_verdict TEXT,
            wifi_type TEXT,
            admin_status TEXT,
            open_ports_json TEXT,
            dns_servers_json TEXT,
            fixes_json TEXT,
            details_json TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)
        
        # Stability History
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stability_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT DEFAULT (datetime('now')),
            overall_score INTEGER NOT NULL,
            uptime_pct REAL DEFAULT 99.0,
            avg_ping_ms REAL NOT NULL,
            packet_loss_pct REAL NOT NULL,
            devices_count INTEGER DEFAULT 0,
            devices_json TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)
        
        # Speed History
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS speed_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT DEFAULT (datetime('now')),
            download_mbps REAL NOT NULL,
            upload_mbps REAL NOT NULL,
            ping_ms REAL NOT NULL,
            jitter_ms REAL NOT NULL,
            test_type TEXT DEFAULT 'local',
            verdict_code TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)
        
        # AI Feedback
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            is_helpful INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """)
        
        # Audit Log
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            target_ip TEXT,
            status TEXT NOT NULL,
            message TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """)
        
        # Check if default demo user exists, if not create demo user safely
        cursor.execute("SELECT id FROM users WHERE username = 'demo@family.com'")
        if not cursor.fetchone():
            # Argon2 or simple fallback hash for demo initial seed
            from app.security.auth import get_password_hash
            demo_hash = get_password_hash("demo123456")
            cursor.execute("""
            INSERT INTO users (username, password_hash, consent_given, consent_timestamp)
            VALUES (?, ?, 1, datetime('now'))
            """, ("demo@family.com", demo_hash))
            
            # Seed initial sample scan so demo mode shows immediate beautiful data
            cursor.execute("""
            INSERT INTO scan_history (user_id, gateway_ip, score, status_verdict, wifi_type, admin_status, open_ports_json, dns_servers_json, fixes_json, details_json)
            VALUES (1, '192.168.1.1', 72, 'fair', 'WPA2-Personal', 'default_detected', '["80/HTTP", "23/Telnet"]', '["1.1.1.1", "8.8.8.8"]', 
            '[{"id": "FIX_CHANGE_ADMIN_PASSWORD", "gain": 12, "time": "2m"}, {"id": "FIX_TURN_OFF_WPS", "gain": 10, "time": "3m"}, {"id": "FIX_DISABLE_TELNET", "gain": 6, "time": "1m"}]',
            '{"checks": {"wifi": "pass", "admin": "fail", "ports": "warn", "wps": "fail", "dns": "pass", "fw": "pass"}}')
            """)
