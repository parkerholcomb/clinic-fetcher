# Clinic Fetcher

This project asychronously searches the Google Places API for "urgent care" locations. It iterates over all of the US Zip Codes, and stores the results in a document database. It could be easily adapted to any other term.

[clinic fetcher](https://github.com/parquar/clinic-fetcher/blob/master/clinic-fetcher.png?raw=true)

## Setup

In order to run this you'll need:
- Two DynamoDB tables: a destination table, and a cache table
- AWS Lambda (via Serverless Framework)
- A Google Places API key
- A python server that support concurrency (e.g. EBS on ec2)

## database setup

You'll want to set up the following tables:

- `urgent_care` with pk `place_id` 
- `urgent_zips_cache` with pk `zip_code` 

NB: Depending on concurrency settings you'll need to up your Write capacity units or your destination table and read units on your cache table

## 1. fetch_clinics

This is a lambda function that searches the Google Places API for "urgent care" in that zip, and stores the results to a document database (in our case, DynamoDB). Once you `serverless deploy` and have an endpoint, you're ready to move on.

### Notes:

The Places API requires a `sleep(2)` between pagination, and each invocation takes ~7 seconds. Hence why we're using Lambda!

`fetch_clinics` uses the [Serverless Framework](http://serverless.com/), and you'll need to update the `serverless.yml` with your own app names and keys. See notes at the top of the yml file about packaging your modules.

This is designed to "over fetch". Results may and will include: 
- more than urgent care facilities (private practices, dentists, etc)
- results from nearby zip codes 
- duplicate records (Only unique `place_id` will save to Dynamodb)


## 2. process_zips

Once you have `fetch_clinics_endpoint`, you're ready to start fetching! I ran this on an micro ec2 instance and let it run for a few hours, and voila!  

## ⚠️ Warning! ⚠️

Google Places API is not free.