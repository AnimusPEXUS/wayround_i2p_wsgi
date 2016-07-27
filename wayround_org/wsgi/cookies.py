
import wayround_org.http.cookies

COOKIE_KEY_NAMES = [
    'HTTP-SET-COOKIE',
    'HTTP-COOKIE'
    ]


class Cookies(wayround_org.http.cookies.Cookies):
    """
    This class should be used with wayround_org WSGI server which
    has been created with multiple_same_name_fields_mode='list'
    """

    def add_from_wsgi_request(self, wsgi_request):
        if 'HTTP-COOKIE' in wsgi_request:
            hc = wsgi_request['HTTP-COOKIE']
            if hc is None:
                pass
            elif isinstance(hc, str):
                self.add_from_str(hc)
            elif isinstance(hc, list):
                for i in hc:
                    self.add_from_str(i)
            else:
                raise Exception(
                    "programming error"
                    )
        return
