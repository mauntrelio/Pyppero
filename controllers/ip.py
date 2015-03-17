# IP controller (print client remote address)

class Controller:

    def __init__(self,master):
        self.master = master

    def run(self):
        if self.master.subrequest:
            return self.master.run_controller('404')
        else:
            self.master.status = 200
            self.master.content_type = 'text/plain; charset=US-ASCII'
            if self.master.request:
                self.master.template_vars.update(content=self.master.request.remote_addr)
