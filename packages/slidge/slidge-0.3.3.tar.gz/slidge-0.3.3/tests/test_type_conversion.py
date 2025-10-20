import pytest

from conftest import AvatarFixtureMixin
from slixmpp import JID, Iq

from slidge import BaseGateway, BaseSession, GatewayUser, LegacyRoster, LegacyBookmarks
from slidge.core.session import _sessions
from slidge.util.test import SlidgeTest
from slidge.util.types import LegacyUserIdType


class SomeType:
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    @classmethod
    def from_str(cls, s: str):
        a, b = (int(x) for x in s.split("-"))
        return SomeType(a, b)

    def __str__(self):
        return f"{self.a}-{self.b}"

class Gateway(BaseGateway):
    COMPONENT_NAME = "A test"
    LEGACY_CONTACT_ID_TYPE = SomeType.from_str
    LEGACY_ROOM_ID_TYPE = SomeType.from_str
    GROUPS = True


class Session(BaseSession):
    async def login(self):
        return "YUP"


class Roster(LegacyRoster):
    async def legacy_id_to_jid_username(self, legacy_id: LegacyUserIdType) -> str:
        return f"{legacy_id.a}-{legacy_id.b}"

    async def jid_username_to_legacy_id(self, jid_username: str) -> LegacyUserIdType:
        return SomeType.from_str(jid_username)


class Bookmarks(LegacyBookmarks):
    async def legacy_id_to_jid_username(self, legacy_id: LegacyUserIdType) -> str:
        return f"{legacy_id.a}-{legacy_id.b}"

    async def jid_username_to_legacy_id(self, jid_username: str) -> LegacyUserIdType:
        return SomeType.from_str(jid_username)

    async def fill(self):
        pass

@pytest.mark.usefixtures("avatar")
class TestLegacyTypeConversion(AvatarFixtureMixin, SlidgeTest):
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

    def tearDown(self):
        super().tearDown()
        _sessions.clear()

    @property
    def romeo_session(self) -> Session:
        return BaseSession.get_self_or_unique_subclass().from_jid(
            JID("romeo@montague.lit")
        )

    def test_contact(self):
        contact = self.run_coro(self.romeo_session.contacts.by_legacy_id(SomeType(1, 2)))
        assert contact.legacy_id.a == 1
        assert contact.legacy_id.b == 2

    def test_muc(self):
        muc = self.run_coro(self.romeo_session.bookmarks.by_legacy_id(SomeType(1, 2)))
        assert muc.legacy_id.a == 1
        assert muc.legacy_id.b == 2
