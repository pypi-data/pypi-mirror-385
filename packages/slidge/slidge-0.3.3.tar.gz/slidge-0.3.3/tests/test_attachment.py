import asyncio
import os
import shutil
import tempfile
import unittest
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

import pytest
from conftest import AvatarFixtureMixin
from test_shakespeare import Base as Shakespeare

from slidge.core import config
from slidge.util.types import LegacyAttachment, MessageReference


@pytest.fixture(scope="function")
def attachment(request, avatar_path):
    class MockHeadResponse:
        status = 200

    class MockGetResponse:
        @staticmethod
        def raise_for_status():
            pass

        @staticmethod
        async def read():
            return avatar_path.read_bytes()

    class MockAioHTTP:
        @asynccontextmanager
        async def head(*a, **k):
            yield MockHeadResponse

        @asynccontextmanager
        async def get(*a, **k):
            yield MockGetResponse

    with (
        patch(
            "slixmpp.plugins.xep_0363.http_upload.XEP_0363.upload_file",
            return_value="http://url",
        ) as http_upload,
        patch("aiohttp.ClientSession", return_value=MockAioHTTP) as client_session,
        patch("slidge.core.mixins.attachment.uuid4", return_value="uuid"),
    ):
        request.cls.head = client_session.head = MockAioHTTP.head
        request.cls.http_upload = http_upload
        yield


@pytest.mark.usefixtures("avatar")
@pytest.mark.usefixtures("attachment")
class Base(Shakespeare, AvatarFixtureMixin):
    http_upload: MagicMock

    def _assert_body(self, text="body", i=None):
        if i:
            self.send(  # language=XML
                f"""
            <message type="chat"
                     from="juliet@aim.shakespeare.lit/slidge"
                     to="romeo@montague.lit"
                     id="{i}">
              <body>{text}</body>
              <active xmlns="http://jabber.org/protocol/chatstates" />
              <markable xmlns="urn:xmpp:chat-markers:0" />
              <store xmlns="urn:xmpp:hints" />
            </message>
            """,
                use_values=False,
            )
        else:
            self.send(  # language=XML
                f"""
            <message type="chat"
                     from="juliet@aim.shakespeare.lit/slidge"
                     to="romeo@montague.lit">
              <body>{text}</body>
              <active xmlns="http://jabber.org/protocol/chatstates" />
              <markable xmlns="urn:xmpp:chat-markers:0" />
              <store xmlns="urn:xmpp:hints" />
            </message>
            """,
                use_values=False,
            )

    def _assert_file(self, url="http://url", disposition: str = '', local_path: Path | None = None):
        when = (
            datetime.fromtimestamp((local_path or self.avatar_path).stat().st_mtime)
            .isoformat()
            .replace("+00:00", "Z")
        )
        if disposition:
            el = f"disposition='{disposition}'"
        else:
            el = ""
        self.send(  # language=XML
            f"""<message type="chat"
                     from="juliet@aim.shakespeare.lit/slidge"
                     to="romeo@montague.lit">
              <reference xmlns="urn:xmpp:reference:0"
                         type="data">
                <media-sharing xmlns="urn:xmpp:sims:1">
                  <sources>
                    <reference xmlns="urn:xmpp:reference:0"
                               uri="{url}"
                               type="data" />
                  </sources>
                  <file xmlns="urn:xmpp:jingle:apps:file-transfer:5">
                    <media-type>image/png</media-type>
                    <name>5x5.png</name>
                    <size>547</size>
                    <date>{when}</date>
                    <hash xmlns="urn:xmpp:hashes:2"
                          algo="sha-256">NdpqDQuHlshve2c0iU25l2KI4cjpoyzaTk3a/CdbjPQ=</hash>
                    <thumbnail xmlns="urn:xmpp:thumbs:1"
                               width="5"
                               height="5"
                               media-type="image/thumbhash"
                               uri="data:image/thumbhash;base64,AAgCBwAAAAAAAAAAAAAAAAAAAAAAAAAA" />
                  </file>
                </media-sharing>
              </reference>
              <file-sharing xmlns="urn:xmpp:sfs:0" {el}>
                <sources>
                  <url-data xmlns="http://jabber.org/protocol/url-data"
                            target="{url}" />
                </sources>
                <file xmlns="urn:xmpp:file:metadata:0">
                  <media-type>image/png</media-type>
                  <name>5x5.png</name>
                  <size>547</size>
                  <date>{when}</date>
                  <hash xmlns="urn:xmpp:hashes:2"
                        algo="sha-256">NdpqDQuHlshve2c0iU25l2KI4cjpoyzaTk3a/CdbjPQ=</hash>
                  <thumbnail xmlns="urn:xmpp:thumbs:1"
                             width="5"
                             height="5"
                             media-type="image/thumbhash"
                             uri="data:image/thumbhash;base64,AAgCBwAAAAAAAAAAAAAAAAAAAAAAAAAA" />
                </file>
              </file-sharing>
              <x xmlns="jabber:x:oob">
                <url>{url}</url>
              </x>
              <body>{url}</body>
              <fallback xmlns="urn:xmpp:fallback:0" for="urn:xmpp:sfs:0">
                <body/>
              </fallback>
            </message>
            """,
            use_values=False,
        )


