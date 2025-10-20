import unittest

import pytest
from slixmpp.exceptions import XMPPError

from conftest import AvatarFixtureMixin
from slixmpp import JID, Iq

from slidge import BaseGateway, BaseSession, GatewayUser, LegacyRoster, LegacyBookmarks, LegacyMUC, LegacyContact
from slidge.core.session import _sessions
from slidge.util.test import SlidgeTest
from slidge.util.types import LegacyUserIdType, LegacyMUCType, MucType


class Gateway(BaseGateway):
    COMPONENT_NAME = "A test"
    GROUPS = True


class Contact(LegacyContact):
    async def update_info(self):
        if self.legacy_id.startswith("group"):
            raise XMPPError()


class Session(BaseSession):
    async def login(self):
        return "YUP"


class Bookmarks(LegacyBookmarks):
    async def fill(self) -> None:
        pass


class MUC(LegacyMUC):
    async def update_info(self):
        if not self.legacy_id.startswith("group"):
            raise XMPPError()
        self.type = MucType.GROUP

@pytest.mark.usefixtures("avatar")
class TestMUCSubject(AvatarFixtureMixin, SlidgeTest):
    plugin = globals()
    xmpp: Gateway

    def setUp(self):
        super().setUp()
        with self.xmpp.store.session() as orm:
            user = GatewayUser(
                jid=JID("romeo@montague.lit/gajim").bare,
                legacy_module_data={"username": "romeo", "city": ""},
                preferences={"sync_avatar": True, "sync_presence": True},
            )
            orm.add(user)
            orm.commit()
        self.run_coro(
            self.xmpp._BaseGateway__dispatcher._on_user_register(
                Iq(sfrom="romeo@montague.lit/gajim")
            )
        )
        welcome = self.next_sent()
        assert welcome["body"]
        stanza = self.next_sent()
        assert "logging in" in stanza["status"].lower(), stanza
        stanza = self.next_sent()
        assert "syncing contacts" in stanza["status"].lower(), stanza
        stanza = self.next_sent()
        assert "syncing groups" in stanza["status"].lower(), stanza
        probe = self.next_sent()
        assert probe.get_type() == "probe"
        stanza = self.next_sent()
        assert "yup" in stanza["status"].lower(), stanza

        self.send(  # language=XML
            """
            <iq type="get"
                to="romeo@montague.lit"
                id="1"
                from="aim.shakespeare.lit">
              <pubsub xmlns="http://jabber.org/protocol/pubsub">
                <items node="urn:xmpp:avatar:metadata" />
              </pubsub>
            </iq>
            """
        )

    @property
    def romeo_session(self) -> Session:
        return BaseSession.get_self_or_unique_subclass().from_jid(
            JID("romeo@montague.lit")
        )

    def test_empty_subject(self):
        muc = self.run_coro(self.romeo_session.bookmarks.by_legacy_id("group"))
        with unittest.mock.patch("uuid.uuid4", return_value="uuid"):
            self.recv(  # language=XML
                f"""
            <presence from="romeo@montague.lit/movim"
                      to="{muc.jid}/nick">
              <x xmlns='http://jabber.org/protocol/muc' />
            </presence>
            """            )
            self.send(  # language=XML
                """
            <presence from="group@aim.shakespeare.lit/romeo"
                      to="romeo@montague.lit/movim">
              <x xmlns="http://jabber.org/protocol/muc#user">
                <item affiliation="member"
                      role="participant"
                      jid="romeo@montague.lit/movim" />
                <status code="210" />
                <status code="110" />
                <status code="100" />
              </x>
              <occupant-id xmlns="urn:xmpp:occupant-id:0"
                           id="slidge-user" />
            </presence>
            """,
            use_values=False)
            self.send(  # language=XML
                """
            <message type="groupchat"
                     from="group@aim.shakespeare.lit"
                     to="romeo@montague.lit/movim">
              <stanza-id xmlns="urn:xmpp:sid:0"
                         id="uuid"
                         by="group@aim.shakespeare.lit" />
              <occupant-id xmlns="urn:xmpp:occupant-id:0"
                           id="room" />
              <subject />
            </message>
            """,
            use_values=False,
            )

    def test_set_thread_subject(self):
        muc: MUC = self.run_coro(self.romeo_session.bookmarks.by_legacy_id("group"))
        muc.add_user_resource("movim")
        with unittest.mock.patch("uuid.uuid4", return_value="uuid"):
            juliet_participant = self.run_coro(muc.get_participant("juliet"))
            juliet_participant.set_thread_subject("legacy-thread-id", "some-subject")
            self.send(  # language=XML
                """
            <message xmlns="jabber:component:accept"
                     type="groupchat"
                     from="group@aim.shakespeare.lit/juliet"
                     to="romeo@montague.lit/movim">
              <stanza-id xmlns="urn:xmpp:sid:0"
                         id="uuid"
                         by="group@aim.shakespeare.lit" />
              <thread>legacy-thread-id</thread>
              <subject>some-subject</subject>
              <occupant-id xmlns="urn:xmpp:occupant-id:0"
                           id="uuid" />
            </message>
            """
            )

    def test_user_set_thread_subject(self):
        muc: MUC = self.run_coro(self.romeo_session.bookmarks.by_legacy_id("group"))
        muc.add_user_resource("movim")
        with unittest.mock.patch("slidge.group.room.LegacyMUC.on_set_subject") as on_set_subject, unittest.mock.patch("slidge.group.room.LegacyMUC.on_set_thread_subject") as on_set_thread_subject:
            self.recv(  # language=XML
                """
            <message xmlns="jabber:component:accept"
                     type="groupchat"
                     from="romeo@montague.lit/movim"
                     to="group@aim.shakespeare.lit">
              <stanza-id xmlns="urn:xmpp:sid:0"
                         id="uuid"
                         by="group@aim.shakespeare.lit" />
              <thread>thread-id</thread>
              <subject>some-subject</subject>
              <occupant-id xmlns="urn:xmpp:occupant-id:0"
                           id="uuid" />
            </message>
            """
            )
            on_set_subject.assert_not_called()
            on_set_thread_subject.assert_awaited_once()
            assert on_set_thread_subject.call_args[0] == ("thread-id", "some-subject")

        with unittest.mock.patch("slidge.group.room.LegacyMUC.on_set_subject") as on_set_subject, unittest.mock.patch("slidge.group.room.LegacyMUC.on_set_thread_subject") as on_set_thread_subject:
            self.recv(  # language=XML
                """
            <message xmlns="jabber:component:accept"
                     type="groupchat"
                     from="romeo@montague.lit/movim"
                     to="group@aim.shakespeare.lit">
              <stanza-id xmlns="urn:xmpp:sid:0"
                         id="uuid"
                         by="group@aim.shakespeare.lit" />
              <thread>thread-id</thread>
              <subject>some-subject</subject>
              <body>some-body</body>
              <occupant-id xmlns="urn:xmpp:occupant-id:0"
                           id="uuid" />
            </message>
            """
            )
            on_set_subject.assert_not_called()
            on_set_thread_subject.assert_not_called()
