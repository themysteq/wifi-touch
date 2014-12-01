__author__ = 'mysteq'


import apihelper


if __name__ == "__main__":
    print "Hello!"
    query = apihelper.APIRequest()
    container = apihelper.IOContainer()

    for i in range(4):
        query.activate()
        response = apihelper.APIResponse()
        response.request_id = query.request_id
        container.putFinishedAsIterable(response.request_id, response)


    print container
    print container.getFinishedFromIterables(query.request_id)