CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    securities TEXT ARRAY
);

CREATE TABLE IF NOT EXISTS securities (
    secid TEXT PRIMARY KEY,
    isin TEXT,
    shortname TEXT,
    name TEXT,
    type TEXT
);