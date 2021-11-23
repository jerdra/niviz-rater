from peewee import SqliteDatabase

# Use in-memory database
# db = SqliteDatabase("file::memory:?cache=shared",
#                     pragmas=[('foreign_keys', 'on')], uri=True)
db = SqliteDatabase("test.db",
                    pragmas=[('foreign_keys', 'on')], uri=True)
