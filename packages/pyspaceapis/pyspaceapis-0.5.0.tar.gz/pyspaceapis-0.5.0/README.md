# 📡 | PySpaceAPI Wrapper!

PySpaceAPI is a fairly thin
(for now at least) API
wrapper, which aims to provide
some more ease when it
comes to retrieving astronomical data
from available public APIs! The
goal is to add support
for all, if not as
many endpoints as possible that
fall within the scope of
astronomical data. And possibly in
the future add more functionality
to the wrapper to achieve
more than simply retrieving data
and returning it as a
python dict, as well as
adding support for multiple other
non-NASA APIs!

Currently, this wrapper contains **nineteen**
endpoints (out of the many
planned) from NASA, but there
will be more in the
future!

## | Currently Supported Endpoints:

> ### 💡
> 
> *Most explanations and in-depth documentation
> seen here are provided by 
> the [**official NASA APIs page**](https://api.nasa.gov)*.

### [**Astronomy Picture of the Day**](https://apod.nasa.gov/apod/astropix.html) (APOD)

"The full documentation for this
API can be found in
the [**APOD API GitHub
repository**](https://github.com/nasa/apod-api)"

  - [**apod**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L32)
    - "This endpoint structures the APOD
    imagery and associated metadata so
    that it can be repurposed
    for other applications."

### [**Near Earth Object Web Service**](https://cneos.jpl.nasa.gov) (Asteroids NeoWs)

"NeoWs (Near Earth Object Web
Service) is a RESTful web
service for near earth Asteroid
information. With NeoWs a user
can: search for Asteroids based
on their closest approach date
to Earth, lookup a specific
Asteroid with its NASA JPL
small body id, as well
as browse the overall data-set."

  - [**Neo - Feed**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L93)
    - "Retrieve a list of Asteroids based on their closest approach date to Earth."


  - [**Neo - Lookup**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L128)
    - "Look up a specific Asteroid based on its [**NASA JPL small body (SPK-ID) ID**](http://ssd.jpl.nasa.gov/sbdb_query.cgi)"


  - [**Neo - Browse**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L151)
    - "Browse the overall Asteroid data-set"

### [**Space Weather Database Of Notifications, Knowledge, Information**](https://ccmc.gsfc.nasa.gov/tools/DONKI) (DONKI)

"The Space Weather Database Of
Notifications, Knowledge, Information (DONKI) is
a comprehensive on-line tool for
space weather forecasters, scientists, and
the general space science community.
DONKI chronicles the daily interpretations
of space weather observations, analysis,
models, forecasts, and notifications provided
by the Space Weather Research
Center (SWRC), comprehensive knowledge-base search
functionality to support anomaly resolution
and space science research, intelligent
linkages, relationships, cause-and-effects between space
weather activities and comprehensive webservice
API access to information stored
in DONKI."

  - [**Coronal Mass Ejection**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L172) (CME)
    - Retrieves basic DONKI Coronal Mass Injection analyses (CMEs)
    within a specific time frame!


  - [**Coronal Mass Ejection Analysis**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L208)
    - Retrieves more robust analyses from DONKI Coronal Mass Injections (CMEs)
    within a specific time frame, accuracy, catalog, and/or keyword!
  

  - [**Geomagnetic Storm**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L284) (GST)
    - Retrieves DONKI Geomagnetic Storm analyses (GSTs)
    within a specific time frame!


  - [**Interplanetary Shock**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L320) (IPS)
    - Retrieves DONKI Interplanetary Shock analyses (IPSs)
    within a specific time frame, location, and/or catalog!


  - [**Solar Flare**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L370) (FLR)
    - Retrieves DONKI Solar Flare analyses (FLRs)
    within a specific time frame!


  - [**Solar Energetic Particle**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L406) (SEP)
    - Retrieves DONKI Solar Energetic Particle analyses (SEP)
    within a specific time frame!


  - [**Magnetopause Crossing**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L442) (MCP)
    - Retrieves DONKI Magnetopause Crossing analyses (MPC)
    within a specific time frame!


  - [**Radiation Belt Enhancement**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L478) (RBE)
    - Retrieves DONKI Radiation Belt Enhancement analyses (RBE)
    within a specific time frame!


  - [**Hight Speed Stream**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L514) (HSS)
    - Retrieves DONKI Hight Speed Stream analyses (HSS)
    within a specific time frame!


  - [**WSA+EnlilSimulation**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L550)
    - Retrieves DONKI WSA+EnlilSimulation analyses
    within a specific time frame!


  - [**Notifications**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L586)
    - Retrieve DONKI Notifications within a specific time frame
    and/or a notification type!

### [**The Earth Observatory Natural Event Tracker**](https://earthobservatory.nasa.gov) (EONET)

"The Earth Observatory Natural Event
Tracker (EONET) is a prototype
web service with the goal
of:

providing a curated source of
continuously updated natural event metadata;
providing a service that links
those natural events to thematically-related
web service-enabled image sources (e.g., via WMS, WMTS, etc.)."

  - [**Events**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L630)
    - Retrieve Earth Observatory Natural Event Tracker (EONET)
    events with up to eleven optional parameters. Such as: Source,
    category, status, limit, days, time frame, magnitude IDs
    and values, and a bounding box!


  - [**Events GeoJSON**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L737)
    - Retrieve Earth Observatory Natural Event Tracker (EONET)
    GeoJSON events with up to eleven optional parameters. Such as:
    Source, category, status, limit, days, time frame, magnitude IDs
    and values, and a bounding box!


  - [**Categories**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L844)
    - "Categories are the types of events by which individual
    events are cataloged. Categories can be used to filter
    the output of the Categories API and the Layers API.
    The acceptable categories can be accessed via the [**categories JSON**](https://eonet.gsfc.nasa.gov/api/v3/categories)."


  - [**Layers**](https://github.com/Py-Kat/py-space-api/blob/d2e1f2e4bef5e9aef19d35876546a359ee38f0d9/pyspaceapi/nasa.py#L919)
    - "A Layer is a reference to a specific web service
      (e.g., WMS, WMTS) that can be used to produce imagery
      of a particular NASA data parameter. Layers are mapped
      to categories within EONET to provide a category-specific
      list of layers (e.g., the ‘Volcanoes’ category is mapped
      to layers that can provide imagery in true color, SO2,
      aerosols, etc.). Web services come in a variety of flavors,
      so it is not possible to include all of the necessary metadata
      here that is required to construct a properly-formulated request
      (URL). The full list of layers can be accessed via the [**layers JSON**](https://eonet.gsfc.nasa.gov/api/v3/layers)."

## | Installing The Package:

This package can be installed
directly from PyPI, or installed
manually via the .tar.gz or
.whl files!

As well, dependencies can be
viewed on [**Line #8 in
'pyproject.toml'**](pyproject.toml).

The PyPI project can also
be viewed by clicking this
link: https://pypi.org/project/pyspaceapis

> ### ⚠️
> 
> Due to a conflict with
> an apparent non-existent package on
> PyPI, the name used for
> installation is *slightly* different than
> the one used when importing.
> Please be sure to correctly
> install `pyspaceapis`. The exact commands
> for installation can be copied
> below!

### Default Installation Method:

```
shell

pip install pyspaceapis
```

---

### Manual Installation Methods:

Using the .whl:
```
shell

pip install "PATH\TO\pyspaceapis-0.4.0-py3-none-any.whl"
```

Using the .tar.gz:
```
shell

pip install "PATH\TO\pyspaceapis-0.4.0.tar.gz"
```

*The .tar.gz and .whl files
will be made available as
well alongside each release for
those who prefer a manual
installation!*

## | Using The Package:

As noted above, this wrapper
is very much so in
the early stages and supports
just 19 NASA API endpoints
at the moment. However, I
am working to constantly and
consistently add more!

All methods currently return a
python dict. This will be
changed if it is found
to be a problem, or
an annoyance for users. However,
I have not found a
reason to do so yet.

To access these, input your
NASA API key or leave
the parameter empty to use
the NASA Demo Key.

```
python

from pyspaceapi import NASAClient


# This uses the Demo Key by default
client = NASAClient()
```

After this, you are ready
to make requests to the
NASA endpoints!

### Example API Request:

*This program will search the
NASA Near Earth Object Web
Service (NeoWs) endpoint and return
a python dict containing the
data of a single specified
asteroid ID!*

```
python

from pyspaceapi import NASAClient


# Replace 'DEMO_KEY' if you plan to use your own NASA API key!
client = NASAClient("DEMO_KEY")

# Search for a specified asteroid ID
data = client.neows_lookup(2001980)
print(data)
```

The program will then return
and print a dict containing
the retrieved data!

The output:

```
console

{'links': {'self': 'http://api.nasa.gov/neo/rest/v1/neo/2001980?api_key=DEMO_KEY'}, 'id': '2001980', 'neo_reference_id': '2001980', 'name': '1980 Tezcatlipoca (1950 LA)', 'name_limited': 'Tezcatlipoca', 'designation': '1980', 'nasa_jpl_url': 'https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=2001980', 'absolute_magnitude_h': 13.81, 'estimated_diameter': {'kilometers': {'estimated_diameter_min': 4.5978518828, 'estimated_diameter_max': 10.2811093604}, 'meters': {'estimated_diameter_min': 4597.8518827937, 'estimated_diameter_max': 10281.1093604022}, 'miles': {'estimated_diameter_min': 2.8569718223, 'estimated_diameter_max': 6.3883832044}, 'feet': {'estimated_diameter_min': 15084.816371145, 'estimated_diameter_max': 33730.6748339819}}, 'is_potentially_hazardous_asteroid': False, 'close_approach_data': [], 'orbital_data': {'orbit_id': '921', 'orbit_determination_date': '2025-05-29 06:22:26', 'first_observation_date': '1950-06-19', 'last_observation_date': '2025-05-27', 'data_arc_in_days': 27371, 'observations_used': 8203, 'orbit_uncertainty': '0', 'minimum_orbit_intersection': '.245041', 'jupiter_tisserand_invariant': '3.996', 'epoch_osculation': '2461000.5', 'eccentricity': '.3647058342921514', 'semi_major_axis': '1.709394204644144', 'inclination': '26.86993780988122', 'ascending_node_longitude': '246.5426397033398', 'orbital_period': '816.3225014335094', 'perihelion_distance': '1.085968165105233', 'perihelion_argument': '115.4724980863188', 'aphelion_distance': '2.332820244183056', 'perihelion_time': '2461337.243438208260', 'mean_anomaly': '211.4954107695293', 'mean_motion': '.4410021766738259', 'equinox': 'J2000', 'orbit_class': {'orbit_class_type': 'AMO', 'orbit_class_description': 'Near-Earth asteroid orbits similar to that of 1221 Amor', 'orbit_class_range': '1.017 AU < q (perihelion) < 1.3 AU'}}, 'is_sentry_object': False}

```

---

### Timeout Handling:

If a request times out
after the initial default ten-second
timeout window, the wrapper will
retry two times by default,
once for fifteen seconds, and
then lastly, for thirty seconds.
This behavior can be overridden
in multiple ways to hopefully
fit any use case! This
can be done via the
`default_retry_delays` class parameter and further
customized via the `retry_delays` parameter
within each class method!

#### Default Retry Delays:

The `default_retry_delays` parameter will **NOT**
override the behavior of the
separate `retry_delays` parameter within each
class method if `retry_delays` is
specified. This allows for configuration
of the `default_retry_delays` AND the
`retry_delays` parameters at once without
causing conflicts.

Setting default retry delays:

```
python

from pyspaceapi import NASAClient


client = NASAClient(default_retry_delays=[5, 10, 15])
```

This, for example, will cause
the wrapper attempt to request
three times. Once for five
seconds, again for 10 seconds,
and then lastly, for fifteen
seconds. This is set to
[10, 15, 30] by default if not
specified.

#### Retry Delays (Class Method Specific):

Specifying the `retry_delays` parameter **WILL**
override the behavior of the
`default_retry_delays` class parameter, specified or
not. This means that you
can have multiple different requests
with timeout delays differing from
each other AND independent of
the default timeout delays without
causing conflict.

Example using default_retry_delays and retry_delays
simultaneously:

```
python

from pyspaceapi import NASAClient


# Specifies the default retry delays
client = NASAClient(default_retry_delays=[10, 20, 30])


# Will use 'default_retry_delays' since 'retry_delays' is unspecified
eonet_data = client.eonet_events()

# Will use 5, 10, and then 15 seconds
donki_data = client.donki_notifications(retry_delays=[5, 10, 15])

# Will use 2, 5, and then 7.5 seconds
neows_data = client.neows_browse(retry_delays=[2, 5, 7.5])
```

#### Timeout Prints:

Along with the main timeout
handling, I have also included
a `timeout_prints` class parameter, which
when set to True, will
enable the debug timeout prints.
This is set to false
by default.

Enabling the timeout prints:

```
python

from pyspaceapi import NASAClient


client = NASAClient(timeout_print=True)
```

The prints will appear as
such:

```
console

(Request timed out after 10 seconds. Retrying for 15 seconds.)

(Request timed out after 15 seconds. Retrying for 30 seconds.)

```

---

### Retrieving Headers:

There is also a method
of retrieving the HTTP header
data as a dict, containing
the current number of requests
remaining, and the total number
of requests for the API
key in-use via the `get_headers`
class method!

*This counter resets every hour
on a rolling basis!*

Retrieving header data:

```
python

from pyspaceapis import NASAClient


client = NASAClient("DEMO_KEY")

headers = client.get_headers()
print(headers)
```

This, by default with no
specified parameters, will return both
the remaining and total number
of requests as a dict!

This will appear like so:

```
console

{'rate_limit_remaining': '7', 'rate_limit_total': '10'}

```

Whether you only want the
remaining number, or the total
number can also be specified
via the `remaining_amount` and `total_amount`
parameters!

*More specifics about API key
rate limiting and amounts can
be read [**here**](https://api.nasa.gov), under the
"How Do I See My
Current Usage?" section.*

---

### Debug Tools:

Along with the endpoint methods,
I have included another separate
module named: [**`debugtools`**](https://github.com/Py-Kat/py-space-api/blob/1e1725859abd83743531d76eb4d592371f675054/pyspaceapi/debugtools.py) which contains
just one tool for now,
being the [**`time_this`**](https://github.com/Py-Kat/py-space-api/blob/1e1725859abd83743531d76eb4d592371f675054/pyspaceapi/debugtools.py#L5) decorator!

Usage would appear something
like this:

```
python

from pyspaceapi.debugtools import time_this
from time import sleep


@time_this
def do_something():
    sleep(1.7)
    print("Did something!")


do_something()
```

The output:

```
console

Did something!


(Finished in: 1.7000 seconds.)

```

# | Final Notes:

Since this package/wrapper is still
very early, please expect there
to possibly be some bugs
or other weirdness! If anything
of the like is noticed
in which you'd like fixed,
or you have any suggestions,
please be sure to make
a submission in the GitHub
repository, and I will attempt
to make implementations as soon
as possible!

✅ Pull Requests are also welcome!
