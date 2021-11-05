from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks

class Authorizer(ApplicationSession):

    def onConnect(self):
        self.join(self.config.realm, ['ticket'], 'authorizer')

    def onChallenge(self, challenge):
        if challenge.method == 'ticket':
            return 'secret123'
        else:
            raise Exception('Invalid authmethod {}'.format(challenge.method))

    @inlineCallbacks
    def onJoin(self, details):
        yield self.register(self.authorize, 'com.example.auth')

    def authorize(self, session, uri, action, options):
        self.log.info('authorize: session={session}, uri={uri}, action={action}, options={options}',
                      session=session, uri=uri, action=action, options=options)
        return True
