# API controller DNS

class Controller:

    def __init__(self,master,name):
        self.master = master

    def run(self):
        self.metadata = self.master.db.apis.find_one({'api':name})
        if not self.metadata:
             return self.master.run_controller('404')
        # elif self.metadata.role
        #
        # to do
        #

