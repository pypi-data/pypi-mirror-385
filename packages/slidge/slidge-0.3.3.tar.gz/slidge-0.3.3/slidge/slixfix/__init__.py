# This module contains patches for slixmpp; some have pending requests upstream
# and should be removed on the next slixmpp release.

# ruff: noqa: F401

import uuid

import slixmpp.plugins
import slixmpp.stanza.roster
from slixmpp import Message, register_stanza_plugin
from slixmpp.exceptions import IqError
from slixmpp.plugins.xep_0050 import XEP_0050, Command
from slixmpp.plugins.xep_0356.permissions import IqPermission
from slixmpp.plugins.xep_0356.privilege import XEP_0356
from slixmpp.plugins.xep_0385.sims import XEP_0385
from slixmpp.plugins.xep_0385.sims import stanza as stanza_sims
from slixmpp.plugins.xep_0469.stanza import NS as PINNED_NS
from slixmpp.plugins.xep_0469.stanza import Pinned
from slixmpp.xmlstream import StanzaBase

from . import (
    link_preview,
    xep_0077,
    xep_0100,
    xep_0153,
    xep_0292,
)


def plugin_init(self):
    register_stanza_plugin(self.xmpp["xep_0372"].stanza.Reference, stanza_sims.Sims)
    register_stanza_plugin(Message, stanza_sims.Sims)

    register_stanza_plugin(stanza_sims.Sims, stanza_sims.Sources)
    register_stanza_plugin(stanza_sims.Sims, self.xmpp["xep_0234"].stanza.File)
    register_stanza_plugin(
        stanza_sims.Sources, self.xmpp["xep_0372"].stanza.Reference, iterable=True
    )


XEP_0385.plugin_init = plugin_init


def set_pinned(self, val: bool) -> None:
    extensions = self.parent()
    if val:
        extensions.enable("pinned")
    else:
        extensions._del_sub(f"{{{PINNED_NS}}}pinned")


Pinned.set_pinned = set_pinned


def session_bind(self, jid) -> None:
    self.xmpp["xep_0030"].add_feature(Command.namespace)
    # awful hack to for the disco items: we need to comment this line
    # related issue: https://todo.sr.ht/~nicoco/slidge/131
    # self.xmpp['xep_0030'].set_items(node=Command.namespace, items=tuple())


XEP_0050.session_bind = session_bind  # type:ignore


def reply(self, body=None, clear: bool = True):
    """
    Overrides slixmpp's Message.reply(), since it strips to sender's resource
    for mtype=groupchat, and we do not want that, because when we raise an XMPPError,
    we actually want to preserve the resource.
    (this is called in RootStanza.exception() to handle XMPPErrors)
    """
    new_message = StanzaBase.reply(self, clear)
    new_message["thread"] = self["thread"]
    new_message["parent_thread"] = self["parent_thread"]

    del new_message["id"]
    if self.stream is not None and self.stream.use_message_ids:
        new_message["id"] = self.stream.new_id()

    if body is not None:
        new_message["body"] = body
    return new_message


Message.reply = reply  # type: ignore

# TODO: remove me when https://codeberg.org/poezio/slixmpp/pulls/3622 is merged


class PrivilegedIqError(IqError):
    """
    Exception raised when sending a privileged IQ stanza fails.
    """

    def nested_error(self) -> IqError | None:
        """
        Return the IQError generated from the inner IQ stanza, if present.
        """
        if "privilege" in self.iq:
            if "forwarded" in self.iq["privilege"]:
                if "iq" in self.iq["privilege"]["forwarded"]:
                    return IqError(self.iq["privilege"]["forwarded"]["iq"])
        return None


async def send_privileged_iq(self, encapsulated_iq, iq_id=None):
    """
    Send an IQ on behalf of a user

    Caution: the IQ *must* have the jabber:client namespace

    Raises :class:`PrivilegedIqError` on failure.
    """
    iq_id = iq_id or str(uuid.uuid4())
    encapsulated_iq["id"] = iq_id
    server = encapsulated_iq.get_to().domain
    perms = self.granted_privileges.get(server)
    if not perms:
        raise PermissionError(f"{server} has not granted us any privilege")
    itype = encapsulated_iq["type"]
    for ns in encapsulated_iq.plugins.values():
        type_ = perms.iq[ns.namespace]
        if type_ == IqPermission.NONE:
            raise PermissionError(
                f"{server} has not granted any IQ privilege for namespace {ns.namespace}"
            )
        elif type_ == IqPermission.BOTH:
            pass
        elif type_ != itype:
            raise PermissionError(
                f"{server} has not granted IQ {itype} privilege for namespace {ns.namespace}"
            )
    iq = self.xmpp.make_iq(
        itype=itype,
        ifrom=self.xmpp.boundjid.bare,
        ito=encapsulated_iq.get_from(),
        id=iq_id,
    )
    iq["privileged_iq"].append(encapsulated_iq)

    try:
        resp = await iq.send()
    except IqError as exc:
        raise PrivilegedIqError(exc.iq)

    return resp["privilege"]["forwarded"]["iq"]


XEP_0356.send_privileged_iq = send_privileged_iq


slixmpp.plugins.PLUGINS.extend(
    [
        "link_preview",
        "xep_0292_provider",
    ]
)
