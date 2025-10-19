select
  emp_id as employee_id,
  company_id
from {{ source('raw_data', 'works_for_tbl') }}
