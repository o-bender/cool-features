def uniques(key, data):
    values = []
    for item in data:
        if key in item and item[key] not in values:
            values.append( item[key] )
            yield item

def sortby(keys, data):
    tmp = {}
    outdata = []
    for log_item in data:
        log_item_keys = log_item.keys()
        for key in keys:
            if key in log_item_keys:
                if log_item[key]:
                    tmp.update({ log_item[key]: log_item })
                    break
    k = list( tmp.keys() )
    k.sort()
    for key in k:
        outdata.append( tmp[key] )
    return outdata
