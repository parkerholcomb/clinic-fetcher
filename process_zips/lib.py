import requests
import boto3
import os
import json
import concurrent.futures
import numpy as np
import time
from config import fetch_clinics_endpoint

class BatchFetcher:
    
    def __init__(self, zips_batch, max_workers=30):
        print(f"fetching batch that starts with {zips_batch[0:10]}")
        print("endpoint is", fetch_clinics_endpoint)
        self.zips_batch = zips_batch
        self.max_workers = max_workers
        t0 = time.time()
        self.process()
        print(f"Searched {len(zips_batch)} zip codes in {int(time.time() - t0)} seconds")
    
    @staticmethod
    def _fetch_clinics(zip_code, url = fetch_clinics_endpoint):
        r = requests.post(url,data = {'zip_code':zip_code})
        print(r.json())

    def process(self):
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            results = executor.map(ClinicFetcher._fetch_clinics, self.zips_batch)    

class ZipsQueue:



    def __init__(self):
        self.all_zip_objs = self._load_us_zips()
        self.all_zips = [z['zip_code'] for z in self.all_zip_objs]
        self.zips_cache = self._fetch_zips_cache()
        self.zips_queue = np.setdiff1d(self.all_zips,self.zips_cache)
        self.print_summary()
        
    def print_summary(self):
        print("all_zips:", len(self.all_zips))
        print("zips_cache:", len(self.zips_cache))
        print("zips_queue:", len(self.zips_queue))
        print(f"you have processed { len(self.zips_cache)/len(self.all_zips):.2f}% of zip codes")

    @staticmethod
    def _fetch_zips_cache():
        ddb = boto3.resource('dynamodb')
        table = ddb.Table('urgent_zip_cache') ## your dynamodb cache table name 
        return [z['zip_code'] for z in ZipsQueue._scan_all(table)]

    @staticmethod
    def _zip_to_str(zip):
        return ZipsQueue._zip_to_str(f"0{zip}") if len(str(zip)) < 5 else str(zip)
    
    @staticmethod
    def _load_us_zips():
        with open('./USCities.json') as f:
            zips = json.load(f)
        for z in zips:
            z['zip_code'] = ZipsQueue._zip_to_str(z['zip_code'])     
        state_codes_to_rm = ['PW','AS','MH','MP','FM','VI','GU','AP','PR','AA','AK','HI','AE']
        zips = [zip for zip in zips if zip['state'] not in state_codes_to_rm]
        return zips

    @staticmethod
    def _scan_all(ddb_table):
        response = ddb_table.scan()
        data = response['Items']
        while ('LastEvaluatedKey' in response):
            response = ddb_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
            print("record count:", len(data))
        return data
