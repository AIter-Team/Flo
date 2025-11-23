import os

script_dir = os.path.dirname(os.path.abspath(__file__))

MEMORY_DIR = os.path.join(script_dir, "..", "memory")
DATABASE_DIR = os.path.join(script_dir, "..", "database")
DB_PATH = os.path.join(MEMORY_DIR, "semantic", "userdata.db")
LOGGING_DIR = os.path.join(script_dir, "../..", "logs")
