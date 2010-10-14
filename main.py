#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import google.appengine.ext.db as db

try:
    import simplejson as json
except:
    import json
import random
import hashlib
import logging

CORPUS = ['rocket',
          'laser',
          'dinosaur',
          'old people',
          'tiger',
          'chicken',
          'steel',
          'crystal',
          'engine',
          'lady',
          'baby',
          'rhino',
          'panda',
          'apocalypse',
          'zombie',
          'ninja',
          'Harrison Ford',
          'space',
          'underpants',
          'future',
          'robot',
          'chocolate',
          'shark',
          'jet',
          'gun',
          'guitar solo',
          'beard',
          'sparkle',
          'fire']


def get_corpus_matrix():
    if not hasattr(get_corpus_matrix, 'matrix'):
        matrix = list()
        for i in CORPUS:
            for j in CORPUS:
                matrix.append('%s %s' % (i, j))
        get_corpus_matrix.matrix = matrix

    return get_corpus_matrix.matrix

class Vote(db.Model):
    user = db.StringProperty()
    winner = db.StringProperty()
    loser = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Location'] = '/vote.html'
        self.response.set_status(301)

class VoteHandler(webapp.RequestHandler):
    def _get_unique_user_id(self):
        user_agent = self.request.headers['user-agent']
        address = self.request.remote_addr
        return hashlib.sha256("%s:%s" % (user_agent, address)).hexdigest()

    def get(self):
        a = b = random.choice(get_corpus_matrix())
        while b == a:
            b = random.choice(get_corpus_matrix())

        self.response.headers['content-type'] = 'application/javascript'
        self.response.out.write(json.dumps([a, b]))

    def post(self):
        winner = self.request.get('winner')
        loser = self.request.get('loser')
        matrix = get_corpus_matrix()
        if winner not in matrix or loser not in matrix:
            logging.error("We're under attack! (%s, %s) not recognized" %
                          (winner, loser))
            self.response.set_status(401)

        vote = Vote(user=self._get_unique_user_id(),
                    winner=winner,
                    loser=loser)
        vote.put()

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                         ('/vote', VoteHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
