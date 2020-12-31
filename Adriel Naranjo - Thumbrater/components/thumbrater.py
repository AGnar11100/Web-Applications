from py4web import action, URL, request
from yatl.helpers import XML
from py4web.utils.url_signer import URLSigner
from py4web.core import Fixture

class ThumbRater(Fixture):

    THUMBRATER = '<thumbrater url="{url}" callback_url="{callback_url}"></thumbrater>'

    def __init__(self, url, session, signer=None, db=None, auth=None):
        self.url = url + '/get'
        self.callback_url = url + '/set'
        self.signer = signer or URLSigner(session)

        self.__prerequisites__ = [session]
        args = list(filter(None, [session, db, auth, self.signer.verify()] ))
        f = action.uses(*args)(self.get_rating)
        action(self.url + "/<id>", method=["GET"])(f)
        f = action.uses(*args)(self.set_rating)
        action(self.callback_url + "/<id>", method=["GET"])(f)


    def __call__(self, id=None):

        return XML(ThumbRater.THUMBRATER.format(url=URL(self.url, id, signer=self.signer), callback_url=URL(self.callback_url, id, signer=self.signer)))


    def get_rating(self, id=None):
        pass


    def set_rating(self, id=None):
        pass


