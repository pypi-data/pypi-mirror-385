from slixmpp import register_stanza_plugin, __version_info__
from slixmpp.plugins.base import BasePlugin, register_plugin
from slixmpp.plugins.xep_0292.stanza import NS, _VCardTextElementBase, VCard4


class VCard4Provider(BasePlugin):
    name = "xep_0292_provider"
    description = "VCard4 Provider"
    dependencies = {"xep_0030"}

    def plugin_init(self) -> None:
        self.xmpp.plugin["xep_0030"].add_feature(NS)




register_plugin(VCard4Provider)


if __version_info__[0] <= 1 and __version_info__[1] <= 11:
    class Pronouns(_VCardTextElementBase):
        name = plugin_attrib = "pronouns"

    register_stanza_plugin(VCard4, Pronouns)
