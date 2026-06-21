import os
import sys

# Force DATABASE_URL to a SQLite URL during schema generation to avoid
# requiring the psycopg2 driver to be installed locally to load settings.
os.environ["DATABASE_URL"] = "sqlite:///./go2car.db"

from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.dialects import postgresql
from app.db.database import Base
# Import all models to register them on Base.metadata
from app.models import (
    User, Vehicle, ParkingFloor, ParkingSection,
    ParkingSlot, Camera, ParkingRecord, DetectionLog,
    BlacklistedToken, Reservation
)

from sqlalchemy import Enum

def main():
    dialect = postgresql.dialect()
    sql_statements = []
    
    # Collect all Enum types from columns to define them in PostgreSQL first
    enums_to_create = {}
    for table in Base.metadata.sorted_tables:
        for column in table.columns:
            if isinstance(column.type, Enum) and column.type.name not in enums_to_create:
                enums_to_create[column.type.name] = column.type.enums
                
    # Generate DDL for custom enum types
    for name, values in enums_to_create.items():
        vals_str = ", ".join(f"'{v}'" for v in values)
        sql_statements.append(f"CREATE TYPE {name} AS ENUM ({vals_str});\n")
        
    # Sort tables by dependencies so that parent tables are created before children (FK constraints)
    for table in Base.metadata.sorted_tables:
        # Generate CREATE TABLE statement
        create_table_ddl = str(CreateTable(table).compile(dialect=dialect)).strip()
        sql_statements.append(create_table_ddl + ";\n")
        
        # Generate CREATE INDEX statements (indexes defined on columns or table)
        for index in table.indexes:
            create_index_ddl = str(CreateIndex(index).compile(dialect=dialect)).strip()
            sql_statements.append(create_index_ddl + ";\n")
            
    # Write to postgresql_schema.sql
    output_file = "postgresql_schema.sql"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("-- ==========================================\n")
        f.write("-- PostgreSQL DDL Schema for Go2Car Backend\n")
        f.write("-- Generated from SQLAlchemy ORM Models\n")
        f.write("-- ==========================================\n\n")
        f.write("\n".join(sql_statements))
        
    print(f"PostgreSQL SQL schema successfully written to {output_file}")

if __name__ == "__main__":
    main()
