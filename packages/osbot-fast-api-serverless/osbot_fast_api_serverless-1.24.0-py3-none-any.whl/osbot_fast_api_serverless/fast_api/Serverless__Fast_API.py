from osbot_fast_api.api.Fast_API                                     import Fast_API
from mangum                                                          import Mangum
from osbot_utils.utils.Env                                           import load_dotenv
from osbot_fast_api_serverless.fast_api.routes.Routes__Info          import Routes__Info
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API__Config import Serverless__Fast_API__Config


class Serverless__Fast_API(Fast_API):
    config: Serverless__Fast_API__Config

    def setup(self):
        load_dotenv()                                       # needed for api key support # todo: add this to Fast_API class (maybe as an top level option)
        super().setup()
        return self

    def handler(self):
        handler = Mangum(self.app())
        return handler

    def setup_routes(self):
        self.add_routes(Routes__Info)