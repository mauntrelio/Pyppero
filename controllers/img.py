
from werkzeug.http import generate_etag, is_resource_modified, http_date
from PIL import Image
import os.path

# flirpy (flickr in python + Mongo) + slirpy (slir in python)

class Controller:
    
  def __init__(self,master):
    self.master = master
    # TODO: read the configuration (move it to somth. slirpy specific)
    self.img_folder = '/var/home/giannozzo/flickr/photo'
    self.cache_folder = '/var/home/giannozzo/flickr/cache'

  def give_404(self):
    return self.master.run_controller('404')

  def run(self):

    # slirpy: SLIR like image resize/crop/watermark service

    # TODO list
    # - improve code to make it usable with werkzeug and flask
    #   - at least work with some classes that could be reusable in those environments
    #   - smth like img = Slirpy(config,path) <--- how do I manage cache?
    #   - define methods/properties like img.http_headers(), img.content(), img.path_to_cached()
    # - also manage here http interface??
    # - parse resize/crop url params
    # - resize/crop image ( + caching and modification of original image)
    # - for etag... manage cache of etags to avoid rereading file and calculate? 
    # - serve proper content-type

    if self.master.subrequest:
      image_file = os.path.join(self.img_folder,self.master.subrequest)
      if os.path.isfile(image_file):

        def response(environ, start_response):
          headers = []
          with open (str(image_file), 'rb') as myfile:
            # improve this: manage cache of etags
            # maybe directly in slir-like cache filenames?
            data = myfile.read()
          last_modified = http_date(os.path.getmtime(image_file))
          etag = generate_etag(data)
          headers.append(('Last-Modified', last_modified))
          headers.append(('ETag', etag))
          # serve fresh result
          if is_resource_modified(environ, etag=etag, last_modified=last_modified):
            content_length = str(os.path.getsize(image_file))
            headers.append(('Content-Type', 'image/jpeg'))
            headers.append(('Content-Length', content_length))
            start_response('200 OK', headers)
            yield data
          # not modified (304)
          else:
            start_response('304 Not modified', headers)
            yield ''

        return response

    # give 404 by default
    self.give_404()


class Slirpy:
  def __init__(self,request,etag=None,last_modified=None):
    self.request = request
    # TODO: read the configuration (move it to smth slirpy specific)
    self._img_folder = '/var/home/giannozzo/flickr/photo'
    self._cache_folder = '/var/home/giannozzo/flickr/cache'
    self._no_photo = ''
    self._watermark_position = 'center-center' 
    #  top-left      top-center     top-right
    #  center-left   center-center  center-right
    #  bottom-left   bottom-center  bottom-right

    self._request_etag = etag
    self._request_last_modified = last_modified

    self._etag = ''
    self._last_modified = 0
    self._status = 404

    self._width = 0
    self._height = 0
    self._crop = (0,0)
    self._ratio = 1
    self._region = (0,0,0,0)
    
    self._orig_image = None
    self._image = None


  # split request (/w35-h23-c1:1/path/to/photo.jpg)
  # evaluate:
  #  - params (w,h,c), later quality and/or other
  #  - path to photo (file exists?)
  #  - calculate checksum of request (md5 or sha1)
  #  - check existance of cached request copy
  #     - evaluate modification date of orig image and cached request
  #     - recreate cached copy if necessary (resize, crop, png transparency, watermark)
  #  - evaluate etag, last-modified (should this be evaluated by the upper level?)
  #  - provide methods to give headers (type,length,etag,date-modified) and status
  #  - provide method to get image content
  # calculate sharpness factor (slir)

  # def __read_config(self):
  #   pass

  # def __read_params(self):
  #   pass

  # def http_headers(self):
  #   pass

  # def get_etag(self):
  #   pass

  # def get_last_modified(self):
  #   pass

  # def mime_type(self):
  #   pass

  # def filesize(self):
  #   pass

  # def render(self):
  #   pass

  # def path_to_cached(self):
  #   pass

  # def __is_cached(self):
  #   pass

  # def __create_cached(self):
  #   pass
