#!/usr/bin/env python
import pickle
Decoders = {}
Decoders["/interface print"] = "(\s{1})(?P<interface_number>[0-9]+)((\s{2})(?P<interface_flags>[RXSD]+)?(\s+))(?P<interface_name>\w+)\s+(?P<interface_type>\w+)\s+(?P<interface_mtu>[0-9]+)(\s+)?(?P<interface_l2mtu>[0-9]+)?(\s+)?(?P<interface_max_l2mtu>[0-9]+)?"
Decoders["/ip address print"] = "\s{1}(?P<ip_number>[0-9]+)(((\s+)(?P<ip_flag>[IXD]+)(\s+))|(\s+))(?P<ip_address>[0-9\.\/]+)\s+(?P<ip_network>[0-9\.]+)\s+(?P<ip_interface>((\w+)|(\(unknown\))))"
pickle.dump(Decoders, open("decoders.p","wb"))
