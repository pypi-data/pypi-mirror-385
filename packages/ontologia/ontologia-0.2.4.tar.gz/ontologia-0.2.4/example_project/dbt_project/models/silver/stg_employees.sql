select
  emp_id as employee_id,
  name as employee_name
from {{ source('raw_data', 'employees_tbl') }}
