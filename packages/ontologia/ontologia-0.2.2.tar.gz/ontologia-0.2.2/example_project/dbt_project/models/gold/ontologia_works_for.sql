-- Feeds LinkType "works_for" with standardized columns
select
  employee_id as emp_id,
  company_id
from {{ ref('stg_works_for') }}
