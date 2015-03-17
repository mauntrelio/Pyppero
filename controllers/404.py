# 404 error controller

class Controller:

    def __init__(self,master):
        self.master = master

    def run(self):
        self.master.status = 404
        self.master.view = '404.j2'
