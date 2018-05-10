from flask import Flask

class DomainsDispatcher(Flask):
    config = {'TEMPLATES_AUTO_RELOAD': False}
    def __init__(self, app_instances, *args, **kwargs):
        self.app_instances = app_instances

    def __call__(self, environ, start_response):
        app = self._get_application(environ['HTTP_HOST'])
        return app(environ, start_response)

    def _get_application(self, host):
        host = host.split(':')[0]
        app = self.app_instances.get(host)
        assert app, 'Domain not found'
        return app
