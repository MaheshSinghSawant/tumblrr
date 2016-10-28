#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template


class LoginPage(webapp2.RequestHandler):
    def get(self):
        # self.response.headers['Content-Type'] = 'text/plain'
        # self.response.out.write("Hey, ")
        #

        # if user:
        #     nickname = user.nickname()
        #     logout_url = users.create_logout_url('/')
        #     greeting = 'Welcome  {}!  <p><a href="{}">sign out</a></p>'.format(
        #         nickname, logout_url)
        # else:
        #     login_url = users.create_login_url('/')
        #     greeting = '<a href="{}">Sign in</a>'.format(login_url)
        #
        # self.response.write(
        #     '<html><body>{}</body></html>'.format(greeting))

        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            upload_url = self.request.uri + 'form'
            upload_url_linktext = 'Upload Data'
            nickname = user.nickname()
            greeting = 'Welcome, {} '.format(nickname)

            p = 'loggedin.html'
        else:
            upload_url = self.request.uri
            upload_url_linktext = ''
            url = users.create_login_url(self.request.uri)
            greeting = 'Welcome please log in: '
            url_linktext = 'Login'
            p = 'loggedout.html'

        template_values = {

            'greeting': greeting,
            'url': url,
            'url_linktext': url_linktext,
            'upload_url': upload_url,
            'upload_text': upload_url_linktext
        }

        path = os.path.join(os.path.dirname(__file__), p)
        self.response.out.write(template.render(path, template_values))


class UserPhoto(ndb.Model):
    user = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()


class PhotoUploadFormHandler(webapp2.RequestHandler):
    def get(self):
        # [START upload_url]
        upload_url = blobstore.create_upload_url('/upload_photo')
        # [END upload_url]
        # [START upload_form]
        # To upload files to the blobstore, the request method must be "POST"
        # and enctype must be set to "multipart/form-data".
        self.response.out.write("""
<html><head><link type="text/css" rel="stylesheet" href="/static/main.css" /></head><body>
<form action="{0}" method="POST" enctype="multipart/form-data">
  Upload File: <input type="file" name="file"><br>
  <input type="submit" name="submit" value="Submit">
</form>
</body></html>""".format(upload_url))
        # [END upload_form]


# [START upload_handler]
class PhotoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            upload = self.get_uploads()
            user_photo = UserPhoto(
                user=users.get_current_user().user_id(),
                blob_key=upload[0].key())
            user_photo.put()

            self.redirect('/view_photo/%s' % upload[0].key())

        except:
            self.error(500)
# [END upload_handler]


# [START download_handler]
class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)
# [END download_handler]


app = webapp2.WSGIApplication([('/', LoginPage),
                               ('/form', PhotoUploadFormHandler),
                               ('/upload_photo', PhotoUploadHandler),
                               ('/view_photo/([^/]+)?', ViewPhotoHandler),
                               ], debug=True)
