# V2bX
A V2board node server based on Xray-Core.

一个基于Xray的V2board节点服务端，支持V2ay,Trojan,Shadowsocks协议

Source: [fastincc/V2bX](https://github.com/fastincc/V2bX).

Independent distribution based on wyx2685/V2bX-script and InazumaV/V2bX. Original authors and license are retained.

如对脚本不放心，可使用此沙箱先测一遍再使用：https://killercoda.com/playgrounds/scenario/ubuntu

# 详细使用教程

[教程](https://v2bx.v-50.me/)

# 一键安装

```
wget -N https://raw.githubusercontent.com/fastincc/V2bX-script/main/install.sh && bash install.sh
```


## AnyTLS real-IP / audit release

`fastincc-v0.4.1-3` defaults AnyTLS PROXY v2 reception ON (3-second timeout, no
relay allowlist). Starting with `fastincc-v0.4.1-4`, audit also defaults ON. The new-config wizard
uses sing info logging when an AnyTLS node is present; existing log levels and
explicit AnyTLSAuditAccess=false are preserved during updates. Installation preserves an existing
config.json, but an omitted PROXY setting now enables reception. Direct/no-header
listeners must explicitly set `AnyTLSProxyProtocol.Enable` to false before upgrading. See [configuration and audit contract](https://github.com/fastincc/V2bX/blob/main/docs/ANYTLS.md).
Enable PROXY reception only when the relay sends the configured header; direct
clients without that header cannot connect to an enabled listener. Without a
trusted-relay allowlist, the client address is declared and unverified.

The installer verifies the published SHA256 digest and archive before stopping
an existing V2bX service. A service restart disconnects current sessions. Back up
binaries and configuration before updating; start with one low-traffic node.
This digest detects corrupted/mismatched downloads; it is not an independent
signature if the distribution repository itself is compromised.

```sh
# Pin the release for a controlled install/update:
curl -fL https://raw.githubusercontent.com/fastincc/V2bX-script/main/install.sh -o install.sh
bash install.sh fastincc-v0.4.1-4
```
