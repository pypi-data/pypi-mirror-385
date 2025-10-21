# Snowmover

Snowflake Data Loader is a small, pragmatic Python library that streamlines common Snowflake workflows. It lets you ingest external text files using PUT + COPY INTO for fast bulk loads or perform row-by-row inserts when you need granular control. You can export query results to local files in multiple formats (plain text, CSV, or Excel), and even move data between Snowflake accounts/warehouses using stage-based PUT + COPY INTO. The package includes straightforward connection utilities (key-pair or password) so you can go from connect → load → extract in just a few lines of code.
