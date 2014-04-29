import codecs
import json
import os
from functools import wraps
import gzip
import syss
from string import punctuation
 
def simple_caching(cachedir=None,
                   cache_comment=None,
                   autodetect=False):
    """ Caching decorator for dictionary/tuples.
        Caches gzipped json in specified cache folder
 
        Accepts the following kwargs:
 
        cachedir (default=None)
        Location of the folder where to cache. cachedir
        doesn't need to be configured if simple_caching
        is caching a method of a class with cachedir attribute.
 
        cache_comment (default=None)
        A comment to add to the name of the cache.
        If no comment is provided, the name of the cache
        if the name of the method that is being cachedonly.
 
        autodetect (default=False)
        auto detects args and kwargs that could be used
        as cache_comment.
 
        The kwargs can be set either (a) at decoration time
        or (b) when the decorated method is called:
 
        example (a):
        @simple_caching(cachedir='/path/to/cache')
        def foo(s):
            ...
 
        example (b):
        @simple_caching()
        def foo(s):
            ...
        ...
 
        foo('baz', cachedir='/path/to/cache')
 
        A combination of both is also fine, of course.
        kwargs provided at decoration time have precedence, though.
    """
    # Without the use of this decorator factory,
    # the name of the method would have been 'wrapper'
    # and the docstring of the original method would have been lost.
    #       from python docs:
    #       https://docs.python.org/2/library/functools.html#module-functools
 
    def caching_decorator(method):
        # cachedir, cache_comment and autodetect are out
        # of scope for method_wrapper, thus local variables
        # need to be instantiated.
        local_cachedir = cachedir
        local_cache_comment = cache_comment
        local_autodetect = autodetect
 
        @wraps(method)
        def method_wrapper(*args, **kwargs):
 
            # looks for cachedir folder in self instance
            # if not found, it looks for it in keyword
            # arguments.
            if not local_cachedir:
                try:
                    cachedir = args[0].cachedir
                except AttributeError:
                        cachedir = kwargs.pop('cachedir', None)
            else:
                cachedir = local_cachedir
 
            # if no cachedir is specified, then it simply returns
            # the original method and does nothing
            if not cachedir:
                return method(*args, **kwargs)
 
            if not local_cache_comment:
                cache_comment = kwargs.pop('cache_comment', '')
            else:
                cache_comment = local_cachedir
 
            if not local_autodetect:
                autodetect = kwargs.pop('autodetect', False)
            else:
                autodetect = local_autodetect
            if autodetect:
                cache_comment += "_".join([a for a in args if type(a) is str])
                cache_comment += "_".join([kwargs[kwa] for kwa in kwargs
                                           if type(kwa) in
                                           (float, int, str, unicode)])
 
            if not os.path.exists(cachedir):
                cachedir = os.path.join(os.getcwd(), cachedir)
                if not os.path.exists(cachedir):
                    print >> sys.stderr, ("[cache error] {0} is not " +
                                          "a valid dir.").format(cachedir)
                    sys.exit(1)
 
            # the ...and...or... makes sure that there is an underscore
            # between cache file name and cache comment if cache_comment
            # exists.
            cachename = '%s%s.cache.gz' % (method.__name__,
                                           (cache_comment and
                                            '_%s' % cache_comment) or '')
            # removes prefix/suffix punctuation from method name
            # (e.g. __call__ will become call)
            while cachename[0] in punctuation:
                cachename = cachename[1:]
            while cachename[(len(cachename) - 1)] in punctuation:
                cachename = cachename[:(len(cachename) - 1)]
            cachepath = os.path.join(cachedir, cachename)
 
            # loads creates cache
            if os.path.exists(cachepath):
                with gzip.open(cachepath, mode='r') as cachefile:
                    return json.loads(cachefile.read())
            else:
                print '[cache] generating %s' % cachepath
                tocache = method(*args, **kwargs)
                with gzip.open(cachepath, mode='w') as cachefile:
                    json.dump(tocache, cachefile)
                return tocache
        return method_wrapper
    return caching_decorator
