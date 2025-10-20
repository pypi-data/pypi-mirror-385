import asyncio
import hashlib
import io
from base64 import b64encode
from contextlib import asynccontextmanager
from http import HTTPStatus
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from slidge.util import SubclassableOnce

SubclassableOnce.TEST_MODE = True


@pytest.fixture
def MockRE():
    class MockRE:
        @staticmethod
        def match(*a, **kw):
            return True

    return MockRE


@pytest.fixture(scope="session")
def avatar_path() -> Path:
    return Path(__file__).parent.parent / "dev" / "assets" / "5x5.png"


@pytest.fixture(scope="class")
def avatar(request, avatar_path):
    img = Image.open(avatar_path)
    with io.BytesIO() as f:
        img.save(f, format="PNG")
        img_bytes = f.getvalue()

    class MockResponse:
        def __init__(self, status):
            self.status = status

        @staticmethod
        async def read():
            return img_bytes

        def raise_for_status(self):
            pass

        headers = {"etag": "etag", "last-modified": "last"}

    @asynccontextmanager
    async def mock_get(url, headers=None):
        if url == "SLOW":
            await asyncio.sleep(1)
        else:
            assert url == "AVATAR_URL"
        if headers and (
            headers.get("If-None-Match") == "etag"
            or headers.get("If-Modified-Since") == "last"
        ):
            yield MockResponse(HTTPStatus.NOT_MODIFIED)
        else:
            yield MockResponse(HTTPStatus.OK)

    request.cls.avatar_path = avatar_path
    request.cls.avatar_image = img
    request.cls.avatar_bytes = img_bytes
    request.cls.avatar_sha1 = hashlib.sha1(img_bytes).hexdigest()
    request.cls.avatar_url = "AVATAR_URL"

    request.cls.avatar_base64 = b64encode(img_bytes).decode("utf-8")
    request.cls.avatar_original_sha1 = hashlib.sha1(avatar_path.read_bytes()).hexdigest()

    with patch("slidge.db.avatar.avatar_cache.http", create=True) as mock:
        mock.get = mock_get
        mock.head = mock_get
        yield request


# just to have typings for the fixture which pycharm does not understand
class AvatarFixtureMixin:
    avatar_path: Path
    avatar_image: Image
    avatar_bytes: bytes
    avatar_sha1: str
    avatar_original_sha1: str
    avatar_url: str
    avatar_base64: str
