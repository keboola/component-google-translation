'''
Template Component main class.

'''

from kbc.env_handler import KBCEnvHandler
import logging
from main import main

MANDATORY_PARS = ['#API_key', 'target_language']

APP_VERSION = '0.0.1'


class Component(KBCEnvHandler):

    def __init__(self, debug=False):
        KBCEnvHandler.__init__(self, MANDATORY_PARS)
        # override debug from config
        if(self.cfg_params.get('debug')):
            debug = True

        self.set_default_logger('DEBUG' if debug else 'INFO')
        logging.info('Running version %s', APP_VERSION)
        logging.info('Loading configuration...')

        try:
            self.validateConfig()
        except ValueError as e:
            logging.error(e)
            exit(1)

    def run(self, debug=True):
        '''
        Main execution code
        '''
        params = self.cfg_params # noqa
        api_key = params.get('#API_key')
        target_language = params.get('target_language')
        tables = self.configuration.get_input_tables()

        for t in tables:
            input_file_path = t["full_path"]
            main(input_file_path, target_language, api_key)


"""
        Main entrypoint
"""
if __name__ == "__main__":
    comp = Component()
    comp.run()
