## How is expiry set?

There is a helper, in file -
lambda_functions/v1/functions/lpa_codes/app/api/helpers.py
  which provides a calculate_expiry_date function
This simply adds on 12 months to the provided date

This is called by insert_new_code,  in lambda_functions/v1/functions/lpa_codes/app/api/code_generator.py,  using today's date to add the 12 mon to and puts the result in the expiry_date field.

This in turn is called by the code creation endpoint, in lambda_functions/v1/functions/lpa_codes/app/api/endpoints.py

## When is expiry set?
As described above, it is done on creation, in the code creation endpoint, in lambda_functions/v1/functions/lpa_codes/app/api/endpoints.py

## What happens at the expiry point?
Expiry date is set as ttl field in the terraform, so dynamo will automatically remove these

## Does the code handle expired codes gracefully?
The code for searching dynamo has extra checking to handle the 48 hr period which AWS say may elapse before deletion actually happens. Other than that, expired codes simply get deleted so no longet will appear

## Changes required for new paper code support
For Modernise codes the difference we will want to
(a) set expiry date on 1st use instead of at creation
(b) set expiry date to 2 yrs time instead of 1 yr
