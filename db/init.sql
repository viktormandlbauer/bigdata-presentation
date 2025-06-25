CREATE TABLE IF NOT EXISTS willhaben_runs (
	scrape_run_id serial primary key,
	navigation_url TEXT NOT NULL,
	description TEXT DEFAULT NULL
);
            
CREATE TABLE IF NOT EXISTS willhaben_items (
    willhaben_code TEXT NOT NULL,
    breadcrumbs TEXT DEFAULT NULL,
    scraped_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    url TEXT NOT NULL,
    title TEXT DEFAULT NULL,
    price NUMERIC DEFAULT NULL,
    price_assumption NUMERIC DEFAULT NULL,
    description TEXT DEFAULT NULL,
    location TEXT DEFAULT NULL,
    contact_address TEXT DEFAULT NULL,
    coordinates TEXT DEFAULT NULL,
    data JSONB DEFAULT NULL,
    PRIMARY KEY(willhaben_code),
    scrape_run_id integer REFERENCES willhaben_runs (scrape_run_id)
);