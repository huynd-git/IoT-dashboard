-- Create the 'iot' schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS iot;

-- Create the 'transformed_network_flows' table
CREATE TABLE IF NOT EXISTS iot.transformed_network_flows (
    -- Primary Key
    flow_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,

    -- Network Flow Attributes
    src_ip INET,
    dst_ip INET,
    protocol SMALLINT,  
    totlen_fwd_pkts INTEGER, 
    totlen_bwd_pkts INTEGER,
    flow_duration BIGINT, -- Microseconds
    tot_fwd_pkts INTEGER,
    tot_bwd_pkts INTEGER,

    -- Time-Based Features
    hour SMALLINT,
    day SMALLINT,
    week SMALLINT,

    -- Geolocation Features
    src_latitude NUMERIC(9, 6),
    src_longitude NUMERIC(9, 6),
    src_city VARCHAR(255),
    src_country VARCHAR(255),
    dst_latitude NUMERIC(9, 6),
    dst_longitude NUMERIC(9, 6),
    dst_city VARCHAR(255),
    dst_country VARCHAR(255),

    -- Derived Metrics
    total_data_transferred INTEGER,
    data_transfer_rate NUMERIC(15, 5), 
    packet_rate NUMERIC(15, 5)
);

-- Create indexes on frequently queried columns
CREATE INDEX idx_timestamp ON iot.transformed_network_flows (timestamp);
CREATE INDEX idx_src_ip ON iot.transformed_network_flows (src_ip);
CREATE INDEX idx_dst_ip ON iot.transformed_network_flows (dst_ip);