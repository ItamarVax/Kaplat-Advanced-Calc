request_id = 0

def next_request_id():
    global request_id
    request_id += 1
    return request_id


