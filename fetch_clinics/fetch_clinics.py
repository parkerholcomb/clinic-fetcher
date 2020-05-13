import json
import googlemaps
import boto3
import time
import os
from helpers import clean_for_ddb

ddb = boto3.resource('dynamodb', aws_access_key_id=os.environ['ACCESS_KEY'],aws_secret_access_key=os.environ['SECRET_KEY'])
gmaps = googlemaps.Client(key=os.environ['GOOGLE_KEY'])

def put_places_ddb(places, zip_code):
    for place in places:
        item = clean_for_ddb(place)
        item['fetched_at'] = str(int(time.time()))
        item['zip_code'] = zip_code
        response = ddb.Table('urgent_care').put_item(Item=item) # you might have different table name
        print("place:", place['name'])

def geocode_zip(zip_code):
    print('searching zip:', zip_code)
    response = gmaps.geocode(f"{zip_code}")
    return response[0]['geometry']['location']

def cache_zip_code(zip_code):
    ddb.Table('urgent_zip_cache').put_item(Item={'zip_code': str(zip_code)}) # you might have different table name

def main(event, context):
    zip_code = event['body'].split("=")[-1] #todo 
    results_counter = 0
    t0 = time.time()
    if zip_code:
        response = gmaps.places("urgent care", location=geocode_zip(zip_code))
        token = response.get('next_page_token',False)
        put_places_ddb(response['results'], zip_code)
        results_counter += len(response['results'])
        while token:
            time.sleep(2) #NB next_page_token not instantly available
            response = gmaps.places("urgent care", page_token=token)
            token = response.get('next_page_token',False)
            put_places_ddb(response['results'], zip_code)
            results_counter += len(response['results'])
        t1 = time.time()
        cache_zip_code(zip_code)
        msg = f"fetch_clinics found {results_counter} results for {zip_code} in {int(t1-t0)} seconds"
        print(msg)
        return {
            'statusCode': 200,
            'body': json.dumps(msg)
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('no zip code found')
        }

if __name__ == "__main__":
    main('', '')