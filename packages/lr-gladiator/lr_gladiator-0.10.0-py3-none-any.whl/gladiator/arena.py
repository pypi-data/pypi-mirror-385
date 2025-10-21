#! /usr/bin/env python
# -*- coding: utf-8 -*-
# src/gladiator/arena.py
from __future__ import annotations
import subprocess
import shlex
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from .config import LoginConfig
from .checksums import sha256_file


class ArenaError(RuntimeError):
    pass


class ArenaClient:
    def __init__(self, cfg: LoginConfig):
        self.cfg = cfg
        self.session = requests.Session()
        self.session.verify = cfg.verify_tls
        # Default headers: explicitly request/submit JSON
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "gladiator-arena/0.1",
                "Arena-Usage-Reason": cfg.reason or "gladiator/cli",
            }
        )
        if cfg.arena_session_id:
            self.session.headers.update({"arena_session_id": cfg.arena_session_id})

        self._debug = bool(int(os.environ.get("GLADIATOR_DEBUG", "0")))

    # ---------- Utilities ----------
    def _ensure_json(self, resp: requests.Response):
        ctype = resp.headers.get("Content-Type", "").lower()
        if "application/json" not in ctype:
            snippet = resp.text[:400].replace("", " ")
            raise ArenaError(
                f"Expected JSON but got '{ctype or 'unknown'}' from {resp.url}. "
                f"Status {resp.status_code}. Body starts with: {snippet}"
            )
        try:
            return resp.json()
        except Exception as e:
            raise ArenaError(f"Failed to parse JSON from {resp.url}: {e}") from e

    def _log(self, msg: str):
        if self._debug:
            print(f"[gladiator debug] {msg}")

    def _try_json(self, resp: requests.Response) -> Optional[dict]:
        """Best-effort JSON parse. Returns None if not JSON or parse fails."""
        ctype = resp.headers.get("Content-Type", "").lower()
        if "application/json" not in ctype:
            return None
        try:
            data = resp.json()
            return data if isinstance(data, dict) else {"data": data}
        except Exception:
            return None

    # --- version picking helpers ---
    @staticmethod
    def _logical_key(f: Dict) -> str:
        # Prefer any group-level id; fall back to normalized filename
        return (
            f.get("attachmentGroupGuid")
            or f.get("attachmentGroupId")
            or f.get("attachmentGuid")
            or (f.get("name") or f.get("filename") or "").lower()
        )

    @staticmethod
    def _version_of(f: Dict) -> int:
        for k in ("version", "fileVersion", "versionNumber", "rev", "revision"):
            v = f.get(k)
            if v is None:
                continue
            try:
                return int(v)
            except Exception:
                if isinstance(v, str) and len(v) == 1 and v.isalpha():
                    return ord(v.upper()) - 64  # A->1
        return -1

    @staticmethod
    def _timestamp_of(f: Dict):
        from datetime import datetime
        from email.utils import parsedate_to_datetime

        for k in (
            "modifiedAt",
            "updatedAt",
            "lastModified",
            "lastModifiedDate",
            "effectiveDate",
            "createdAt",
        ):
            s = f.get(k)
            if not s:
                continue
            try:
                return datetime.fromisoformat(s.replace("Z", "+00:00"))
            except Exception:
                try:
                    return parsedate_to_datetime(s)
                except Exception:
                    continue
        return None

    def _latest_files(self, files: List[Dict]) -> List[Dict]:
        best: Dict[str, Dict] = {}
        for f in files:
            key = self._logical_key(f)
            if not key:
                continue
            score = (self._version_of(f), self._timestamp_of(f) or 0)
            prev = best.get(key)
            if not prev:
                f["_score"] = score
                best[key] = f
                continue
            if score > prev.get("_score", (-1, 0)):
                f["_score"] = score
                best[key] = f
        out = []
        for v in best.values():
            v.pop("_score", None)
            out.append(v)
        return out

    # ---------- Public high-level methods ----------
    def get_latest_approved_revision(self, item_number: str) -> str:
        return self._api_get_latest_approved(item_number)

    def list_files(
        self, item_number: str, revision: Optional[str] = None
    ) -> List[Dict]:
        target_guid = self._api_resolve_revision_guid(
            item_number, revision or "EFFECTIVE"
        )
        raw = self._api_list_files_by_item_guid(target_guid)
        return self._latest_files(raw)

    def download_files(
        self,
        item_number: str,
        revision: Optional[str] = None,
        out_dir: Path = Path("."),
    ) -> List[Path]:
        files = self.list_files(item_number, revision)
        out_dir.mkdir(parents=True, exist_ok=True)
        downloaded: List[Path] = []
        for f in files:
            # Skip associations with no blob
            if not f.get("haveContent", True):
                self._log(
                    f"Skip {item_number}: file {f.get('filename')} has no content"
                )
                continue

            url = f.get("downloadUrl") or f.get("url")
            filename = f.get("filename") or f.get("name")
            if not url or not filename:
                continue

            p = out_dir / filename
            try:
                with self.session.get(
                    url,
                    stream=True,
                    headers={"arena_session_id": self.cfg.arena_session_id or ""},
                ) as r:
                    # If the blob is missing/forbidden, don’t abort the whole command
                    if r.status_code in (400, 403, 404):
                        self._log(
                            f"Skip {item_number}: {filename} content unavailable "
                            f"(HTTP {r.status_code})"
                        )
                        continue
                    r.raise_for_status()
                    with open(p, "wb") as fh:
                        for chunk in r.iter_content(128 * 1024):
                            fh.write(chunk)
                downloaded.append(p)
            except requests.HTTPError as e:
                # Be resilient: log and continue
                self._log(f"Download failed for {filename}: {e}")
                continue
        return downloaded

    def download_files_recursive(
        self,
        item_number: str,
        revision: Optional[str] = None,
        out_dir: Path = Path("."),
        *,
        max_depth: Optional[int] = None,
    ) -> List[Path]:
        """
        Download files for `item_number` AND, recursively, for all subassemblies
        discovered via the BOM. Each child item is placed under a subdirectory:
            <out_dir>/<child_item_number>/
        Root files go directly in <out_dir>/.

        Depth semantics match `get_bom(..., recursive=True, max_depth=...)`.
        """
        # Ensure the root directory exists
        out_dir.mkdir(parents=True, exist_ok=True)

        downloaded: List[Path] = []
        # 1) Download files for the root item into out_dir
        downloaded.extend(self.download_files(item_number, revision, out_dir=out_dir))

        # 2) Expand BOM recursively and collect unique child item numbers
        lines = self.get_bom(
            item_number,
            revision,
            recursive=True,
            max_depth=max_depth,
        )
        seen_children = set()
        for ln in lines:
            child_num = (ln or {}).get("itemNumber")
            if not child_num or child_num == item_number:
                continue
            if child_num in seen_children:
                continue
            seen_children.add(child_num)

            # Place each child's files under <out_dir>/<child_num>/
            child_dir = out_dir / child_num
            downloaded.extend(
                self.download_files(child_num, revision, out_dir=child_dir)
            )

        return downloaded

    def upload_file_to_working(
        self,
        item_number: str,
        file_path: Path,
        reference: Optional[str] = None,
        *,
        title: Optional[str] = None,
        category_name: str = "CAD Data",
        file_format: Optional[str] = None,
        description: Optional[str] = None,
        primary: bool = True,
        latest_edition_association: bool = True,
        edition: str = None,
    ) -> Dict:
        """
        Update-if-exists-else-create semantics, matching the bash script:
          1) Resolve EFFECTIVE GUID from item number
          2) Resolve WORKING revision GUID (fail if none)
          3) Find existing file by exact filename (WORKING first, then EFFECTIVE)
             - If found: POST /files/{fileGuid}/content (multipart)
             - Else:     POST /items/{workingGuid}/files (multipart) with file.edition
        """
        return self._api_upload_or_update_file(
            item_number=item_number,
            file_path=file_path,
            reference=reference,
            title=title,
            category_name=category_name,
            file_format=file_format,
            description=description,
            primary=primary,
            latest_edition_association=latest_edition_association,
            edition=edition,
        )

    def get_bom(
        self,
        item_number: str,
        revision: Optional[str] = None,
        *,
        recursive: bool = False,
        max_depth: Optional[int] = None,
    ) -> List[Dict]:
        """
        Return a normalized list of BOM lines for the given item.

        By default this fetches the EFFECTIVE (approved) revision's BOM.
        Use revision="WORKING" or a specific label (e.g., "B2") to override.

        If recursive=True, expand subassemblies depth-first. max_depth limits the recursion
        depth (1 = only direct children). If omitted, recursion is unlimited.
        """
        selector = (revision or "EFFECTIVE").strip()
        out: List[Dict] = []
        self._bom_expand(
            root_item=item_number,
            selector=selector,
            out=out,
            recursive=recursive,
            max_depth=max_depth,
            _level=0,
            _seen=set(),
        )
        return out

    # === Internal: single fetch + normalization (your original logic) ===

    def _fetch_bom_normalized(self, item_number: str, selector: str) -> List[Dict]:
        """
        Fetch and normalize the BOM for item_number with the given revision selector.
        Falls back WORKING -> EFFECTIVE if selector is WORKING and no WORKING exists.
        """
        # 1) Resolve the exact revision GUID we want the BOM for
        try:
            target_guid = self._api_resolve_revision_guid(item_number, selector)
        except ArenaError:
            if selector.strip().upper() == "WORKING":
                # fallback: try EFFECTIVE for children that don't have a WORKING revision
                target_guid = self._api_resolve_revision_guid(item_number, "EFFECTIVE")
            else:
                raise

        # 2) GET /items/{guid}/bom
        url = f"{self._api_base()}/items/{target_guid}/bom"
        self._log(f"GET {url}")
        r = self.session.get(url)
        r.raise_for_status()
        data = self._ensure_json(r)

        rows = data.get("results", data if isinstance(data, list) else [])
        norm: List[Dict] = []
        for row in rows:
            itm = row.get("item", {}) if isinstance(row, dict) else {}
            norm.append(
                {
                    # association/line
                    "guid": row.get("guid"),
                    "lineNumber": row.get("lineNumber"),
                    "notes": row.get("notes"),
                    "quantity": row.get("quantity"),
                    "refDes": row.get("refDes")
                    or row.get("referenceDesignators")
                    or "",
                    # child item
                    "itemGuid": itm.get("guid") or itm.get("id"),
                    "itemNumber": itm.get("number"),
                    "itemName": itm.get("name"),
                    "itemRevision": itm.get("revisionNumber"),
                    "itemRevisionStatus": itm.get("revisionStatus"),
                    "itemUrl": (itm.get("url") or {}).get("api"),
                    "itemAppUrl": (itm.get("url") or {}).get("app"),
                }
            )
        return norm

    # === Internal: recursive expansion ===

    def _bom_expand(
        self,
        *,
        root_item: str,
        selector: str,
        out: List[Dict],
        recursive: bool,
        max_depth: Optional[int],
        _level: int,
        _seen: set,
    ) -> None:
        # avoid cycles
        if root_item in _seen:
            return
        _seen.add(root_item)

        rows = self._fetch_bom_normalized(root_item, selector)

        # attach level and parentNumber (useful in JSON + for debugging)
        for r in rows:
            r["level"] = _level
            r["parentNumber"] = root_item
            out.append(r)

        if not recursive:
            return

        # depth check: if max_depth=1, only expand children once (level 0 -> level 1)
        if max_depth is not None and _level >= max_depth:
            return

        # expand each child that looks like an assembly (if it has a BOM; empty BOM is okay)
        for r in rows:
            child_num = r.get("itemNumber")
            if not child_num:
                continue
            try:
                # Recurse; keep same selector, with WORKING->EFFECTIVE fallback handled in _fetch_bom_normalized
                self._bom_expand(
                    root_item=child_num,
                    selector=selector,
                    out=out,
                    recursive=True,
                    max_depth=max_depth,
                    _level=_level + 1,
                    _seen=_seen,
                )
            except ArenaError:
                # Child might not have a BOM; skip silently
                continue

    def _api_base(self) -> str:
        return self.cfg.base_url.rstrip("/")

    def _api_get_latest_approved(self, item_number: str) -> str:
        item_guid = self._api_resolve_item_guid(item_number)
        url = f"{self._api_base()}/items/{item_guid}/revisions"
        self._log(f"GET {url}")
        r = self.session.get(url)
        if r.status_code == 404:
            raise ArenaError(f"Item {item_number} not found")
        r.raise_for_status()
        data = self._ensure_json(r)
        revs = data.get("results", data if isinstance(data, list) else [])
        if not isinstance(revs, list):
            raise ArenaError(f"Unexpected revisions payload for item {item_number}")

        # Arena marks the currently effective (approved) revision as:
        #   - revisionStatus == "EFFECTIVE"   (string)
        #   - OR status == 1                  (numeric)
        effective = [
            rv
            for rv in revs
            if (str(rv.get("revisionStatus") or "").upper() == "EFFECTIVE")
            or (rv.get("status") == 1)
        ]
        if not effective:
            raise ArenaError(f"No approved/released revisions for item {item_number}")

        # Prefer the one that is not superseded; otherwise fall back to the most recently superseded.
        current = next(
            (rv for rv in effective if not rv.get("supersededDateTime")), None
        )
        if not current:
            # sort by supersededDateTime (None last) then by number/name as a stable tie-breaker
            def _sd(rv):
                dt = rv.get("supersededDateTime")
                return dt or "0000-00-00T00:00:00Z"

            effective.sort(key=_sd)
            current = effective[-1]

        # The human-visible revision is under "number" (e.g., "B3"); fall back defensively.
        rev_label = (
            current.get("number") or current.get("name") or current.get("revision")
        )
        if not rev_label:
            raise ArenaError(
                f"Could not determine revision label for item {item_number}"
            )
        return rev_label

    def _api_list_files(self, item_number: str) -> List[Dict]:
        item_guid = self._api_resolve_item_guid(item_number)
        url = f"{self._api_base()}/items/{item_guid}/files"
        self._log(f"GET {url}")
        r = self.session.get(url)
        r.raise_for_status()
        data = self._ensure_json(r)
        rows = data.get("results", data if isinstance(data, list) else [])
        norm: List[Dict] = []
        for row in rows:
            f = row.get("file", {}) if isinstance(row, dict) else {}
            file_guid = f.get("guid") or f.get("id")
            norm.append(
                {
                    "id": row.get("guid") or row.get("id"),
                    "fileGuid": file_guid,
                    "name": f.get("name") or f.get("title"),
                    "title": f.get("title"),
                    "filename": f.get("name") or f.get("title"),
                    "size": f.get("size"),
                    "haveContent": f.get("haveContent", True),
                    "downloadUrl": (
                        f"{self._api_base()}/files/{file_guid}/content"
                        if file_guid
                        else None
                    ),
                    "edition": f.get("edition"),
                    "updatedAt": f.get("lastModifiedDateTime")
                    or f.get("lastModifiedDate")
                    or f.get("creationDateTime"),
                    "attachmentGroupGuid": row.get("guid"),
                }
            )
        return norm

    def _api_resolve_revision_guid(self, item_number: str, selector: str | None) -> str:
        """Return the item GUID for the requested revision selector."""
        # Resolve base item (effective) guid from number
        effective_guid = self._api_resolve_item_guid(item_number)

        # If no selector, we default to EFFECTIVE
        sel = (selector or "EFFECTIVE").strip().upper()

        # Fetch revisions
        url = f"{self._api_base()}/items/{effective_guid}/revisions"
        self._log(f"GET {url}")
        r = self.session.get(url)
        r.raise_for_status()
        data = self._ensure_json(r)
        revs = data.get("results", data if isinstance(data, list) else [])

        def pick(pred):
            for rv in revs:
                if pred(rv):
                    return rv.get("guid")
            return None

        # Named selectors
        if sel in {"WORKING"}:
            guid = pick(
                lambda rv: (rv.get("revisionStatus") or "").upper() == "WORKING"
                or rv.get("status") == 0
            )
            if not guid:
                raise ArenaError("No WORKING revision exists for this item.")
            return guid

        if sel in {"EFFECTIVE", "APPROVED", "RELEASED"}:
            # Prefer the one not superseded
            eff = [
                rv
                for rv in revs
                if (rv.get("revisionStatus") or "").upper() == "EFFECTIVE"
                or rv.get("status") == 1
            ]
            if not eff:
                raise ArenaError(
                    "No approved/effective revision exists for this item. Try using revision 'WORKING'."
                )
            current = next(
                (rv for rv in eff if not rv.get("supersededDateTime")), eff[-1]
            )
            return current.get("guid")

        # Specific label (e.g., "A", "B2")
        guid = pick(
            lambda rv: (rv.get("number") or rv.get("name"))
            and str(rv.get("number") or rv.get("name")).upper() == sel
        )
        if not guid:
            raise ArenaError(f'Revision "{selector}" not found for item {item_number}.')
        return guid

    def _api_list_files_by_item_guid(self, item_guid: str) -> list[dict]:
        url = f"{self._api_base()}/items/{item_guid}/files"
        self._log(f"GET {url}")
        r = self.session.get(url)
        r.raise_for_status()
        data = self._ensure_json(r)
        rows = data.get("results", data if isinstance(data, list) else [])
        # … keep existing normalization from _api_list_files() …
        norm = []
        for row in rows:
            f = row.get("file", {}) if isinstance(row, dict) else {}
            file_guid = f.get("guid") or f.get("id")
            norm.append(
                {
                    "id": row.get("guid") or row.get("id"),
                    "fileGuid": file_guid,
                    "name": f.get("name") or f.get("title"),
                    "filename": f.get("name") or f.get("title"),
                    "size": f.get("size"),
                    "haveContent": f.get("haveContent", True),
                    "downloadUrl": (
                        f"{self._api_base()}/files/{file_guid}/content"
                        if file_guid
                        else None
                    ),
                    "edition": f.get("edition"),
                    "updatedAt": f.get("lastModifiedDateTime")
                    or f.get("lastModifiedDate")
                    or f.get("creationDateTime"),
                    "attachmentGroupGuid": row.get("guid"),
                }
            )
        return norm

    def _api_upload_or_update_file(
        self,
        *,
        item_number: str,
        file_path: Path,
        reference: Optional[str],
        title: Optional[str],
        category_name: str,
        file_format: Optional[str],
        description: Optional[str],
        primary: bool,
        latest_edition_association: bool,
        edition: str,
    ) -> Dict:
        if not file_path.exists() or not file_path.is_file():
            raise ArenaError(f"File not found: {file_path}")

        filename = file_path.name  # Use truncated SHA256 hash if no edition is provided
        if not edition:
            # Arena seems to only accept 16 characters of edition information.
            # The hex digest gives 16 hex × 4 bits = 64 bits of entropy.
            # Less than a million files, collision risk is practically zero (~1 / 10^8).
            edition = sha256_file(file_path)[:16]

        # 0) Resolve EFFECTIVE revision guid from item number
        effective_guid = self._api_resolve_item_guid(item_number)

        # 1) Resolve WORKING revision guid
        revs_url = f"{self._api_base()}/items/{effective_guid}/revisions"
        self._log(f"GET {revs_url}")
        r = self.session.get(revs_url)
        r.raise_for_status()
        data = self._ensure_json(r)
        rows = data.get("results", data if isinstance(data, list) else [])
        working_guid = None
        for rv in rows:
            if (str(rv.get("revisionStatus") or "").upper() == "WORKING") or (
                rv.get("status") == 0
            ):
                working_guid = rv.get("guid")
                break
        if not working_guid:
            raise ArenaError(
                "No WORKING revision exists for this item. Create a working revision in Arena, then retry."
            )

        # Helper to list associations for a given item/revision guid
        def _list_assocs(item_guid: str) -> list:
            url = f"{self._api_base()}/items/{item_guid}/files"
            self._log(f"GET {url}")
            lr = self.session.get(url)
            lr.raise_for_status()
            payload = self._ensure_json(lr)
            return payload.get("results", payload if isinstance(payload, list) else [])

        # Try to find existing association by exact filename (WORKING first, then EFFECTIVE)
        filename = file_path.name
        assoc = None
        for guid in (working_guid, effective_guid):
            assocs = _list_assocs(guid)
            # prefer primary && latestEditionAssociation, then any by name
            prim_latest = [
                a
                for a in assocs
                if a.get("primary")
                and a.get("latestEditionAssociation")
                and ((a.get("file") or {}).get("name") == filename)
            ]
            if prim_latest:
                assoc = prim_latest[0]
                break
            any_by_name = [
                a for a in assocs if (a.get("file") or {}).get("name") == filename
            ]
            if any_by_name:
                assoc = any_by_name[0]
                break

        # If an existing file is found: update its content (new edition)
        if assoc:
            file_guid = (assoc.get("file") or {}).get("guid")
            if not file_guid:
                raise ArenaError("Existing association found but no file.guid present.")
            post_url = f"{self._api_base()}/files/{file_guid}/content"
            self._log(f"POST {post_url} (multipart content update)")
            with open(file_path, "rb") as fp:
                files = {"content": (filename, fp, "application/octet-stream")}
                existing_ct = self.session.headers.pop("Content-Type", None)
                try:
                    ur = self.session.post(post_url, files=files)
                finally:
                    if existing_ct is not None:
                        self.session.headers["Content-Type"] = existing_ct
            ur.raise_for_status()

            # Update the edition label on the File itself
            try:
                put_url = f"{self._api_base()}/files/{file_guid}"
                self._log(f"PUT {put_url} (set edition={edition})")
                pr = self.session.put(put_url, json={"edition": str(edition)})
                pr.raise_for_status()
            except requests.HTTPError as e:
                # Don't fail the whole operation if the label update is rejected
                self._log(f"Edition update failed for {file_guid}: {e}")

            # Many tenants return 201 with no JSON for content updates. Be flexible.
            data = self._try_json(ur)
            if data is None:
                # Synthesize a small success payload with whatever we can glean.
                return {
                    "ok": True,
                    "status": ur.status_code,
                    "fileGuid": file_guid,
                    "location": ur.headers.get("Location"),
                    "edition": str(edition),
                }
            return data

        # Else: create a new association on WORKING
        # 2) Resolve file category guid by name (default: CAD Data)
        cats_url = f"{self._api_base()}/settings/files/categories"
        self._log(f"GET {cats_url}")
        r = self.session.get(cats_url)
        r.raise_for_status()
        cats = self._ensure_json(r).get("results", [])
        cat_guid = None
        for c in cats:
            if c.get("name") == category_name and (c.get("parentCategory") or {}).get(
                "name"
            ) in {"Internal File", None}:
                cat_guid = c.get("guid")
                break
        if not cat_guid:
            raise ArenaError(
                f'File category "{category_name}" not found or not allowed.'
            )

        # 3) Prepare multipart (create association)
        title = title or file_path.name
        file_format = file_format or (
            file_path.suffix[1:].lower() if file_path.suffix else "bin"
        )
        description = description or "Uploaded via gladiator"
        files = {
            "content": (
                file_path.name,
                open(file_path, "rb"),
                "application/octet-stream",
            )
        }

        # NOTE: nested field names are sent in `data`, not `files`
        data_form = {
            "file.title": title,
            "file.description": description,
            "file.category.guid": cat_guid,
            "file.format": file_format,
            "file.edition": str(edition),
            "file.storageMethodName": "FILE",
            "file.private": "false",
            "primary": "true" if primary else "false",
            "latestEditionAssociation": (
                "true" if latest_edition_association else "false"
            ),
        }
        if reference:
            data_form["reference"] = reference

        # 4) POST to /items/{workingGuid}/files (multipart). Ensure Content-Type not pinned.
        post_url = f"{self._api_base()}/items/{working_guid}/files"
        self._log(f"POST {post_url} (multipart)")

        with open(file_path, "rb") as fp:
            files = {"content": (filename, fp, "application/octet-stream")}
            existing_ct = self.session.headers.pop("Content-Type", None)
            try:
                cr = self.session.post(post_url, data=data_form, files=files)
            finally:
                if existing_ct is not None:
                    self.session.headers["Content-Type"] = existing_ct
        cr.raise_for_status()
        resp = self._ensure_json(cr)

        # Normalize common fields we use elsewhere
        row = resp if isinstance(resp, dict) else {}
        f = row.get("file", {})

        # Ensure the edition label is exactly what we asked for (some tenants ignore form edition)
        try:
            file_guid_created = (f or {}).get("guid")
            if file_guid_created and str(edition):
                put_url = f"{self._api_base()}/files/{file_guid_created}"
                self._log(f"PUT {put_url} (set edition={edition})")
                pr = self.session.put(put_url, json={"edition": str(edition)})
                pr.raise_for_status()
                # Update local 'f' edition if the PUT succeeded
                f["edition"] = str(edition)
        except requests.HTTPError as e:
            self._log(
                f"Edition update after create failed for {file_guid_created}: {e}"
            )

        return {
            "associationGuid": row.get("guid"),
            "primary": row.get("primary"),
            "latestEditionAssociation": row.get("latestEditionAssociation"),
            "file": {
                "guid": f.get("guid"),
                "title": f.get("title"),
                "name": f.get("name"),
                "size": f.get("size"),
                "format": f.get("format"),
                "category": (f.get("category") or {}).get("name"),
                "edition": f.get("edition") or str(edition),
                "lastModifiedDateTime": f.get("lastModifiedDateTime"),
            },
            "downloadUrl": (
                f"{self._api_base()}/files/{(f or {}).get('guid')}/content"
                if f.get("guid")
                else None
            ),
        }

    def _api_resolve_item_guid(self, item_number: str) -> str:
        url = f"{self._api_base()}/items/"
        params = {"number": item_number, "limit": 1, "responseview": "minimal"}
        self._log(f"GET {url} params={params}")
        r = self.session.get(url, params=params)
        r.raise_for_status()
        data = self._ensure_json(r)
        results = data.get("results") if isinstance(data, dict) else data
        if not results:
            raise ArenaError(f"Item number {item_number} not found")
        guid = (
            results[0].get("guid") or results[0].get("id") or results[0].get("itemId")
        )
        if not guid:
            raise ArenaError("API response missing item GUID")
        return guid

    def _run(self, cmd: str) -> Tuple[int, str, str]:
        proc = subprocess.run(
            cmd, shell=True, check=False, capture_output=True, text=True
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
