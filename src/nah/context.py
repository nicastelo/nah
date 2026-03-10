"""Context resolution — filesystem and network context for 'context' policy decisions."""

import os
import urllib.parse

from nah import paths, taxonomy

# Known safe registries / hosts for network context.
_KNOWN_HOSTS: set[str] = {
    "npmjs.org", "www.npmjs.org", "registry.npmjs.org",
    "pypi.org", "files.pythonhosted.org",
    "github.com", "api.github.com", "raw.githubusercontent.com",
    "crates.io",
    "rubygems.org",
    "packagist.org",
    "registry.yarnpkg.com",
    "registry.npmmirror.com",
    "dl.google.com",
    "repo.maven.apache.org",
    "pkg.go.dev", "proxy.golang.org",
    "hub.docker.com", "registry.hub.docker.com", "ghcr.io",
}

# Localhost addresses.
_LOCALHOST: set[str] = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}


def resolve_filesystem_context(target_path: str) -> tuple[str, str]:
    """Resolve filesystem context for a target path.

    Returns (decision, reason).
    """
    if not target_path:
        return taxonomy.ALLOW, "no target path"

    resolved = paths.resolve_path(target_path)

    # Core path check (hook + sensitive)
    basic = paths.check_path_basic(resolved)
    if basic:
        return basic

    # Project root check
    project_root = paths.get_project_root()
    if project_root is None:
        return taxonomy.ASK, f"outside project (no git root): {paths.friendly_path(resolved)}"

    real_root = os.path.realpath(project_root)
    if resolved == real_root or resolved.startswith(real_root + os.sep):
        return taxonomy.ALLOW, f"inside project: {paths.friendly_path(resolved)}"

    return taxonomy.ASK, f"outside project: {paths.friendly_path(resolved)}"


def resolve_network_context(tokens: list[str]) -> tuple[str, str]:
    """Resolve network context for outbound commands.

    Returns (decision, reason).
    """
    host = extract_host(tokens)
    if host is None:
        return taxonomy.ASK, "unknown host"

    # Strip port if present
    host_no_port = host.split(":")[0] if ":" in host else host

    # Localhost
    if host_no_port in _LOCALHOST:
        return taxonomy.ALLOW, f"localhost: {host}"

    # Known registries
    if host_no_port in _KNOWN_HOSTS:
        return taxonomy.ALLOW, f"known host: {host_no_port}"

    # User-configured known registries
    from nah.config import get_config  # lazy import to avoid circular
    cfg = get_config()
    if host_no_port in cfg.known_registries:
        return taxonomy.ALLOW, f"known host (config): {host_no_port}"

    return taxonomy.ASK, f"unknown host: {host_no_port}"


def extract_host(tokens: list[str]) -> str | None:
    """Extract hostname from network command tokens.

    Handles curl/wget URLs, ssh user@host, nc/telnet host.
    """
    if not tokens:
        return None

    cmd = tokens[0]
    args = tokens[1:]

    if cmd in ("curl", "wget"):
        return _extract_url_host(args)
    if cmd in ("ssh", "scp", "sftp"):
        return _extract_positional_host(args, {"-p", "-i", "-l", "-o", "-F", "-J", "-P"})
    if cmd in ("nc", "ncat", "telnet"):
        return _extract_positional_host(args, {"-p", "-w", "-s"})

    # Fallback: try URL extraction
    return _extract_url_host(args)


def _extract_url_host(args: list[str]) -> str | None:
    """Find URL-like argument and parse hostname."""
    for arg in args:
        if arg.startswith("-"):
            continue
        # Try parsing as URL
        if "://" in arg or arg.startswith("//"):
            parsed = urllib.parse.urlparse(arg)
            if parsed.hostname:
                return parsed.hostname
        # Bare hostname:port or hostname/path
        if "." in arg or ":" in arg:
            # Could be host:port or host/path
            part = arg.split("/")[0]
            if part and not part.startswith("-"):
                return part.split(":")[0] if ":" in part else part
    return None


def _extract_positional_host(args: list[str], valued_flags: set[str]) -> str | None:
    """Extract host from positional args, skipping valued flags. Handles user@host."""
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg.startswith("-"):
            if arg in valued_flags:
                skip_next = True
            continue
        # user@host
        if "@" in arg:
            host_part = arg.split("@", 1)[1]
            return host_part.split(":")[0] if ":" in host_part else host_part
        return arg
    return None
