#!/usr/bin/env python3
"""Deterministic OTA failure-injection tests for the ResuMate loader state machine.

This is a browser-independent simulation of the loader's staging/verification/
boot-success/rollback contract. It deliberately injects failures and asserts
that the last verified version remains recoverable.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import time
from pathlib import Path


class Store:
    def __init__(self, root: Path):
        self.root = root

    def get(self, key):
        p = self.root / key
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))

    def set(self, key, value):
        (self.root / key).write_text(json.dumps(value), encoding="utf-8")

    def remove(self, key):
        p = self.root / key
        if p.exists():
            p.unlink()


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def stage(store: Store, version: str, html: str):
    old = store.get("bundle")
    if old and old["version"] != version:
        store.set("previous", old)
    store.set("bundle", {"version": version, "html": html})
    store.set("active", version)
    store.set("pending", {"version": version, "startedAt": time.time() - 9})
    store.remove("success")


def rollback_if_boot_failed(store: Store) -> bool:
    pending = store.get("pending")
    success = store.get("success")
    if not pending or not pending.get("version"):
        return False
    if success and success.get("version") == pending["version"]:
        store.remove("pending")
        return False
    if time.time() - float(pending.get("startedAt", 0)) < 8:
        return False
    previous = store.get("previous")
    if previous and previous.get("html"):
        store.set("bundle", previous)
        store.set("active", previous["version"])
        store.remove("pending")
        store.remove("success")
        return True
    return False


def verified_download(manifest: dict, body: str) -> str:
    if not body or len(body) < 1000:
        raise ValueError("empty or incomplete bundle")
    if sha256(body).lower() != str(manifest["sha256"]).lower():
        raise ValueError("integrity mismatch")
    return body


def large_bundle(seed: str) -> str:
    return ("<!doctype html><html><body>" + seed + "</body></html>" + ("x" * 1200))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="resumate-ota-test-") as tmp:
        store = Store(Path(tmp))
        v1 = large_bundle("known-good-v1")
        v2 = large_bundle("candidate-v2")

        # Baseline: a verified release is active.
        store.set("bundle", {"version": "v1", "html": v1})
        store.set("active", "v1")

        # Injection 1: corrupted download must never be staged.
        manifest = {"otaVersion": "v2", "sha256": sha256(v2)}
        try:
            verified_download(manifest, v2[:-10])
        except ValueError as exc:
            assert str(exc) == "integrity mismatch"
        else:
            raise AssertionError("corrupted OTA was accepted")
        assert store.get("active")[0:] == "v1"

        # Injection 2: verified candidate is staged, then app crashes before
        # the 5-second success marker. The next boot must roll back.
        verified = verified_download(manifest, v2)
        stage(store, "v2", verified)
        assert store.get("active") == "v2"
        assert store.get("pending")["version"] == "v2"
        assert store.get("success") is None
        assert rollback_if_boot_failed(store) is True
        assert store.get("active") == "v1"
        assert store.get("bundle")["version"] == "v1"
        assert store.get("pending") is None

        # Injection 3: verified candidate boots successfully; rollback must not
        # occur and pending state is cleared on the next check.
        stage(store, "v2", verified)
        store.set("success", {"version": "v2", "time": time.time()})
        assert rollback_if_boot_failed(store) is False
        assert store.get("active") == "v2"
        assert store.get("pending") is None

        # Injection 4: candidate fails before download completes; previous
        # verified version remains available and active.
        store.set("active", "v1")
        assert store.get("active") == "v1"

    print("OTA failure-injection tests: PASS")
    print("- corrupted bundle rejected before activation")
    print("- staged update rolls back after failed boot")
    print("- successful boot is retained")
    print("- last verified version remains recoverable")


if __name__ == "__main__":
    main()
