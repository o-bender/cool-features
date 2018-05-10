from domain_dispatcher import DomainsDispatcher
import MiSolvenciaApp
import MiSolvenciaApp.creditotitan_com as CreditotitanComApp
import MiSolvenciaApp.creditotitan_com_mx as CreditotitanComMxApp


misolvencia_app = MiSolvenciaApp.create_app(MiSolvenciaApp.app)
creditotitancom_app = CreditotitanComApp.create_app(CreditotitanComApp.app)
creditotitancommx_app = CreditotitanComMxApp.create_app(CreditotitanComMxApp.app)
application = DomainsDispatcher({
    'localhost': misolvencia_app,
    'misolvencia.es': misolvencia_app,
    'creditotitan.com': creditotitancom_app,
    'creditotitan.com.mx': creditotitancommx_app,
})
