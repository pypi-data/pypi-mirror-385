-- Analysis model for project 2
{{ config(
    materialized='view'
) }}

SELECT 
    2 as project_id,
    'project2' as project_name,
    CURRENT_TIMESTAMP as timestamp
