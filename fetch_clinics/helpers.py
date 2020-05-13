def clean_for_ddb(obj):
    cleaned = {}
    for k, v in obj.items():
        if isinstance(v, dict):
            cleaned[k] = clean_for_ddb(v)
        elif isinstance(v, str):
            if v != "":
                cleaned[k]=v
        elif isinstance(v, float):
            cleaned[k] = str(v)
        else:
            cleaned[k]=v 
    return cleaned