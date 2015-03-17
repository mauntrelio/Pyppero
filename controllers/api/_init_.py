# controller API

class Controller:

    def __init__(self,master):
        self.master = master
        # load available apis
        self.apis = {}
        list_apis = list(self.master.db.apis.find())
        for api in list_apis:
            self.apis[api['api']] = api

    def process_subrequest(self):
        api_request = self.master.subrequest.split('/')[0]
        # check api exists
        if (api_request not in self.apis.keys()):
            return self.master.run_controller('404')
        else:
            current_api = self.apis[api_request]
            # check if api needs role
            if 'role' in current_api:
                if current_api['role'] > 0:
                    # api needs user authentication

                    #
                    # TODO: check user logged in...
                    # check user permission... run the api controller
                    # fine grain permission control later
                    # (number of requests per day, per ip on free apis, api actions, usw...)
                    #

            # import sys
            # sys.path.append(os.path.join(os.path.dirname(__file__),'api'))
            # api_controller = __import__(api_request+'_api')
            # api_instance = api_controller.Controller(self.master,api_request)
            # return api_instance.run()

    def list_available_apis(self):
        self.master.status = 200
        self.master.template_vars.update(apilist=self.apis)

    def run(self):
        if self.master.subrequest:
            return self.process_subrequest()
        else:
            self.list_available_apis()
