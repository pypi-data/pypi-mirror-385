-- Simple staging model for testing
{{ config(
    materialized='table'
) }}

SELECT 
    1 as id,
    'test' as name,
    CURRENT_TIMESTAMP as created_at
