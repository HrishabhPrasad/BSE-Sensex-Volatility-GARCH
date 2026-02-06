CREATE DATABASE BSE_INDICES;


USE BSE_INDICES;



SELECT * FROM sensex_data LIMIT 9000;


SELECT 
    MIN(record_date) as start_date, 
    MAX(record_date) as end_date, 
    COUNT(*) as total_days
FROM sensex_data;