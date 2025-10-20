import pytest
import sqlalchemy as sa
from slixmpp import JID
from sqlalchemy import select

import slidge.db.store
from slidge import GatewayUser
from slidge.db.meta import Base
from slidge.db.models import Avatar, Contact, Participant, Room
from slidge.db.store import SlidgeStore


@pytest.fixture
def slidge_store(tmp_path):
    engine = sa.create_engine("sqlite+pysqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    import slidge.core.config

    if not hasattr(slidge.core.config, "HOME_DIR"):
        slidge.core.config.HOME_DIR = tmp_path
    yield SlidgeStore(engine)


def test_delete_avatar(slidge_store):
    with slidge_store.session() as orm:
        user = GatewayUser(jid=JID("x@x.com"), legacy_module_data={})
        orm.add(user)
        orm.commit()
        avatar = Avatar(
            hash="hash",
            height=0,
            width=0,
        )

        contact = Contact(
            jid=JID("xxx@xxx.com"), legacy_id="prout", user_account_id=user.id
        )
        orm.add(contact)
        orm.commit()
        contact_pk = contact.id
        contact = slidge_store.contacts.get_by_pk(orm, contact_pk)
        contact.avatar = avatar
        orm.add(contact)

        orm.commit()

    with slidge_store.session() as orm:
        contact = slidge_store.contacts.get_by_pk(orm, contact_pk)
        assert contact.avatar is not None
        orm.delete(contact.avatar)
        orm.commit()
    with slidge_store.session() as orm:
        contact = slidge_store.contacts.get_by_pk(orm, contact_pk)
        assert contact.avatar is None


def test_delete_contact_avatar_orphan(slidge_store):
    with slidge_store.session() as orm:
        user = GatewayUser(jid=JID("x@x.com"), legacy_module_data={})
        orm.add(user)
        orm.commit()

        avatar = Avatar(
            hash="hash",
            height=0,
            width=0,
        )

        contact = Contact(
            jid=JID("xxx@xxx.com"), legacy_id="prout", user_account_id=user.id, avatar=avatar
        )
        orm.add(contact)
        orm.commit()
        avatar_pk = avatar.id

        avatar = orm.get(Avatar, avatar_pk)
        assert avatar is not None

        orm.delete(contact)
        orm.commit()

        avatar = orm.get(Avatar, avatar_pk)
        assert avatar is None


def test_unregister(slidge_store):
    with slidge_store.session() as orm:
        user = GatewayUser(jid=JID("x@x.com"), legacy_module_data={})
        orm.add(user)
        contact = Contact(jid=JID("xxx@xxx.com"), legacy_id="prout", user=user)
        orm.add(contact)
        orm.commit()
        contact_pk = contact.id
        slidge_store.contacts.add_to_sent(orm, contact_pk, "an-id")
        orm.commit()
        orm.delete(user)
        orm.commit()


def test_unregister_with_participants(slidge_store):
    with slidge_store.session() as orm:
        user = GatewayUser(jid=JID("x@x.com"), legacy_module_data={})
        orm.add(user)
        orm.commit()
        contact = Contact(jid=JID("xxx@xxx.com"), legacy_id="prout", user=user)
        orm.add(contact)
        orm.commit()

        room = Room(
            user_account_id=user.id,
            legacy_id="legacy-room",
            jid=JID("legacy-room@something"),
        )
        orm.add(room)
        orm.commit()

        contacts = orm.execute(select(Contact).where(Contact.user_account_id == user.id)).scalars()
        assert len(list(contacts)) == 1
        rooms = orm.execute(select(Room).where(Room.user_account_id == user.id)).scalars()
        assert len(list(rooms)) == 1

        participant = Participant(
            room_id=room.id,
            contact_id=contact.id,
            resource="whatever",
            nickname="whatever",
            nickname_no_illegal="whatever",
        )
        orm.add(participant)
        orm.commit()

        orm.delete(user)
        orm.commit()

        rooms = orm.execute(select(Room).where(Room.user_account_id == user.id)).scalars()
        assert len(list(rooms)) == 0

        contacts = orm.execute(select(Contact).where(Contact.user_account_id == user.id)).scalars()
        assert len(list(contacts)) == 0
