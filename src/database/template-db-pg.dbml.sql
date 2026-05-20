-- Active: 1777889443311@@127.0.0.1@5432@template
-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: PostgreSQL
-- Generated at: 2026-04-26T13:30:03.734Z

CREATE TABLE "Attachments" (
  "id" uuid PRIMARY KEY DEFAULT (gen_random_uuid()),
  "filename" varchar(255),
  "original_name" varchar(255),
  "file_path" varchar(500),
  "file_size" bigint,
  "mime_type" varchar(100),
  "file_hash" varchar(64),
  "url" varchar(255),
  "uploaded_by" uuid,
  "uploaded_at" timestamp,
  "deleted_at" timestamp
);

CREATE INDEX ON "Attachments" ("file_hash");

CREATE INDEX ON "Attachments" ("uploaded_by");

CREATE INDEX ON "Attachments" ("uploaded_at");

CREATE INDEX ON "Attachments" ("uploaded_by", "uploaded_at");