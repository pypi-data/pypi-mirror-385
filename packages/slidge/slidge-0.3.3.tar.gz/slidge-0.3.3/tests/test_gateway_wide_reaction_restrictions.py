from typing import Optional

from slixmpp import JID, Iq

from slidge import BaseGateway, BaseSession, GatewayUser
from slidge.contact import LegacyContact
from slidge.util.test import SlidgeTest
from slidge.util.types import RecipientType, LegacyMessageType, LegacyThreadType


class Gateway(BaseGateway):
    COMPONENT_NAME = "A test"


class Session(BaseSession):
    async def login(self):
        pass

    async def on_react(
        self,
        chat: RecipientType,
        legacy_msg_id: LegacyMessageType,
        emojis: list[str],
        thread: Optional[LegacyThreadType] = None,
    ):
        pass

class Contact(LegacyContact):
    REACTIONS_SINGLE_EMOJI = True


class TestGatewayWideRestrictions(SlidgeTest):
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
        probe = self.next_sent()
        assert probe.get_type() == "probe"
        stanza = self.next_sent()
        assert "logged in" in stanza["status"].lower(), stanza

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

    def test_gateway_wide_restrictions(self):
        self.recv(  # language=XML
            f"""
            <iq from='romeo@montague.lit'
                to='{self.xmpp.boundjid.bare}'
                type='get'>
              <query xmlns='http://jabber.org/protocol/disco#info' />
            </iq>
            """
        )
        self.send(  # language=XML
            """
            <iq xmlns="jabber:component:accept"
                from="aim.shakespeare.lit"
                to="romeo@montague.lit"
                type="result"
                id="2">
              <query xmlns="http://jabber.org/protocol/disco#info">
                <identity category="account"
                          type="registered"
                          name="A test" />
                <identity category="pubsub"
                          type="pep"
                          name="A test" />
                <identity category="gateway"
                          type=""
                          name="A test" />
                <feature var="jabber:iq:search" />
                <feature var="jabber:iq:register" />
                <feature var="urn:ietf:params:xml:ns:vcard-4.0" />
                <feature var="urn:xmpp:mds:displayed:0+notify" />
                <feature var="urn:xmpp:mds:displayed:0" />
                <feature var="http://jabber.org/protocol/pubsub#event" />
                <feature var="http://jabber.org/protocol/pubsub#retrieve-items" />
                <feature var="http://jabber.org/protocol/pubsub#persistent-items" />
                <feature var="urn:xmpp:avatar:metadata+notify" />
                <feature var="urn:xmpp:chat-markers:0" />
                <feature var="jabber:iq:gateway" />
                <feature var="urn:xmpp:ping" />
                <feature var="http://jabber.org/protocol/commands" />
                <x xmlns="jabber:x:data"
                   type="result">
                  <field var="FORM_TYPE"
                         type="hidden">
                    <value>urn:xmpp:reactions:0:restrictions</value>
                  </field>
                  <field var="max_reactions_per_user"
                         type="number">
                    <value>1</value>
                  </field>
                  <field var="scope">
                    <value>domain</value>
                  </field>
                </x>
              </query>
            </iq>
            """
        )


    def test_error_multi_emoji(self):
        # one of the other tests has a persisting side effect which is triggered only
        # when running the full suite. :(
        self.xmpp.plugin["xep_0356"].granted_privileges.clear()
        self.recv(  # language=XML
            f"""
            <message from='romeo@montague.lit'
                     to='juliet@{self.xmpp.boundjid.bare}'>
              <reactions id='some-id'
                         xmlns='urn:xmpp:reactions:0'>
                <reaction>👋</reaction>
                <reaction>🐢</reaction>
              </reactions>
            </message>
            """
        )
        self.send(  # language=XML
            f"""
            <message xmlns="jabber:component:accept"
                     type="chat"
                     from="aim.shakespeare.lit"
                     to="romeo@montague.lit">
              <body>Maximum 1 emoji/message</body>
              <active xmlns="http://jabber.org/protocol/chatstates" />
              <markable xmlns="urn:xmpp:chat-markers:0" />
              <store xmlns="urn:xmpp:hints" />
            </message>
            """
        )
        self.send(  # language=XML
            """
            <message from="juliet@aim.shakespeare.lit"
                     to="romeo@montague.lit"
                     type="error">
              <reactions xmlns="urn:xmpp:reactions:0"
                         id="some-id">
                <reaction>👋</reaction>
                <reaction>🐢</reaction>
              </reactions>
              <error type="modify">
                <feature-not-implemented xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" />
                <text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas">Maximum 1 emoji/message</text>
              </error>
            </message>
            """,
            use_values=False
        )
