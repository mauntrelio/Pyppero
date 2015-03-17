# Test controller


class Controller:
    
    def __init__(self,master):
        self.master = master
    
    def run(self):
        #self.master.template_vars.update(test='test')
        
        def response(environ, start_response):
            start_response('200 OK', [('content-type', 'text/plain')])
            contents = ["Hello world!",
												str(self.master.subrequest),
												str(self.master.request.headers)
            						]
            data = "\n".join(contents)
            yield data 

        return response


