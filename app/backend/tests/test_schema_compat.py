import pathlib
import sys
import unittest

from sqlalchemy import create_engine, text

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.schema_compat import ensure_sqlite_compat_schema


class SchemaCompatTests(unittest.TestCase):
    def test_ensure_sqlite_compat_schema_adds_missing_clinical_profile_column(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        with engine.begin() as conn:
            conn.exec_driver_sql(
                """
                CREATE TABLE user_profiles (
                    user_id TEXT PRIMARY KEY,
                    nickname TEXT,
                    session_count INTEGER DEFAULT 0,
                    risk_level TEXT DEFAULT 'none',
                    alliance JSON,
                    preferences JSON,
                    updated_at TEXT
                )
                """
            )

            ensure_sqlite_compat_schema(conn)

            columns = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info('user_profiles')"))
            }
            self.assertIn("clinical_profile", columns)

            # 再跑一次也不应报错
            ensure_sqlite_compat_schema(conn)


if __name__ == "__main__":
    unittest.main()
