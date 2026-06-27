# Database Schema

This document describes the core database model and relationships for the Rojgari project.

> Source: `file:///Users/pablo/Library/Containers/net.whatsapp.WhatsApp/Data/tmp/documents/DE5683CE-2E06-4A4E-92B0-F3241A6C1452/rojgari_database_schema.html`

## Overview

The schema is centered around users, workers, customers, service categories, service requests, bookings, payments, reviews, notifications, and worker location history.

## Tables

### `USER`
- `uuid id` (PK)
- `string full_name`
- `string phone_number` (UK)
- `string email` (UK)
- `string password_hash`
- `string role`
- `string profile_photo_url`
- `boolean is_active`
- `boolean is_verified`
- `timestamp created_at`
- `timestamp updated_at`

### `CUSTOMER`
- `uuid id` (PK)
- `uuid user_id` (FK)
- `string address`
- `float default_lat`
- `float default_lng`
- `timestamp created_at`

### `WORKER`
- `uuid id` (PK)
- `uuid user_id` (FK)
- `string bio`
- `float avg_rating`
- `int total_jobs`
- `boolean is_available`
- `boolean is_approved`
- `float current_lat`
- `float current_lng`
- `geometry current_location`
- `string bank_account`
- `string wallet_number`
- `timestamp approved_at`
- `timestamp created_at`

### `WORKER_DOCUMENT`
- `uuid id` (PK)
- `uuid worker_id` (FK)
- `string document_type`
- `string file_url`
- `string verification_status`
- `string rejection_reason`
- `timestamp submitted_at`
- `timestamp reviewed_at`

### `SERVICE_CATEGORY`
- `uuid id` (PK)
- `string name` (UK)
- `string description`
- `string icon_url`
- `boolean is_active`
- `timestamp created_at`

### `WORKER_SERVICE`
- `uuid id` (PK)
- `uuid worker_id` (FK)
- `uuid category_id` (FK)
- `int years_experience`
- `string skill_level`
- `decimal hourly_rate`
- `timestamp created_at`

### `SERVICE_REQUEST`
- `uuid id` (PK)
- `uuid customer_id` (FK)
- `uuid category_id` (FK)
- `string description`
- `string status`
- `float customer_lat`
- `float customer_lng`
- `geometry customer_location`
- `string address`
- `timestamp requested_at`
- `timestamp expires_at`

### `BOOKING`
- `uuid id` (PK)
- `uuid request_id` (FK)
- `uuid worker_id` (FK)
- `string status`
- `decimal agreed_price`
- `timestamp accepted_at`
- `timestamp started_at`
- `timestamp completed_at`
- `timestamp cancelled_at`
- `string cancellation_reason`

### `PAYMENT`
- `uuid id` (PK)
- `uuid booking_id` (FK)
- `decimal amount`
- `string method`
- `string status`
- `string transaction_ref` (UK)
- `timestamp paid_at`

### `REVIEW`
- `uuid id` (PK)
- `uuid booking_id` (FK)
- `uuid reviewer_id` (FK)
- `uuid reviewee_id` (FK)
- `int rating`
- `string comment`
- `timestamp created_at`

### `NOTIFICATION`
- `uuid id` (PK)
- `uuid user_id` (FK)
- `string title`
- `string body`
- `string type`
- `boolean is_read`
- `uuid reference_id`
- `string reference_type`
- `timestamp created_at`

### `WORKER_LOCATION_HISTORY`
- `uuid id` (PK)
- `uuid worker_id` (FK)
- `float lat`
- `float lng`
- `geometry location`
- `timestamp recorded_at`

## Relationships

- `USER` ||--|| `CUSTOMER` : "has profile"
- `USER` ||--|| `WORKER` : "has profile"
- `WORKER` ||--o{ `WORKER_DOCUMENT` : "submits"
- `WORKER` ||--o{ `WORKER_SERVICE` : "offers"
- `SERVICE_CATEGORY` ||--o{ `WORKER_SERVICE` : "categorizes"
- `SERVICE_CATEGORY` ||--o{ `SERVICE_REQUEST` : "requested for"
- `CUSTOMER` ||--o{ `SERVICE_REQUEST` : "places"
- `SERVICE_REQUEST` ||--o| `BOOKING` : "leads to"
- `WORKER` ||--o{ `BOOKING` : "accepts"
- `BOOKING` ||--o| `PAYMENT` : "has"
- `BOOKING` ||--o{ `REVIEW` : "receives"
- `USER` ||--o{ `NOTIFICATION` : "receives"
- `WORKER` ||--o{ `WORKER_LOCATION_HISTORY` : "tracked in"

## Notes

This file reflects the schema defined in the HTML ER diagram source. If the diagram changes, update this document to keep the table and relationship definitions aligned.
