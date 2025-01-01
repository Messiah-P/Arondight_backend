class Listener(object):

    def before_action(self, scoped_session, context):
        pass

    def after_action(self, scoped_session, context, status, msg):
        pass