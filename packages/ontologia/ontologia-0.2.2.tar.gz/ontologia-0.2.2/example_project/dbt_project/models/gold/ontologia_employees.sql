-- Feeds ObjectType "employee" expected schema
select
  employee_id as id,
  employee_name as name
from {{ ref('stg_employees') }}
