import warnings
from datetime import datetime
from enum import IntEnum
from typing import Optional

import sqlalchemy as sa
from slixmpp import JID
from slixmpp.types import MucAffiliation, MucRole
from sqlalchemy import JSON, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..util.types import ClientType, Hat, MucType
from .meta import Base, JSONSerializable, JSONSerializableTypes


class ArchivedMessageSource(IntEnum):
    """
    Whether an archived message comes from ``LegacyMUC.backfill()`` or was received
    as a "live" message.
    """

    LIVE = 1
    BACKFILL = 2


class GatewayUser(Base):
    """
    A user, registered to the gateway component.
    """

    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    jid: Mapped[JID] = mapped_column(unique=True)
    registration_date: Mapped[datetime] = mapped_column(
        sa.DateTime, server_default=sa.func.now()
    )

    legacy_module_data: Mapped[JSONSerializable] = mapped_column(default={})
    """
    Arbitrary non-relational data that legacy modules can use
    """
    preferences: Mapped[JSONSerializable] = mapped_column(default={})
    avatar_hash: Mapped[Optional[str]] = mapped_column(default=None)
    """
    Hash of the user's avatar, to avoid re-publishing the same avatar on the
    legacy network
    """

    contacts: Mapped[list["Contact"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    rooms: Mapped[list["Room"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["Attachment"]] = relationship(cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, jid={self.jid!r})"

    def get(self, field: str, default: str = "") -> JSONSerializableTypes:
        # """
        # Get fields from the registration form (required to comply with slixmpp backend protocol)
        #
        # :param field: Name of the field
        # :param default: Default value to return if the field is not present
        #
        # :return: Value of the field
        # """
        return self.legacy_module_data.get(field, default)

    @property
    def registration_form(self) -> dict:
        # Kept for retrocompat, should be
        # FIXME: delete me
        warnings.warn(
            "GatewayUser.registration_form is deprecated.", DeprecationWarning
        )
        return self.legacy_module_data


class Avatar(Base):
    """
    Avatars of contacts, rooms and participants.

    To comply with XEPs, we convert them all to PNG before storing them.
    """

    __tablename__ = "avatar"

    id: Mapped[int] = mapped_column(primary_key=True)

    hash: Mapped[str] = mapped_column(unique=True)
    height: Mapped[int] = mapped_column()
    width: Mapped[int] = mapped_column()

    legacy_id: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)

    # this is only used when avatars are available as HTTP URLs and do not
    # have a legacy_id
    url: Mapped[Optional[str]] = mapped_column(default=None)
    etag: Mapped[Optional[str]] = mapped_column(default=None)
    last_modified: Mapped[Optional[str]] = mapped_column(default=None)

    contacts: Mapped[list["Contact"]] = relationship(back_populates="avatar")
    rooms: Mapped[list["Room"]] = relationship(back_populates="avatar")


class Contact(Base):
    """
    Legacy contacts
    """

    __tablename__ = "contact"
    __table_args__ = (
        UniqueConstraint("user_account_id", "legacy_id"),
        UniqueConstraint("user_account_id", "jid"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_account_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped[GatewayUser] = relationship(lazy=True, back_populates="contacts")
    legacy_id: Mapped[str] = mapped_column(nullable=False)

    jid: Mapped[JID] = mapped_column()

    avatar_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("avatar.id"), nullable=True
    )
    avatar: Mapped[Optional[Avatar]] = relationship(
        lazy=False, back_populates="contacts"
    )

    nick: Mapped[Optional[str]] = mapped_column(nullable=True)

    cached_presence: Mapped[bool] = mapped_column(default=False)
    last_seen: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    ptype: Mapped[Optional[str]] = mapped_column(nullable=True)
    pstatus: Mapped[Optional[str]] = mapped_column(nullable=True)
    pshow: Mapped[Optional[str]] = mapped_column(nullable=True)
    caps_ver: Mapped[Optional[str]] = mapped_column(nullable=True)

    is_friend: Mapped[bool] = mapped_column(default=False)
    added_to_roster: Mapped[bool] = mapped_column(default=False)
    sent_order: Mapped[list["ContactSent"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )

    extra_attributes: Mapped[Optional[JSONSerializable]] = mapped_column(
        default=None, nullable=True
    )
    updated: Mapped[bool] = mapped_column(default=False)

    vcard: Mapped[Optional[str]] = mapped_column()
    vcard_fetched: Mapped[bool] = mapped_column(default=False)

    participants: Mapped[list["Participant"]] = relationship(back_populates="contact")

    client_type: Mapped[ClientType] = mapped_column(nullable=False, default="pc")

    messages: Mapped[list["DirectMessages"]] = relationship(
        cascade="all, delete-orphan"
    )
    threads: Mapped[list["DirectThreads"]] = relationship(cascade="all, delete-orphan")


class ContactSent(Base):
    """
    Keep track of XMPP msg ids sent by a specific contact for networks in which
    all messages need to be marked as read.

    (XMPP displayed markers convey a "read up to here" semantic.)
    """

    __tablename__ = "contact_sent"
    __table_args__ = (UniqueConstraint("contact_id", "msg_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id"))
    contact: Mapped[Contact] = relationship(back_populates="sent_order")
    msg_id: Mapped[str] = mapped_column()


class Room(Base):
    """
    Legacy room
    """

    __table_args__ = (
        UniqueConstraint(
            "user_account_id", "legacy_id", name="uq_room_user_account_id_legacy_id"
        ),
        UniqueConstraint("user_account_id", "jid", name="uq_room_user_account_id_jid"),
    )

    __tablename__ = "room"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_account_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped[GatewayUser] = relationship(lazy=True, back_populates="rooms")
    legacy_id: Mapped[str] = mapped_column(nullable=False)

    jid: Mapped[JID] = mapped_column(nullable=False)

    avatar_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("avatar.id"), nullable=True
    )
    avatar: Mapped[Optional[Avatar]] = relationship(lazy=False, back_populates="rooms")

    name: Mapped[Optional[str]] = mapped_column(nullable=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(nullable=True)
    subject_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    subject_setter: Mapped[Optional[str]] = mapped_column(nullable=True)

    n_participants: Mapped[Optional[int]] = mapped_column(default=None)

    muc_type: Mapped[MucType] = mapped_column(default=MucType.CHANNEL)

    user_nick: Mapped[Optional[str]] = mapped_column()
    user_resources: Mapped[Optional[str]] = mapped_column(nullable=True)

    participants_filled: Mapped[bool] = mapped_column(default=False)
    history_filled: Mapped[bool] = mapped_column(default=False)

    extra_attributes: Mapped[Optional[JSONSerializable]] = mapped_column(default=None)
    updated: Mapped[bool] = mapped_column(default=False)

    participants: Mapped[list["Participant"]] = relationship(
        back_populates="room",
        primaryjoin="Participant.room_id == Room.id",
        cascade="all, delete-orphan",
    )

    archive: Mapped[list["ArchivedMessage"]] = relationship(
        cascade="all, delete-orphan"
    )

    messages: Mapped[list["GroupMessages"]] = relationship(cascade="all, delete-orphan")
    threads: Mapped[list["GroupThreads"]] = relationship(cascade="all, delete-orphan")


class ArchivedMessage(Base):
    """
    Messages of rooms, that we store to act as a MAM server
    """

    __tablename__ = "mam"
    __table_args__ = (UniqueConstraint("room_id", "stanza_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("room.id"), nullable=False)

    stanza_id: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    author_jid: Mapped[JID] = mapped_column(nullable=False)
    source: Mapped[ArchivedMessageSource] = mapped_column(nullable=False)
    legacy_id: Mapped[Optional[str]] = mapped_column(nullable=True)

    stanza: Mapped[str] = mapped_column(nullable=False)


class _LegacyToXmppIdsBase:
    """
    XMPP-client generated IDs, and mapping to the corresponding legacy IDs.

    A single legacy ID can map to several XMPP ids.
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    legacy_id: Mapped[str] = mapped_column(nullable=False)
    xmpp_id: Mapped[str] = mapped_column(nullable=False)


class DirectMessages(_LegacyToXmppIdsBase, Base):
    __tablename__ = "direct_msg"
    __table_args__ = (Index("ix_direct_msg_legacy_id", "legacy_id", "foreign_key"),)
    foreign_key: Mapped[int] = mapped_column(ForeignKey("contact.id"), nullable=False)


class GroupMessages(_LegacyToXmppIdsBase, Base):
    __tablename__ = "group_msg"
    __table_args__ = (Index("ix_group_msg_legacy_id", "legacy_id", "foreign_key"),)
    foreign_key: Mapped[int] = mapped_column(ForeignKey("room.id"), nullable=False)


class DirectThreads(_LegacyToXmppIdsBase, Base):
    __tablename__ = "direct_thread"
    __table_args__ = (Index("ix_direct_direct_thread_id", "legacy_id", "foreign_key"),)
    foreign_key: Mapped[int] = mapped_column(ForeignKey("contact.id"), nullable=False)


class GroupThreads(_LegacyToXmppIdsBase, Base):
    __tablename__ = "group_thread"
    __table_args__ = (Index("ix_direct_group_thread_id", "legacy_id", "foreign_key"),)
    foreign_key: Mapped[int] = mapped_column(ForeignKey("room.id"), nullable=False)


class Attachment(Base):
    """
    Legacy attachments
    """

    __tablename__ = "attachment"
    __table_args__ = (UniqueConstraint("user_account_id", "legacy_file_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_account_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped[GatewayUser] = relationship(back_populates="attachments")

    legacy_file_id: Mapped[Optional[str]] = mapped_column(index=True, nullable=True)
    url: Mapped[str] = mapped_column(index=True, nullable=False)
    sims: Mapped[Optional[str]] = mapped_column()
    sfs: Mapped[Optional[str]] = mapped_column()


class Participant(Base):
    __tablename__ = "participant"
    __table_args__ = (
        UniqueConstraint("room_id", "resource"),
        UniqueConstraint("room_id", "contact_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    room_id: Mapped[int] = mapped_column(ForeignKey("room.id"), nullable=False)
    room: Mapped[Room] = relationship(
        lazy=False, back_populates="participants", primaryjoin=Room.id == room_id
    )

    contact_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("contact.id"), nullable=True
    )
    contact: Mapped[Optional[Contact]] = relationship(
        lazy=False, back_populates="participants"
    )

    is_user: Mapped[bool] = mapped_column(default=False)

    affiliation: Mapped[MucAffiliation] = mapped_column(default="member")
    role: Mapped[MucRole] = mapped_column(default="participant")

    presence_sent: Mapped[bool] = mapped_column(default=False)

    resource: Mapped[str] = mapped_column(nullable=False)
    nickname: Mapped[str] = mapped_column(nullable=False, default=None)
    nickname_no_illegal: Mapped[str] = mapped_column(nullable=False, default=None)

    hats: Mapped[list[Hat]] = mapped_column(JSON, default=list)

    extra_attributes: Mapped[Optional[JSONSerializable]] = mapped_column(default=None)


class Bob(Base):
    __tablename__ = "bob"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(nullable=False)

    sha_1: Mapped[str] = mapped_column(nullable=False, unique=True)
    sha_256: Mapped[str] = mapped_column(nullable=False, unique=True)
    sha_512: Mapped[str] = mapped_column(nullable=False, unique=True)

    content_type: Mapped[Optional[str]] = mapped_column(nullable=False)