class TestBodyOnly(Base):
    def test_no_file_no_body(self):
        self.run_coro(self.juliet.send_files([]))
        assert self.next_sent() is None

    def test_just_body(self):
        self.run_coro(self.juliet.send_files([], body="body"))
        self._assert_body()
        self.run_coro(self.juliet.send_files([], body="body", body_first=True))
        self._assert_body()
        self.run_coro(self.juliet.send_files([], body="body", legacy_msg_id=12))
        self._assert_body(i=12)


class TestAttachmentUpload(Base):
    def __test_basic(self, attachment: LegacyAttachment, upload_kwargs: dict, disposition: str = ''):
        """
        Basic test that file is uploaded.
        """
        self.run_coro(self.juliet.send_files([attachment]))
        self.http_upload.assert_called_with(**upload_kwargs)
        self._assert_file(disposition=disposition)

    def _test_reuse(self, attachment: LegacyAttachment, upload_kwargs: dict):
        """
        Basic test the no new file is uploaded when the same attachment is used
        twice.
        """
        self.run_coro(self.juliet.send_files([attachment]))
        self.http_upload.assert_called_with(**upload_kwargs)
        self._assert_file()
        self.http_upload.reset_mock()
        self.run_coro(self.juliet.send_files([attachment]))
        self.http_upload.assert_not_called()
        self._assert_file()

    def test_path(self):
        self.__test_basic(
            LegacyAttachment(path=self.avatar_path),
            dict(
                filename=self.avatar_path,
                content_type="image/png",
                ifrom=self.xmpp.boundjid,
                domain=None,
            ),
        )

    def test_path_attachment(self):
        self.__test_basic(
            LegacyAttachment(path=self.avatar_path, disposition="attachment"),
            dict(
                filename=self.avatar_path,
                content_type="image/png",
                ifrom=self.xmpp.boundjid,
                domain=None,
            ),
            "attachment",
        )

    def test_thumbhash(self):
        self.__test_basic(
            LegacyAttachment(path=self.avatar_path, content_type="image/png"),
            dict(
                filename=self.avatar_path,
                content_type="image/png",
                ifrom=self.xmpp.boundjid,
                domain=None,
            ),
        )

    def test_path_and_id(self):
        self._test_reuse(
            LegacyAttachment(path=self.avatar_path, legacy_file_id=1235),
            dict(
                filename=self.avatar_path,
                content_type="image/png",
                ifrom=self.xmpp.boundjid,
                domain=None,
            ),
        )

    def test_bytes(self):
        with patch("pathlib.Path.stat", return_value=os.stat(self.avatar_path)):
            self.__test_basic(
                LegacyAttachment(data=self.avatar_path.read_bytes(), name="5x5.png"),
                dict(
                    filename=ANY,
                    content_type="image/png",
                    ifrom=self.xmpp.boundjid,
                    domain=None,
                ),
            )

    def test_bytes_and_id(self):
        with patch("pathlib.Path.stat", return_value=os.stat(self.avatar_path)):
            self._test_reuse(
                LegacyAttachment(
                    data=self.avatar_path.read_bytes(),
                    legacy_file_id=123,
                    name="5x5.png",
                ),
                dict(
                    filename=ANY,
                    content_type="image/png",
                    ifrom=self.xmpp.boundjid,
                    domain=None,
                ),
            )

    def test_race_condition(self):
        async def stream(t):
            await asyncio.sleep(t)
            for _ in range(10):
                yield b"e"

        self.run_coro(
            asyncio.gather(
                self.juliet.send_file(LegacyAttachment(aio_stream=stream(0.1), legacy_file_id=123)),
                self.juliet.send_file(LegacyAttachment(aio_stream=stream(0.5), legacy_file_id=123)),
            )
        )
        _msg1 = self.next_sent()
        _msg2 = self.next_sent()
        assert self.next_sent() is None

