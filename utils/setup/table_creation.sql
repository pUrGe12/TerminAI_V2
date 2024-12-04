CREATE TABLE History_v3 (
    id SERIAL PRIMARY KEY,
    "Prompt" TEXT NOT NULL,
    "Categorizer_json" JSONB NOT NULL,
    "Results" JSONB NOT NULL
);