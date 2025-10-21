import requests
from requests.exceptions import HTTPError, ReadTimeout, ConnectTimeout


class NASAClient:

    # APOD, NeoWs, and DONKI Base Url
    _base_nasa_url = "https://api.nasa.gov"
    # EONET Base Url
    _base_eonet_url = "https://eonet.gsfc.nasa.gov/api/v3"

    def __init__(self,
                 api_key: str | None = "DEMO_KEY",
                 default_retry_delays: list[float] | None = None,
                 timeout_print: bool | None = False):
        """
        This is where you enter your NASA API key
        for handling requests made to the NASA API. If
        you do not have an API key, you can generate
        your own by clicking this link: https://api.nasa.gov/#signUp.

        Having your own NASA API key will increase the limit
        of requests to 1000 requests per hour!

        This is also where you can set the 'default_retry_delays' parameter
        for modifying the values of all request timeouts at once if needed.
        These can be further tweaked by using the 'retry_delays' parameter
        within each class method to control the retry delays between specific
        class methods! You can also enable the 'timeout_print' parameter,
        which will toggle on debug prints when timeouts occur if set to True!

        :param api_key: Your NASA API key.
            This defaults to the DEMO_KEY.
            (DEMO_KEY is limited to 30 requests per hour!)

        :param default_retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT retry delays
            in which will be attempted when a timeout occurs. (This is if none are
            specified within a class method parameter itself. e.g. the list [5, 10, 15] will
            cause the wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) Specifying this does NOT override separate retry delays
            set within class method parameters via the 'retry_delays' parameter.
            This defaults to [15, 30, 45]

        :param timeout_print: If this parameter is set to True, timeout
            debug prints will be made visible! (e.g. '(Request timed out
            after 15 seconds. Retrying for 30 seconds.)')
            This defaults to False.
        """

        # Requests Session and API Key
        self._session = requests.Session()
        self._api_key = api_key

        # Default Timeout Retry Delays
        self._default_retry_delays = default_retry_delays or [10, 15, 30]

        # Timeout Print
        if timeout_print:
            self._timeout_print = "(Request timed out after {previous_delay} seconds. Retrying for {delay} seconds.)\n"
        if not timeout_print:
            self._timeout_print = ""

    def get_headers(self,
                    remaining_amount: bool | None = True,
                    total_amount: bool | None = True) -> dict:
        """
         Using this class method, you can retrieve the X-RateLimit
         HTTP headers containing the remaining requests and total
         requests for the current API key in-use within the NASAClient
         class as a dict! If both parameters are unspecified,
         this method will return both headers by default.

         rate_limit_remaining: This is the number of requests remaining
         until the count is reset upon the next hour.

         rate_limit_total: This is the total number of requests allowed
         for the given API key within the hour reset window.

         :param remaining_amount: Whether to retrieve the
            number of remaining requests. This defaults to True.

        :param total_amount: Whether to retrieve the total
            number of requests. This defaults to True.
        """

        if not remaining_amount and not total_amount:
            raise TypeError(
                "Both remaining_amount and total_amount cannot be False."
            )

        response = self._session.get(f"{self._base_nasa_url}/neo/rest/v1/neo/2001980?api_key={self._api_key}")

        remaining = response.headers.get("X-RateLimit-Remaining")
        total = response.headers.get("X-RateLimit-Limit")

        headers = None
        if remaining_amount:
            headers = {
                "rate_limit_remaining": remaining
            }

        if total_amount:
            headers = {
                "rate_limit_total": total
            }

        if remaining_amount and total_amount:
            headers = {
                "rate_limit_remaining": remaining,
                "rate_limit_total": total
            }

        return headers

    # Astronomy Picture of the Day API ( APOD )
    def apod(self,
             date: str | None = None,
             start_date: str | None = None,
             end_date: str | None = None,
             count: int | None = None,
             thumbs: bool | None = None,
             retry_delays: list[float] | None = None) -> dict:
        """
        "This endpoint structures the APOD
        imagery and associated metadata so
        that it can be repurposed
        for other applications!"

        "The full documentation for this
        API can be found in
        the APOD API Github repository:
        https://github.com/nasa/apod-api."

        Date Format: YYYY-MM-DD

        :param date: The date of the APOD image to retrieve.
            This defaults to the current date.

        :param start_date: "The start of a date range,
            when requesting for a range of dates."
            Cannot be used with date.
            This defaults to None.

        :param end_date: "The end of a date range,
            when used with start_date."
            This defaults to the current date.

        :param count: "If this is specified, the chosen
            number of random images will be returned.
            Cannot be used with date or start_date and end_date."
            This defaults to None.

        :param thumbs: "Return the URL of a video thumbnail.
            If an APOD is not a video, this parameter is ignored."
            This defaults to False.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/planetary/apod"
        params = {"api_key": self._api_key}

        if date:
            params["date"] = date
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if count:
            params["count"] = str(count)
        if thumbs:
            params["thumbs"] = str(thumbs)

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    # Near Earth Object Web Service ( NeoWs )
    def neows_feed(self,
                   start_date: str | None = None,
                   end_date: str | None = None,
                   retry_delays: list[float] | None = None) -> dict:
        """
        "Retrieve a list of Asteroids based on their closest approach date to Earth!"

        Date Format: YYYY-MM-DD

        :param start_date: Starting date for the asteroid search.
            This defaults to None.

        :param end_date: Ending date for the asteroid search.
            This defaults to 7 days after start_date.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/neo/rest/v1/feed"
        params = {"api_key": self._api_key}

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def neows_lookup(self,
                     asteroid_id: int,
                     retry_delays: list[float] | None = None) -> dict:
        """
        "Lookup a specific asteroid based on its NASA JPL small body (SPK-ID) ID!"

        Small-Body Database Queries: https://ssd.jpl.nasa.gov/tools/sbdb_query.html

        :param asteroid_id: Asteroid SPK-ID correlates to the NASA JPL small body.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/neo/rest/v1/neo/{asteroid_id}"
        params = {"api_key": self._api_key}

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def neows_browse(self,
                     retry_delays: list[float] | None = None) -> dict:
        """
        "Browse the overall Asteroid data-set!"

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/neo/rest/v1/neo/browse"
        params = {"api_key": self._api_key}

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    # Space Weather Database Of Notifications, Knowledge, Information ( DONKI )
    def donki_cme(self,
                  start_date: str | None = None,
                  end_date: str | None = None,
                  retry_delays: list[float] | None = None) -> dict:
        """
        Retrieves basic DONKI Coronal Mass Injection analyses (CMEs)
        within a specific time frame!

        Date Format: YYYY-MM-DD

        :param start_date: The starting date for the CME search.
            This defaults to 30 days prior to the current UTC date.

        :param end_date: The ending date for the CME search.
            This defaults to the current UTC date.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/DONKI/CME"
        params = {"api_key": self._api_key}

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def donki_cme_analysis(self,
                           start_date: str | None = None,
                           end_date: str | None = None,
                           most_accurate_only: bool = True,
                           complete_entry_only: bool = True,
                           speed: int = 0,
                           half_angle: int = 0,
                           catalog: str | None = None,
                           keyword: str | None = None,
                           retry_delays: list[float] | None = None) -> dict:
        """
        Retrieves more robust analyses from DONKI Coronal Mass Injections (CMEs)
        within a specific time frame, accuracy, catalog, and/or keyword!

        Date Format: YYYY-MM-DD

        :param start_date: The starting date for the CME search.
            This defaults to 30 days prior to the current UTC date.

        :param end_date: The ending date for the CME search.
            This defaults to the current UTC date.

        :param most_accurate_only: Whether or not to only return the CME analysis
            marked as "best fit" for each CME entry.
            This defaults to True.

        :param complete_entry_only: Whether or not to only return CME analyses
            with all required fields being filled.
            This defaults to True.

        :param speed: (Lower Limit) Will only return CME analyses greater than,
            or equal to the chosen speed (Measured in km/s).
            This defaults to 0 (No Filtering).

        :param half_angle: (Lower Limit) Filter the angular half-width of the returned CME's.
            This defaults to 0 (No Filtering).

        :param catalog: The catalog from which to retrieve CME analyses.
            This defaults to ALL catalogs.
            (Choices: SWRC_CATALOG, JANG_ET_AL_CATALOG)

        :param keyword: Filter CME results by specific subsets with a keyword.
            This defaults to None.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/DONKI/CMEAnalysis"
        params = {"api_key": self._api_key}

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if most_accurate_only:
            params["most_accurate_only"] = str(most_accurate_only)
        if complete_entry_only:
            params["complete_entry_only"] = str(complete_entry_only)
        if speed:
            params["speed"] = str(speed)
        if half_angle:
            params["half_angle"] = str(half_angle)
        if catalog:
            params["catalog"] = catalog
        if keyword:
            params["keyword"] = keyword

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def donki_gst(self,
                  start_date: str | None = None,
                  end_date: str | None = None,
                  retry_delays: list[float] | None = None) -> dict:
        """
        Retrieves DONKI Geomagnetic Storm analyses (GSTs)
        within a specific time frame!

        Date Format: YYYY-MM-DD

        :param start_date: The starting date for the GST search.
            This defaults to 30 days prior to the current UTC date.

        :param end_date: The ending date for the GST search.
            This defaults to the current UTC date.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/DONKI/GST"
        params = {"api_key": self._api_key}

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def donki_ips(self,
                  start_date: str | None = None,
                  end_date: str | None = None,
                  location: str | None = None,
                  catalog: str | None = None,
                  retry_delays: list[float] | None = None) -> dict:
        """
        Retrieves DONKI Interplanetary Shock analyses (IPSs)
        within a specific time frame, location, and/or catalog!

        Date Format: YYYY-MM-DD

        :param start_date: The starting date for the IPS search.
            This defaults to 30 days prior to the current UTC date.

        :param end_date: The ending date for the IPS search.
            This defaults to the current UTC date.

        :param location: The location from which to retrieve IPS analyses.
            This defaults to ALL locations.
            (Options: Earth, MESSENGER, STEREO A, STEREO B)

        :param catalog: The catalog from which to retrieve IPS analyses.
            This defaults to ALL catalogs.
            (Options: SWRC_CATALOG, WINSLOW_MESSENGER_ICME_CATALOG)

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/DONKI/IPS"
        params = {"api_key": self._api_key}

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if location:
            params["location"] = location
        if catalog:
            params["catalog"] = catalog

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def donki_flr(self,
                  start_date: str | None = None,
                  end_date: str | None = None,
                  retry_delays: list[float] | None = None) -> dict:
        """
        Retrieves DONKI Solar Flare analyses (FLRs)
        within a specific time frame!

        Date Format: YYYY-MM-DD

        :param start_date: The starting date for the FLR search.
            This defaults to 30 days prior to the current UTC date.

        :param end_date: The ending date for the FLR search.
            This defaults to the current UTC date.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/DONKI/FLR"
        params = {"api_key": self._api_key}

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def donki_sep(self,
                  start_date: str | None = None,
                  end_date: str | None = None,
                  retry_delays: list[float] | None = None) -> dict:
        """
        Retrieves DONKI Solar Energetic Particle analyses (SEP)
        within a specific time frame!

        Date Format: YYYY-MM-DD

        :param start_date: The starting date for the SEP search.
            This defaults to 30 days prior to the current UTC date.

        :param end_date: The ending date for the SEP search.
            This defaults to the current UTC date.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/DONKI/SEP"
        params = {"api_key": self._api_key}

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def donki_mpc(self,
                  start_date: str | None = None,
                  end_date: str | None = None,
                  retry_delays: list[float] | None = None) -> dict:
        """
        Retrieves DONKI Magnetopause Crossing analyses (MPC)
        within a specific time frame!

        Date Format: YYYY-MM-DD

        :param start_date: The starting date for the MPC search.
            This defaults to 30 days prior to the current UTC date.

        :param end_date: The ending date for the MPC search.
            This defaults to the current UTC date.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/DONKI/MPC"
        params = {"api_key": self._api_key}

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def donki_rbe(self,
                  start_date: str | None = None,
                  end_date: str | None = None,
                  retry_delays: list[float] | None = None) -> dict:
        """
        Retrieves DONKI Radiation Belt Enhancement analyses (RBE)
        within a specific time frame!

        Date Format: YYYY-MM-DD

        :param start_date: The starting date for the RBE search.
            This defaults to 30 days prior to the current UTC date.

        :param end_date: The ending date for the RBE search.
            This defaults to the current UTC date.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/DONKI/RBE"
        params = {"api_key": self._api_key}

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def donki_hss(self,
                  start_date: str | None = None,
                  end_date: str | None = None,
                  retry_delays: list[float] | None = None) -> dict:
        """
        Retrieves DONKI Hight Speed Stream analyses (HSS)
        within a specific time frame!

        Date Format: YYYY-MM-DD

        :param start_date: The starting date for the HSS search.
            This defaults to 30 days prior to the current UTC date.

        :param end_date: The ending date for the HSS search.
            This defaults to the current UTC date.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/DONKI/HSS"
        params = {"api_key": self._api_key}

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def donki_wsa_es(self,
                     start_date: str | None = None,
                     end_date: str | None = None,
                     retry_delays: list[float] | None = None) -> dict:
        """
        Retrieves DONKI WSA+EnlilSimulation analyses
        within a specific time frame!

        Date Format: YYYY-MM-DD

        :param start_date: The starting date for the WSA+EnlilSimulation search.
            This defaults to 7 days prior to the current UTC date.

        :param end_date: The ending date for the WSA+EnlilSimulation search.
            This defaults to the current UTC date.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/DONKI/WSAEnlilSimulations"
        params = {"api_key": self._api_key}

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def donki_notifications(self,
                            start_date: str | None = None,
                            end_date: str | None = None,
                            notification_type: str | None = None,
                            retry_delays: list[float] | None = None) -> dict:
        """
        Retrieve DONKI Notifications within a specific time frame
        and/or a notification type!

        Date Format: YYYY-MM-DD

        :param start_date: The starting date for the DONKI Notifications search.
            This defaults to 7 days prior to the current UTC date.

        :param end_date: The ending date for the DONKI Notifications search.
            This defaults to the current UTC date.

        :param notification_type: The notification type to retrieve.
            This defaults to ALL notification types.
            (Options: FLR, SEP, CME, IPS, MPC, GST, RBE, report)

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_nasa_url}/DONKI/notifications"
        params = {"api_key": self._api_key}

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if notification_type:
            params["type"] = notification_type

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    # The Earth Observatory Natural Event Tracker (EONET)
    def eonet_events(self,
                     source: str | None = None,
                     category: str | None = None,
                     status: str | None = None,
                     limit: int | None = None,
                     days: int | None = None,
                     start_date: str | None = None,
                     end_date: str | None = None,
                     mag_id: str | None = None,
                     mag_min: float | None = None,
                     mag_max: float | None = None,
                     bounding_box: list[float] | None = None,
                     retry_delays: list[float] | None = None) -> dict:
        """
        Retrieve Earth Observatory Natural Event Tracker (EONET)
        events with up to eleven optional parameters. Such as: Source,
        category, status, limit, days, time frame, magnitude IDs
        and values, and a bounding box!

        Date Format: YYYY-MM-DD

        :param source: Filter the returned events by the Source.
            Multiple sources can be included in the parameter:
            comma separated, operates as a boolean "OR".
            Event sources can be found here:
            https://eonet.gsfc.nasa.gov/api/v3/sources.
            This defaults to None.

        :param category: Filter the returned events by the category.
            Multiple sources can be included in the parameter:
            comma separated, operates as a boolean OR.
            The acceptable categories can be accessed via the categories JSON:
            https://eonet.gsfc.nasa.gov/api/v3/categories.
            This defaults to None.

        :param status: Events that have ended are assigned a closed date
            and the existence of that date will allow you to filter for
            only-open or only-closed events. Omitting the status parameter
            will return only the currently open events (default). Using
            “all“ will list open and closed values.
            This can be "open", "closed" or "all".
            This defaults to None.

        :param limit: Limits the number of events returned.
            This defaults to None.

        :param days: Limit the number of prior days (including today)
            from which events will be returned.
            This defaults to None.

        :param start_date: The starting date for the events to fall between.
            This defaults to None.

        :param end_date: The ending date for the events to fall between.
            This defaults to None.

        :param mag_id: The ID of the magnitude in which to search for.
            This defaults to None.

        :param mag_min: The floor (minimum) magnitude value in which to search for.
            This defaults to None.

        :param mag_max: The ceiling (maximum) magnitude value in which to search for.
            This defaults to None.

        :param bounding_box: Query using a bounding box for all events with datapoints
            that fall within. This uses two pairs of coordinates: min lon, max lat, max lon, min lat.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_eonet_url}/events"
        params = {}

        if source:
            params["source"] = source
        if category:
            params["category"] = category
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        if days:
            params["days"] = days
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date
        if mag_id:
            params["magID"] = mag_id
        if mag_min:
            params["magMin"] = mag_min
        if mag_max:
            params["magMax"] = mag_max
        if bounding_box:
            values = ",".join(map(str, bounding_box))
            params["bbox"] = values

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def eonet_events_geojson(self,
                             source: str | None = None,
                             category: str | None = None,
                             status: str | None = None,
                             limit: int | None = None,
                             days: int | None = None,
                             start_date: str | None = None,
                             end_date: str | None = None,
                             mag_id: str | None = None,
                             mag_min: float | None = None,
                             mag_max: float | None = None,
                             bounding_box: list[float] | None = None,
                             retry_delays: list[float] | None = None) -> dict:
        """
        Retrieve Earth Observatory Natural Event Tracker (EONET)
        GeoJSON events with up to eleven optional parameters. Such as:
        Source, category, status, limit, days, time frame, magnitude IDs
        and values, and a bounding box!

        Date Format: YYYY-MM-DD

        :param source: Filter the returned events by the Source.
            Multiple sources can be included in the parameter:
            comma separated, operates as a boolean "OR".
            Event sources can be found here:
            https://eonet.gsfc.nasa.gov/api/v3/sources.
            This defaults to None.

        :param category: Filter the returned events by the category.
            Multiple sources can be included in the parameter:
            comma separated, operates as a boolean OR.
            The acceptable categories can be accessed via the categories JSON:
            https://eonet.gsfc.nasa.gov/api/v3/categories.
            This defaults to None.

        :param status: Events that have ended are assigned a closed date
            and the existence of that date will allow you to filter for
            only-open or only-closed events. Omitting the status parameter
            will return only the currently open events (default). Using
            “all“ will list open and closed values.
            This can be "open", "closed" or "all".
            This defaults to None.

        :param limit: Limits the number of events returned.
            This defaults to None.

        :param days: Limit the number of prior days (including today)
            from which events will be returned.
            This defaults to None.

        :param start_date: The starting date for the events to fall between.
            This defaults to None.

        :param end_date: The ending date for the events to fall between.
            This defaults to None.

        :param mag_id: The ID of the magnitude in which to search for.
            This defaults to None.

        :param mag_min: The floor (minimum) magnitude value in which to search for.
            This defaults to None.

        :param mag_max: The ceiling (maximum) magnitude value in which to search for.
            This defaults to None.

        :param bounding_box: Query using a bounding box for all events with datapoints
            that fall within. This uses two pairs of coordinates: min lon, max lat, max lon, min lat.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_eonet_url}/events"
        params = {}

        if source:
            params["source"] = source
        if category:
            params["category"] = category
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        if days:
            params["days"] = days
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date
        if mag_id:
            params["magID"] = mag_id
        if mag_min:
            params["magMin"] = mag_min
        if mag_max:
            params["magMax"] = mag_max
        if bounding_box:
            values = ",".join(map(str, bounding_box))
            params["bbox"] = values

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def eonet_categories(self,
                         category: str | None = None,
                         source: str | None = None,
                         status: str | None = None,
                         limit: int | None = None,
                         days: int | None = None,
                         start_date: str | None = None,
                         end_date: str | None = None,
                         retry_delays: list[float] | None = None) -> dict:
        """
        "Categories are the types of events by which individual
        events are cataloged. Categories can be used to filter
        the output of the Categories API and the Layers API.
        The acceptable categories can be accessed via the categories JSON:
        https://eonet.gsfc.nasa.gov/api/v3/categories."

        Date Format: YYYY-MM-DD

        :param category: "Filter the returned events by the category."
            This defaults to None.

        :param source: "Filter the topically-constrained events by the Source.
            Multiple sources can be included in the parameter: comma separated,
            operates as a boolean "OR"."

        :param status: "Events that have ended are assigned a closed date
            and the existence of that date will allow you to filter
            for only-open or only-closed events. Omitting the status parameter
            will return only the currently open events."
            This can be "open", or "closed".
            This defaults to None.

        :param limit: "Limits the number of events returned."
            This defaults to None.

        :param days: "Limit the number of prior days (including today)"
            from which events will be returned.
            This defaults to None.

        :param start_date: The starting date for the categories to fall between.
            This defaults to None.

        :param end_date: The ending date for the categories to fall between.
            This defaults to None.

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_eonet_url}/categories"
        params = {}

        if category:
            url = f"{self._base_eonet_url}/categories/{category}"
        if source:
            params["source"] = source
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        if days:
            params["days"] = days
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, params=params, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error

    def eonet_layers(self,
                     category: str,
                     retry_delays: list[float] | None = None) -> dict:
        """
        "A Layer is a reference to a specific web service
        (e.g., WMS, WMTS) that can be used to produce imagery
        of a particular NASA data parameter. Layers are mapped
        to categories within EONET to provide a category-specific
        list of layers (e.g., the ‘Volcanoes’ category is mapped
        to layers that can provide imagery in true color, SO2,
        aerosols, etc.). Web services come in a variety of flavors,
        so it is not possible to include all of the necessary metadata
        here that is required to construct a properly-formulated request
        (URL). The full list of layers can be accessed via the layers JSON:
        https://eonet.gsfc.nasa.gov/api/v3/layers."

        :param category: "Filter the returned layers by the category.
            The acceptable categories can be accessed via the categories JSON:
            https://eonet.gsfc.nasa.gov/api/v3/categories."

        :param retry_delays: This parameter can be specified
            with a list of floats/integers to override the DEFAULT timeout
            retry delays in which will be attempted if a timeout occurs.
            This will also override the main 'default_retry_delays'
            parameter if specified as well, allowing for further customization
            between API requests! (e.g. the list [5, 10, 15] will cause the
            wrapper to try three times, once for five seconds, once again for
            ten seconds, etc.) This defaults to [10, 15, 30]
        """

        url = f"{self._base_eonet_url}/layers/{category}"

        timing_out = False
        previous_delay = None
        timeout_error = None

        for delay in retry_delays or self._default_retry_delays:
            if timing_out:
                print(
                    self._timeout_print.format(previous_delay=previous_delay, delay=delay)
                )

            try:
                response = self._session.get(url, timeout=delay)
                response.raise_for_status()

                return response.json()

            except (ConnectTimeout,
                    ReadTimeout) as e:
                timing_out = True
                previous_delay = delay

                if ConnectTimeout:
                    timeout_error = ConnectTimeout(
                        f"{e}"
                    )
                if ReadTimeout:
                    timeout_error = ReadTimeout(
                        f"{e}"
                    )

            except HTTPError:
                raise

        else:
            raise timeout_error
