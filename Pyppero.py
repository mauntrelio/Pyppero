# -*- coding: utf-8 -*-

import pymongo
import json
import os
import re
import sys
import datetime
import time
from werkzeug.wrappers import Request, Response
from werkzeug.utils import append_slash_redirect
from jinja2 import Environment, FileSystemLoader
from babel.support import Translations

__version__ = '0.0.1'

class configClass:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class Pyppero:
    ## TODO : error handling (who cares?) ##
    def __init__(self, environ, start_response):
        # define environ and start_response for WSGI
        self.environ = environ
        self.start = start_response
        # read the configuration file
        config_file = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
        if os.path.isfile(config_file):
            config_dict = json.load(open(config_file,'r'))
            self.config = configClass(**config_dict)
        # fallback config for possible missing config parameters
        self.fallback_config()
        # make templates, controllers and locales' paths absolute
        self.config.templates_path = os.path.join(os.path.dirname(__file__), self.config.templates_path)
        self.config.controllers_path = os.path.join(os.path.dirname(__file__), self.config.controllers_path)
        self.config.locales_path = os.path.join(os.path.dirname(__file__), self.config.locales_path)
        # find out available locales and languages
        self.available_languages = {}
        for locale in os.listdir(self.config.locales_path):
            if os.path.isdir(os.path.join(self.config.locales_path,locale)):
                language = locale.split('_')[0]
                if language in self.available_languages:
                    self.available_languages[language].append(locale)
                else:
                    self.available_languages[language] = [locale]
        # build up array of available_locales
        self.available_locales = [item for lang in self.available_languages.keys() for item in self.available_languages[lang]]
        # append controllers path to sys path 
        sys.path.append(self.config.controllers_path)
        # create jinja2 Environment
        self.jinja_env = Environment(extensions=['jinja2.ext.i18n'],
            loader=FileSystemLoader(self.config.templates_path), 
            autoescape=False)
        # open the connection with mongo (and select database)
        self.db = pymongo.MongoClient(self.config.db_host,self.config.db_port)[self.config.db_name]
        # assign default view 
        self.view = self.config.default_view
        # default "code" of the request and "page", assign other defaults
        self.code = ''
        self.page = None
        self.subrequest = ''
        self.template_vars = self.config.default_vars
        self.status = 404
        self.response_headers = []
        self.content_type = 'text/html; charset=UTF-8'

    def __iter__(self):
        # This is the actual call to the application as a singletone instance
        self.request = Request(self.environ)
        response = self.dispatch_request()
        return response(self.environ, self.start)

    def fallback_config(self):
        # assign default config for params missing in config file
        default_config = {
            'domain_name' : 'localhost.localdomain',
            'db_host': 'localhost',
            'db_port': 27017,
            'db_name': 'localdb',
            'templates_path' : 'templates',
            'controllers_path' : 'controllers',
            'locales_path' : 'locale',
            'default_view': '404.j2',
            'default_locale': 'en_US',
            'cookie_days_expires' : 7,
            'default_vars' : {
                'domain_name' : 'localhost.localdomain',
                'locale' : 'en_US',
                'language' : 'en'
            }
        }
        for key in default_config:
            if not key in self.config.__dict__:
                self.config.__dict__[key] = default_config[key]

    def search_language(self,user_language):
        found = False
        # look for user language in available locales
        if user_language in self.available_locales:
            self.locale = user_language
            found = True
        # look for user language in generic available languages
        elif user_language in self.available_languages:
            # set the locale to the first associated national locale
            self.locale = self.available_languages[user_language][0]
            found = True
        # actually found available locale
        if found:
            # save preference in a cookie
            self.save_language_preference()
            # expand locale with charset
            self.locale = self.locale + '.UTF8'
        return found

    def negotiate_language(self):
        # FIRST CHOICE: query string parameter
        if 'hl' in self.request.args:
            if self.search_language(self.request.args['hl']): return
        # SECOND CHOICE: user cookie
        if 'hl' in self.request.cookies:
            if self.search_language(self.request.cookies['hl']): return
        # THIRD CHOICE: browser content language negotiation
        ul = self.request.accept_languages.values()
        for hl in ul:
            if self.search_language(hl): return
        # FOURTH CHOICE: browser language
        bl = self.request.user_agent.language
        if self.search_language(bl): return
        # FIFTH CHOICE: return the default
        self.locale = self.config.default_locale

    def save_language_preference(self):
        # save language preference in a cookie
        max_age = self.config.cookie_days_expires * 24 * 3600 
        expires = time.time() + max_age
        cookie_expires =time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime(expires))
        cookie = 'hl=%s; Domain=.%s; Expires=%s; Max-Age=%s; Path=/' % \
                (self.locale, self.config.domain_name, cookie_expires, max_age)
        self.response_headers.append(('Set-Cookie',cookie))

    def run_controller(self,controller_name):
        # import the file and run controller instance
        module_controller = __import__(controller_name)
        controller = module_controller.Controller(self)
        return controller.run()
    
    def render_template(self):
        # load the translations
        translations = Translations.load(self.config.locales_path, self.locale)
        # install get_text on the templates
        self.jinja_env.install_gettext_translations(translations,True)
        # load the template
        template = self.jinja_env.get_template(self.view)
        # render template
        return template.render(self.template_vars)

    def route_request(self):
        # ROUTING IS HERE 
        # find out code and subrequest matching host name or request path 
        # //xyz.domain.tld/abc/d/ is equivalent to //domain.tld/xyz/abc/d/
        # code = xyz, subrequest = abc/d
        # 3rd level domain
        matches = re.findall(r'^([a-z0-9-]+)\.%s$' % self.config.domain_name,self.request.host,re.I)
        if matches:
            self.code = matches[0]
            self.subrequest = self.request.path[1:-1]
        # first path part 
        else:
            matches = re.findall(r'^/([^/]+)/(.*)$',self.request.path,re.I)
            if matches:
                self.code = matches[0][0]
                if matches[0][1]:
                    self.subrequest = matches[0][1][:-1]

    def update_visit_counter(self):
        # update visit counters of the page
        now = datetime.datetime.utcnow()
        (year, month, day) = map(str,(now.year,now.month,now.day))
        visits_increment = {
            'visits.counter':1,
            '.'.join(('visits',year,'counter')) : 1,
            '.'.join(('visits',year,month.zfill(2),'counter')): 1,
            '.'.join(('visits',year,month.zfill(2),day.zfill(2),'counter')): 1
            }
        self.db.urls.update({'code':self.code},{'$set': {'lastaccess' : now }, '$inc': visits_increment})        

    def dispatch_request(self):
        # actually serve the request
        # if missing, redirect to same URL with trailing slash
        # TODO: review this mechanism if we have an extension (e.g.: .jpg, .json, etc..)
        if self.request.path[-1] != '/':
            return append_slash_redirect(self.environ)
        # init controller name and response to None
        controller_name = response = None
        # apply routing
        self.route_request()
        # find and set the page from db
        self.page = self.db.urls.find_one({'code':self.code})
        # got the page
        if self.page:
            # update visits counter
            self.update_visit_counter()
            # check and assign controller (if any) 
            if 'controller' in self.page:
                if os.path.isfile(os.path.join(self.config.controllers_path,self.page['controller']+'.py')):
                    controller_name = self.page['controller']
            # check and assign template (if page and template are there status is 200)
            if 'view' in self.page:
                if os.path.isfile(os.path.join(self.config.templates_path,self.page['view'])):
                    self.status = 200
                    self.view = self.page['view']
                    self.template_vars.update(page=self.page)
        # negotiate the language
        self.negotiate_language()
        # load and run the controller (if any)
        if controller_name:
            response = self.run_controller(controller_name)
        # if the controller returns a response we return it
        if response:
            return response
        # otherwise proceed with normal response
        else:
            # render the template
            content = self.render_template()
            return Response(content, status=self.status, headers=self.response_headers, content_type=self.content_type)
