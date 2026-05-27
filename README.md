# b4-mcp

A tiny [Model Context Protocol](https://modelcontextprotocol.io) server that
exposes [`b4 mbox`](https://b4.docs.kernel.org/) as a tool, so Claude Code
(or any MCP-aware client) can fetch Linux-kernel patch threads from
`lore.kernel.org` on demand.

The server runs `b4` through a forward proxy, which is required in
environments where outbound HTTP is only reachable via
`http://fwdproxy:8080` (e.g. Meta corp hosts). Outside of such an
environment, edit `PROXY_ENV` in `server.py` or remove it entirely.

## Tools

| Tool      | Arguments        | Returns                                                              |
| --------- | ---------------- | -------------------------------------------------------------------- |
| `b4_mbox` | `msgid: string`  | Path(s) to the saved mbox file(s) plus `b4`'s stdout/stderr output.  |

`msgid` accepts the Message-ID with or without angle brackets.

Each call writes into a fresh `/tmp/b4-mbox-XXXXXX/` directory.

## Requirements

- Python ≥ 3.10
- [`uv`](https://docs.astral.sh/uv/) (recommended) or `pip`
- [`b4`](https://b4.docs.kernel.org/) on `$PATH`
- Network reachability to `lore.kernel.org` (directly or via the
  configured forward proxy)

## Install

```sh
git clone https://github.com/<you>/b4-mcp.git
cd b4-mcp
uv sync
```

That creates `.venv/` with the `mcp` SDK. Verify the server loads:

```sh
uv run python -c "import server; print(server.mcp.name)"
# -> b4-mcp
```

## Register with Claude Code

Register at **user scope** so the server is available in every project
and every session:

```sh
claude mcp add --scope user b4-mcp -- \
    uv --directory /absolute/path/to/b4-mcp run python server.py
```

Scope options:

| Scope       | Flag                | Where it lives                            |
| ----------- | ------------------- | ----------------------------------------- |
| `local`     | (default)           | Current project only                      |
| `user`      | `--scope user`      | `~/.claude.json` — available everywhere   |
| `project`   | `--scope project`   | `.mcp.json` checked into the repo         |

Verify:

```sh
claude mcp list      # should show b4-mcp
```

Inside a Claude session, run `/mcp` to see connected servers and their
tools.

## Usage

Once registered, just ask Claude in natural language:

> grab the mbox for `20260115-fix-foo-v2-0-abc@kernel.org`

or be explicit:

> use the `b4-mcp` MCP to fetch message-id `<...>` and show me the
> cover letter

Claude will call `b4_mbox`, receive the path of the saved mbox, and can
then `Read` it, apply it with `git am`, feed it to `b4 shazam`, etc.

## Configuration

Edit `server.py` to change behavior:

- **Proxy** — adjust `PROXY_ENV`. Set it to `{}` to use the host's
  default network configuration.
- **Timeout** — `subprocess.run(..., timeout=120)` (seconds).
- **Output dir** — currently a fresh `tempfile.mkdtemp` per call. Swap
  for a fixed directory if you want to accumulate threads.

## Troubleshooting

- **`b4 not found in PATH`** — install `b4` (`pipx install b4`) and make
  sure it's on the PATH that Claude inherits at startup.
- **`b4 mbox failed (exit N)`** — the tool surfaces `b4`'s stdout and
  stderr verbatim. Most common cause is a wrong msgid or the proxy
  being unreachable.
- **Tool doesn't appear in `/mcp`** — re-check `claude mcp list`. If
  you edited `server.py`, restart the session (`/mcp` → reconnect) or
  re-register.
- **Path moved/renamed** — the registered command embeds an absolute
  path. If you move the checkout, `claude mcp remove b4-mcp` and add
  it again with the new path.

## License

MIT (or whatever you prefer — adjust before publishing).
