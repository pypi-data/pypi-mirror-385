import logging
import smart_open.utils
from smart_open.s3 import _SeekableRawReader, _get, _unwrap_ioerror, _OUT_OF_RANGE, _initialize_boto3, SinglepartWriter
import io

log = logging.getLogger(__name__)

old_init = _SeekableRawReader.__init__


def _new__init__(self, *args, **kwargs):
    old_init(self, *args, **kwargs)
    self.response = None


def _open_body(self, start=None, stop=None):
    """Open a connection to download the specified range of bytes. Store
    the open file handle in self._body.

    If no range is specified, start defaults to self._position.
    start and stop follow the semantics of the http range header,
    so a stop without a start will read bytes beginning at stop.

    As a side effect, set self._content_length. Set self._position
    to self._content_length if start is past end of file.
    """
    if start is None and stop is None:
        start = self._position
    range_string = smart_open.utils.make_range_string(start, stop)

    try:
        # Optimistically try to fetch the requested content range.
        response = _get(
            self._client,
            self._bucket,
            self._key,
            self._version_id,
            range_string,
        )
    except IOError as ioe:
        # Handle requested content range exceeding content size.
        error_response = _unwrap_ioerror(ioe)
        if error_response is None or error_response.get('Code') != _OUT_OF_RANGE:
            raise
        self._position = self._content_length = int(error_response['ActualObjectSize'])
        self._body = io.BytesIO()
    else:
        #
        # Keep track of how many times boto3's built-in retry mechanism
        # activated.
        #
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html#checking-retry-attempts-in-an-aws-service-response
        #
        log.debug(
            '%s: RetryAttempts: %d',
            self,
            response['ResponseMetadata']['RetryAttempts'],
        )
        units, start, stop, length = smart_open.utils.parse_content_range(response['ContentRange'])
        self._content_length = length
        self._position = start
        self._body = response['Body']
        self.response = response


_SeekableRawReader.__init__ = _new__init__
_SeekableRawReader._open_body = _open_body


def _spw__init__(
        self,
        bucket,
        key,
        client=None,
        client_kwargs=None,
        writebuffer=None):
    _initialize_boto3(self, client, client_kwargs, bucket, key)

    if writebuffer is None:
        self._buf = io.BytesIO()
    else:
        self._buf = writebuffer

    self._total_bytes = 0

    #
    # This member is part of the io.BufferedIOBase interface.
    #
    self.raw = None


SinglepartWriter.__init__ = _spw__init__
