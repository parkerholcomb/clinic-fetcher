from lib import ZipsQueue, BatchFetcher

limit = 1000
offset = 10000
batchsize = 100
queue = ZipsQueue().zips_queue[offset:offset+limit]

for i in range(0, len(queue), batchsize):
    zips_batch = queue[i:i+batchsize]
    BatchFetcher(zips_batch)
    
    