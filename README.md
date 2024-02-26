# REPOSITORY ARCHIVE NOTICE
This repository is now archived. You are free to fork this or to visit an updated python implementation.  
At the time of writing, the most up-to-date python code is located here: https://github.com/maxperron/lufa-delivery  
- commit hash: `f8b04b4`  
- branch: `dev-testing`

(According to this [PR #2](https://github.com/JohnnyLin-a/lufa-weekly-canceler/pull/2))

# Original README below:

# Lufa Farms weekly order canceler

Once upon a time, we were able to order grocery from Lufa Farms whenever and however we wanted.  
After recent development, they have switched the process to become a subscription model and are forcing us customers to order consistently every week.  
This script cancels all regular weekly orders.

## Why even do this?

Because you can always use the `Extra Basket` feature to get grocery delivered as quick as Amazon Prime 1-day shipping anyway!

## How to run this:

1. Fork this repo
2. Configure the `LUFA_CANCELER_CONFIG` repository secret in your fork, according to the config.json.template file. (Fill in the blanks)
3. Enable github workflows.
