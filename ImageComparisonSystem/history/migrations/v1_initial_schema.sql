-- Historical Metrics Tracking Database Schema
-- Version: 1
-- Created: 2025-12-03

-- Core comparison runs table
CREATE TABLE IF NOT EXISTS runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_number TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    base_dir TEXT NOT NULL,
    new_dir TEXT NOT NULL,
    known_good_dir TEXT NOT NULL,
    config_snapshot TEXT,  -- JSON serialized Config object
    total_images INTEGER,
    avg_difference REAL,
    max_difference REAL,
    notes TEXT
);

-- Individual image comparison results
CREATE TABLE IF NOT EXISTS results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    subdirectory TEXT,
    new_image_path TEXT NOT NULL,
    known_good_path TEXT NOT NULL,

    -- Pixel difference metrics
    pixel_difference REAL,
    changed_pixels INTEGER,
    mean_absolute_error REAL,
    max_pixel_difference REAL,

    -- SSIM metrics
    ssim_score REAL,
    ssim_percentage REAL,

    -- Color difference metrics
    mean_color_distance REAL,
    max_color_distance REAL,
    significant_color_changes INTEGER,

    -- Histogram metrics
    red_histogram_correlation REAL,
    green_histogram_correlation REAL,
    blue_histogram_correlation REAL,
    red_histogram_chi_square REAL,
    green_histogram_chi_square REAL,
    blue_histogram_chi_square REAL,

    -- Composite metric (calculated)
    composite_score REAL,

    -- Statistical analysis
    historical_mean REAL,
    historical_std_dev REAL,
    std_dev_from_mean REAL,
    is_anomaly BOOLEAN DEFAULT 0,

    -- Full metrics backup
    metrics_json TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE
);

-- Composite metric configuration (versioned)
CREATE TABLE IF NOT EXISTS composite_metric_config (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    version INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,

    -- Weights (should sum to 1.0)
    weight_pixel_diff REAL DEFAULT 0.25,
    weight_ssim REAL DEFAULT 0.25,
    weight_color_distance REAL DEFAULT 0.25,
    weight_histogram REAL DEFAULT 0.25,

    -- Normalization parameters
    pixel_diff_max REAL DEFAULT 100.0,
    ssim_min REAL DEFAULT 0.0,
    color_distance_max REAL DEFAULT 441.67,  -- sqrt(255^2 * 3)
    histogram_chi_square_max REAL DEFAULT 2.0,

    description TEXT,
    config_json TEXT  -- Full config as JSON for extensibility
);

-- Image storage (paths + optional thumbnails)
CREATE TABLE IF NOT EXISTS image_storage (
    storage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,

    -- Relative file paths (portable)
    new_image_rel_path TEXT NOT NULL,
    known_good_rel_path TEXT NOT NULL,
    diff_image_rel_path TEXT,
    annotated_image_rel_path TEXT,

    -- Optional thumbnails (200x200px JPEG as BLOB)
    thumbnail_new BLOB,
    thumbnail_known_good BLOB,
    thumbnail_diff BLOB,

    -- Image metadata
    image_width INTEGER,
    image_height INTEGER,
    image_format TEXT,
    file_size_bytes INTEGER,

    FOREIGN KEY (result_id) REFERENCES results(result_id) ON DELETE CASCADE
);

-- Reviewer annotations for ML training
CREATE TABLE IF NOT EXISTS annotations (
    annotation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,

    -- Annotation metadata
    annotator_name TEXT,
    annotation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    annotation_type TEXT CHECK(annotation_type IN ('bounding_box', 'polygon', 'point', 'classification')),

    -- Geometry data (JSON format)
    geometry_json TEXT,

    -- Classification/label
    label TEXT NOT NULL,
    category TEXT,
    confidence REAL,

    -- Notes
    notes TEXT,

    FOREIGN KEY (result_id) REFERENCES results(result_id) ON DELETE CASCADE
);

-- Reviewer metadata (separate from technical metrics)
CREATE TABLE IF NOT EXISTS reviewer_metadata (
    metadata_id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,

    -- Review information
    reviewer_name TEXT,
    review_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    review_status TEXT CHECK(review_status IN ('approved', 'rejected', 'needs_review', 'false_positive')),

    -- Categorical metadata
    issue_type TEXT,
    severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical')),

    -- Free-form notes
    comments TEXT,
    tags TEXT,  -- Comma-separated

    -- External references
    jira_ticket TEXT,
    external_ref TEXT,

    FOREIGN KEY (result_id) REFERENCES results(result_id) ON DELETE CASCADE
);

-- Retention policy configuration
CREATE TABLE IF NOT EXISTS retention_policy (
    policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    is_active BOOLEAN DEFAULT 1,

    -- Retention rules
    keep_all_runs BOOLEAN DEFAULT 1,
    max_runs_to_keep INTEGER,  -- NULL = unlimited
    max_age_days INTEGER,      -- NULL = unlimited
    keep_annotated BOOLEAN DEFAULT 1,
    keep_anomalies BOOLEAN DEFAULT 1,

    -- Last cleanup
    last_cleanup_timestamp DATETIME,

    description TEXT
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_runs_build_number ON runs(build_number);
CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp);
CREATE INDEX IF NOT EXISTS idx_results_run_id ON results(run_id);
CREATE INDEX IF NOT EXISTS idx_results_filename ON results(filename);
CREATE INDEX IF NOT EXISTS idx_results_subdirectory ON results(subdirectory);
CREATE INDEX IF NOT EXISTS idx_results_composite_score ON results(composite_score);
CREATE INDEX IF NOT EXISTS idx_results_is_anomaly ON results(is_anomaly);
CREATE INDEX IF NOT EXISTS idx_annotations_result_id ON annotations(result_id);
CREATE INDEX IF NOT EXISTS idx_reviewer_metadata_result_id ON reviewer_metadata(result_id);
CREATE INDEX IF NOT EXISTS idx_image_storage_result_id ON image_storage(result_id);

-- Insert default composite metric configuration
INSERT OR IGNORE INTO composite_metric_config (
    version,
    is_active,
    weight_pixel_diff,
    weight_ssim,
    weight_color_distance,
    weight_histogram,
    pixel_diff_max,
    ssim_min,
    color_distance_max,
    histogram_chi_square_max,
    description
) VALUES (
    1,
    1,
    0.25,
    0.25,
    0.25,
    0.25,
    100.0,
    0.0,
    441.67,
    2.0,
    'Default configuration with equal weights'
);

-- Insert default retention policy
INSERT OR IGNORE INTO retention_policy (
    is_active,
    keep_all_runs,
    max_runs_to_keep,
    max_age_days,
    keep_annotated,
    keep_anomalies,
    description
) VALUES (
    1,
    1,
    NULL,
    NULL,
    1,
    1,
    'Default policy: keep all runs, preserve annotations and anomalies'
);