class TestAttachmentNoUpload(Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config.NO_UPLOAD_URL_PREFIX = "https://url"

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        config.NO_UPLOAD_PATH = None
        config.NO_UPLOAD_URL_PREFIX = None

    def setUp(self):
        super().setUp()
        config.NO_UPLOAD_PATH = tempfile.TemporaryDirectory().name

    def tearDown(self):
        super().tearDown()
        try:
            shutil.rmtree(config.NO_UPLOAD_PATH)
        except FileNotFoundError:
            pass

    def __test_basic(self, attachment: LegacyAttachment, url: str, local_path: Path | None = None):
        """
        Basic test that file is copied.
        """
        self.run_coro(self.juliet.send_files([attachment]))
        self._assert_file(url=url, local_path=local_path)

    def __test_reuse(self, attachment: LegacyAttachment, url: str):
        """
        Basic test the no new file is copied when the same attachment is used
        twice.
        """
        self.run_coro(self.juliet.send_files([attachment]))
        self._assert_file(url=url)
        self.run_coro(self.juliet.send_files([attachment]))
        self._assert_file(url=url)

    def test_path(self):
        self.__test_basic(
            LegacyAttachment(path=self.avatar_path), "https://url/uuid/uuid/5x5.png"
        )

    def test_path_and_id(self):
        self.__test_reuse(
            LegacyAttachment(path=self.avatar_path, legacy_file_id=1234),
            "https://url/1234/uuid/5x5.png",
        )

    def test_multi(self):
        self.xmpp.LEGACY_MSG_ID_TYPE = int
        self.xmpp.use_message_ids = True
        self.run_coro(
            self.juliet.send_files(
                [
                    LegacyAttachment(path=self.avatar_path),
                    LegacyAttachment(path=self.avatar_path, caption="CAPTION"),
                ],
                legacy_msg_id=6666,
                body="BODY",
            )
        )
        xmpp_ids = []
        for _ in range(2):
            att = self.next_sent()
            xmpp_ids.append(att.get_id())
        caption = self.next_sent()
        assert caption["body"] == "CAPTION"
        xmpp_ids.append(caption.get_id())
        body = self.next_sent()
        assert body["body"] == "BODY"
        xmpp_ids.append(body.get_id())
        assert self.next_sent() is None
        assert len(set(xmpp_ids)) == len(xmpp_ids)
        self.juliet.react(6666, "♥")
        reaction = self.next_sent()
        assert reaction["reactions"]["id"] in xmpp_ids

        self.recv(  # language=XML
            """
            <message to="aim.shakespeare.lit"
                     from="montague.lit">
              <privilege xmlns="urn:xmpp:privilege:2">
                <perm access="roster"
                      type="both" />
                <perm access="message"
                      type="outgoing" />
              </privilege>
            </message>
            """
        )
        for i in xmpp_ids:
            with patch("test_shakespeare.Session.on_react") as mock:
                self.recv(  # language=XML
                    f"""
            <message from="romeo@montague.lit/gajim"
                     to="juliet@{self.xmpp.boundjid.bare}/slidge">
              <reactions id='{i}'
                         xmlns='urn:xmpp:reactions:0'>
                <reaction>👋</reaction>
                <reaction>🐢</reaction>
              </reactions>
            </message>
            """
                )
            for j in [k for k in xmpp_ids if k != i]:
                reac = self.next_sent()
                assert reac["privilege"]["forwarded"]["message"]["reactions"]["id"] == j

            mock.assert_awaited_once()
            assert mock.call_args[0][0].jid == self.juliet.jid
            assert mock.call_args[0][1] == 6666
            assert mock.call_args[0][2] == ["👋", "🐢"]
            assert mock.call_args[1] == dict(thread=None)
        self.xmpp.use_message_ids = False
        self.xmpp.LEGACY_MSG_ID_TYPE = True

    def test_multi_moderation(self):
        session = self.get_romeo_session()
        muc = self.run_coro(session.bookmarks.by_legacy_id("room"))
        muc.add_user_resource("gajim")
        part = muc.get_system_participant()
        self.run_coro(
            part.send_files(
                [
                    LegacyAttachment(path=self.avatar_path),
                    LegacyAttachment(path=self.avatar_path, caption="CAPTION"),
                ],
                legacy_msg_id="the-real-msg-id",
                body="BODY",
            )
        )
        stanza_ids = []
        while (stanza := self.next_sent()) is not None:
            stanza_ids.append(stanza["stanza_id"]["id"])
        assert len(stanza_ids) == 4  # 2 attachments, the caption and the body
        assert "the-real-msg-id" in stanza_ids

        part.moderate("the-real-msg-id")

        moderated_ids = []
        while (stanza := self.next_sent()) is not None:
            moderated_ids.append(stanza["retract"]["id"])
        assert set(stanza_ids) == set(moderated_ids)

    def test_reply_with_attachment(self):
        self.run_coro(
            self.juliet.send_files(
                [
                    LegacyAttachment(path=self.avatar_path),
                ],
                reply_to=MessageReference("some_msg_id", body="a body"),
            )
        )
        when = (
            datetime.fromtimestamp(self.avatar_path.stat().st_mtime)
            .isoformat()
            .replace("+00:00", "Z")
        )
        self.send(  # language=XML
            f"""
            <message xmlns="jabber:component:accept"
                     type="chat"
                     from="juliet@aim.shakespeare.lit/slidge"
                     to="romeo@montague.lit">
              <reply xmlns="urn:xmpp:reply:0"
                     id="some_msg_id" />
              <body>https://url/uuid/uuid/5x5.png</body>
              <reference xmlns="urn:xmpp:reference:0"
                         type="data">
                <media-sharing xmlns="urn:xmpp:sims:1">
                  <sources>
                    <reference xmlns="urn:xmpp:reference:0"
                               uri="https://url/uuid/uuid/5x5.png"
                               type="data" />
                  </sources>
                  <file xmlns="urn:xmpp:jingle:apps:file-transfer:5">
                    <media-type>image/png</media-type>
                    <name>5x5.png</name>
                    <size>547</size>
                    <date>{when}</date>
                    <hash xmlns="urn:xmpp:hashes:2"
                          algo="sha-256">NdpqDQuHlshve2c0iU25l2KI4cjpoyzaTk3a/CdbjPQ=</hash>
                    <thumbnail xmlns="urn:xmpp:thumbs:1"
                               width="5"
                               height="5"
                               media-type="image/thumbhash"
                               uri="data:image/thumbhash;base64,AAgCBwAAAAAAAAAAAAAAAAAAAAAAAAAA" />
                  </file>
                </media-sharing>
              </reference>
              <file-sharing xmlns="urn:xmpp:sfs:0">
                <sources>
                  <url-data xmlns="http://jabber.org/protocol/url-data"
                            target="https://url/uuid/uuid/5x5.png" />
                </sources>
                <file xmlns="urn:xmpp:file:metadata:0">
                  <media-type>image/png</media-type>
                  <name>5x5.png</name>
                  <size>547</size>
                  <date>{when}</date>
                  <hash xmlns="urn:xmpp:hashes:2"
                        algo="sha-256">NdpqDQuHlshve2c0iU25l2KI4cjpoyzaTk3a/CdbjPQ=</hash>
                  <thumbnail xmlns="urn:xmpp:thumbs:1"
                             width="5"
                             height="5"
                             media-type="image/thumbhash"
                             uri="data:image/thumbhash;base64,AAgCBwAAAAAAAAAAAAAAAAAAAAAAAAAA" />
                </file>
              </file-sharing>
              <x xmlns="jabber:x:oob">
                <url>https://url/uuid/uuid/5x5.png</url>
              </x>
              <fallback xmlns="urn:xmpp:fallback:0"
                        for="urn:xmpp:sfs:0">
                <body />
              </fallback>
            </message>
            """,
            use_values=False,
        )

    def test_url(self):
        tmp = tempfile.mkdtemp()

        with unittest.mock.patch("tempfile.mkdtemp", return_value=tmp):
            self.__test_basic(
                LegacyAttachment(url=self.avatar_url, name="5x5.png"),
                url="https://url/uuid/uuid/5x5.png",
                local_path=Path(tmp) / "5x5.png",
            )
        shutil.rmtree(tmp)


class TestAttachmentOriginalUrl(Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config.USE_ATTACHMENT_ORIGINAL_URLS = True


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        config.USE_ATTACHMENT_ORIGINAL_URLS = False

    def __check(self, url, name=None, content_type=None, disposition=None):
        disposition = f"disposition='{disposition}'" if disposition else ""
        # file_sharing = "<file-sharing xmlns='urn:xmpp:sfs:0'" + disposition
        name = f"<name>{name}</name>" if name else ""
        content_type = f"<media-type>{content_type}</media-type>" if content_type else ""

        self.send(  # language=XML
            f"""<message type="chat"
                     from="juliet@aim.shakespeare.lit/slidge"
                     to="romeo@montague.lit">
              <media-sharing xmlns="urn:xmpp:sims:1">
                <sources>
                  <reference xmlns="urn:xmpp:reference:0"
                             uri="{url}"
                             type="data" />
                </sources>
                <file xmlns="urn:xmpp:jingle:apps:file-transfer:5">{content_type} {name}</file>
              </media-sharing>
              <file-sharing xmlns="urn:xmpp:sfs:0" {disposition}>
                <sources>
                  <url-data xmlns="http://jabber.org/protocol/url-data"
                            target="{url}" />
                </sources>
                <file xmlns="urn:xmpp:file:metadata:0">{content_type} {name}</file>
              </file-sharing>
              <x xmlns="jabber:x:oob">
                <url>{url}</url>
              </x>
              <fallback xmlns='urn:xmpp:fallback:0'
                        for='urn:xmpp:sfs:0'>
                <body />
              </fallback>
              <body>{url}</body>
            </message>
            """
        )

    def __check_no_meta(self, url):
        self.send(  # language=XML
            f"""
            <message type="chat"
                     from="juliet@aim.shakespeare.lit/slidge"
                     to="romeo@montague.lit">
              <x xmlns="jabber:x:oob">
                <url>{url}</url>
              </x>
              <body>{url}</body>
            </message>
            """
        )

    def __send_file(self, url, name=None, content_type=None, disposition=None):
        self.run_coro(self.juliet.send_file(
            LegacyAttachment(url=url, name=name, content_type=content_type, disposition=disposition)))

    def test_url_original(self):
        self.__send_file("prout", name="5x5.png", disposition="inline")
        self.__check("prout", name="5x5.png", content_type="image/png", disposition="inline")

        self.__send_file("prout", name="5x5.png", content_type="GNAGNA")
        self.__check("prout", name="5x5.png", content_type="GNAGNA")

        self.__send_file("prout", disposition="inline")
        self.__check("prout", disposition="inline")

        self.__send_file("prout", name="5x5.png")
        self.__check("prout", name="5x5.png", content_type="image/png")

        self.__send_file("prout.png")
        self.__check("prout.png", content_type="image/png")

    def test_no_metadata(self):
        self.__send_file("prout")
        self.__check_no_meta("prout")
