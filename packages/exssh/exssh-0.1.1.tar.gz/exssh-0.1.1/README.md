# exssh

Provide automation capability for any ssh client.

## Install

`pip install exssh`

with bitwarden cli support:

`pip install exssh[bitwarden]`


## Usage

- `CONNECT_CONFIG` connection config file (default: ~/.ssh/connect.conf)
- `EXPECT_CONFIG` expect config file (default: ~/.ssh/expect.conf)
- `COPY_CONFIG` copy config file (default: ~/.ssh/copy.conf)
- `PROG` ssh client program (default: ssh)
- `EXTRA` extra parameter for ssh client program

`python3 -m exssh [-p PORT] [--timeout TIMEOUT] [--connect-config CONNECT_CONFIG] [--expect-config EXPECT_CONFIG] [--copy-config COPY_CONFIG] [--prog PROG] [--extra EXTRA] host`

### CONNECT_CONFIG

``` config
[*]
prog=zssh
-z=^\\
extra=-t "tmux new-session -A -s main"

[*-vps]
prog=mosh
--predict=experimental
--predict-overwrite=
```

- config section title is matching ssh host of ~/.ssh/config
- prog and extra is the same of command argument
- other configs are parameters specific to the choosing prog

### EXPECT_CONFIG

``` config
[ssh-host]
prompt = Welcome to HOST
user = Username
password = P@ssw0rd
```

- config section title is matching ssh host of ~/.ssh/config
- prompt is the indicator of successful connection in case not autodetected
- other configs key is trigger keyword, value is auto fill response

### COPY_CONFIG

```config
[*]
start=b'\x21\x21'
end=b'\x26'
sshid=~/.ssh/id_ed25519.pub
hostname=/etc/hostname
```

In this example, when connected in a session:
type `!!sshid&` will copy content of `~/.ssh/id_ed25519.pub` into clipboard
type `!!hostname&` will copy content of `/etc/hostname` into clipboard

if `start` not defined, default to `\x60\x60`
if `end` not defined, default to `\x09`
