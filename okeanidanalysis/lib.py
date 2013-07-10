"""
okeanidanalysis.lib
===================

Generally useful methods that span across submodules.

"""

import time, datetime, pytz, itertools
import numpy as np
import scipy as sp
import scipy.interpolate
import matplotlib as mpl
import matplotlib.patches

UNIX_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC)                         

golden_ratio = 1.61803398875

def utime(t, convention=None):
    """Convert time to mircoseconds since epoch.

    Expects time given as a datetime object.

    """
#    typet = type(t)
#    if typet is datetime.datetime: # t = t.timetuple()
#        return int(time.mktime(t.timetuple())*1e6 + t.microsecond)
#    else:
#        raise TypeError('time type {} not recognized'.format(typet))
#TODO something to handle matlab datenum convention easily
    return python_datetime_to_unix_epoch(t) * 1e6


def python_datetime_to_unix_epoch(dto):                                         
    try:                                                                        
        return [(dt - UNIX_EPOCH).total_seconds for dt in dto]
    except TypeError: # can't subtract offset-naive and offset-aware datetimes
        dto = (pytz.UTC.localize(dt) for dt in dto)
        return [(dt - UNIX_EPOCH).total_seconds() for dt in dto]  


def matlab_datenum_to_python_datetime(dn):                                      
    day = (datetime.datetime.fromordinal(int(n)) for n in dn)
    frac = (datetime.timedelta(days=n%1) for n in dn)
    shift = datetime.timedelta(days = 366)                                       
    return [d + f - shift for d, f in itertools.izip(day, frac)] 


def injectlocals(l, skip=['self','args','kwargs'], **kwargs):
    """Update a dictionary with another, skipping specified keys."""
    if l.has_key('kwargs') : kwargs.update(l['kwargs'])
    kwargs.update(dict((k, v) for k, v in l.items() if k not in skip))
    return kwargs


def make_multiplier(n): return lambda x: x*n


def make_divider(n): return lambda x: x/n


def indexclip(s, e, *a): return [b[int(s):int(e)] for b in a]


def angle_difference(a, b, degrees=False):
    if degrees: p = 180.0
    else: p = np.pi
    return np.mod(np.unwrap(a, p) - np.unwrap(b, p) + p, 2 * p) - p


def rad2deg360(x):
    """
    
    """
    d = np.rad2deg(x)
    d[d < 0] += 360
    return d
    

def rmnans(x, *a):
    """Remove values from array(s), using NaNs in key array.

    Examples
    --------
    >>> b = np.array([0,1,nan,3])
    >>> c = np.ones(b.shape)
    >>> bn, cn = rmnans(b,c)
    >>> bn
    array([ 0.,  1.,  3.])
    >>> cn
    array([ 1.,  1.,  1.])

    """
    mask = np.isnan(x)
    y = [x[~mask]]
    for b in a: y.append(b[~mask])
    return y


def plot_date_blocks(t, v, axes, colormap=None, unit_height=False, **kw):
    #TODO logic to check edges & heights for sanity
#    if kw.has_key('ec') or kw.has_key('edgecolor'): 
#        pass
#    else:
#        kw.update(dict(edgecolor='red'))
    d = np.diff(v)
    left = np.hstack((t[0],t[d.nonzero()]))
    right = np.hstack((t[d.nonzero()],mpl.dates.num2date(axes.get_xlim()[-1])))
    height = np.hstack((v[d.nonzero()], v[-1]))
    print height
    norm_height = height / np.float(np.max(height))
    for l, r, h, nh  in itertools.izip(left, right, height, norm_height):
        # draw a rectangle with the appropriate color
        if colormap:
            kw.update(dict(color = colormap(nh)))
        if unit_height: 
            h = 1 # do this _after_ colormap
        ll = (mpl.dates.date2num(l),0)
        w = mpl.dates.date2num(r) - mpl.dates.date2num(l)
        axes.add_patch(mpl.patches.Rectangle(ll, w, h, **kw))
    pt = np.vstack((left, right))
    pv = np.vstack((height, height))
    print pt.shape, pv.shape
    axes.plot_date(pt.ravel('F'), pv.ravel('F'), 'k-')

# TODO modify to use PatchCollection and set colors that way
# http://matplotlib.org/examples/api/patch_collection.html


def slant_range_and_depths_to_horizontal_range(r, d1, d2):
    """
    Compute the radius of a circle on a sphere (half-chord on a circle)
    using the Pythagorean theorem, the sphere radius, and the apothem (in
    this case, the difference in depths).

    Sphere radius must be greater than difference in depths.

    Examples
    --------
    >>> depth_corrected_range(10, 5, 9)
    # TODO
    """
    return (r**2 - (d1 - d2)**2) **0.5

