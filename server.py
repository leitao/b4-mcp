import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

PROXY_ENV = {
    "https_proxy": "http://fwdproxy:8080",
    "http_proxy": "http://fwdproxy:8080",
    "no_proxy": ".fbcdn.net,.facebook.com,.thefacebook.com,.tfbnw.net,"
                ".fb.com,.fburl.com,.facebook.net,.sb.fbsbx.com,localhost",
}

mcp = FastMCP("b4-mcp")


@mcp.tool()
def b4_mbox(msgid: str) -> str:
    """Fetch a patch thread from lore.kernel.org with `b4 mbox` and return
    the path to the saved mbox file.

    The fetch runs through the Meta forward proxy (fwdproxy:8080).

    Args:
        msgid: The Message-ID of any message in the thread. Angle brackets
               are optional.
    """
    b4 = shutil.which("b4")
    if not b4:
        raise RuntimeError("b4 not found in PATH")

    clean_msgid = msgid.strip().lstrip("<").rstrip(">")
    if not clean_msgid:
        raise ValueError("msgid is empty")

    outdir = Path(tempfile.mkdtemp(prefix="b4-mbox-"))

    env = os.environ.copy()
    env.update(PROXY_ENV)

    result = subprocess.run(
        [b4, "mbox", "-o", str(outdir), clean_msgid],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )

    files = sorted(p for p in outdir.iterdir() if p.is_file())
    if result.returncode != 0 or not files:
        raise RuntimeError(
            f"b4 mbox failed (exit {result.returncode})\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    paths = "\n".join(str(p) for p in files)
    return f"{paths}\n\n--- b4 output ---\n{result.stdout}{result.stderr}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
