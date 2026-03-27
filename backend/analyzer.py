import csv
import os
from urllib.parse import urlparse

import requests
import urllib3

# Disable insecure request warnings when bypassing SSL verification.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_KNOWN_URL_LABELS = {}
_KNOWN_DOMAIN_LABELS = {}
_DATASET_LOADED = False


def _normalize_url_for_lookup(url: str) -> str:
    if not url:
        return ""
    working = url.strip()
    if not working.startswith(("http://", "https://")):
        working = f"http://{working}"
    parsed = urlparse(working)
    host = (parsed.netloc or "").lower()
    if ":" in host:
        host = host.split(":", 1)[0]
    path = parsed.path or ""
    normalized = f"{host}{path}".rstrip("/")
    return normalized


def _extract_domain(url: str) -> str:
    if not url:
        return ""
    working = url.strip()
    if not working.startswith(("http://", "https://")):
        working = f"http://{working}"
    parsed = urlparse(working)
    host = (parsed.netloc or "").lower()
    if ":" in host:
        host = host.split(":", 1)[0]
    return host


def _load_resource_data() -> None:
    global _DATASET_LOADED
    if _DATASET_LOADED:
        return

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(project_root, "phishing_url_dataset_unique.csv")
    if not os.path.exists(dataset_path):
        _DATASET_LOADED = True
        return

    with open(dataset_path, "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            raw_url = (row.get("url") or "").strip()
            raw_label = (row.get("label") or "").strip()
            if not raw_url or raw_label not in {"0", "1"}:
                continue

            label = int(raw_label)
            normalized = _normalize_url_for_lookup(raw_url)
            domain = _extract_domain(raw_url)
            if normalized:
                _KNOWN_URL_LABELS[normalized] = label
            if domain and domain not in _KNOWN_DOMAIN_LABELS:
                _KNOWN_DOMAIN_LABELS[domain] = label

    _DATASET_LOADED = True


def _lookup_in_resources(url: str):
    _load_resource_data()
    normalized = _normalize_url_for_lookup(url)
    domain = _extract_domain(url)

    if normalized in _KNOWN_URL_LABELS:
        return _KNOWN_URL_LABELS[normalized], "Exact URL match in dataset"

    if domain in _KNOWN_DOMAIN_LABELS:
        return _KNOWN_DOMAIN_LABELS[domain], "Domain match in dataset"

    return None, "No dataset match"


def analyze_website(url: str):
    """
    Detection strategy requested by user:
    1) Check local resource dataset first (known phishing/safe URLs).
    2) If not found, do real-time reachability check:
       - reachable website => Safe
       - unreachable website => Phishing
    """
    features = {
        "Target": url,
        "Source Check": "Checking dataset...",
        "Live Status": "Checking connectivity..."
    }

    label, source_detail = _lookup_in_resources(url)
    features["Source Check"] = source_detail

    if label is not None:
        if label == 1:
            features["Live Status"] = "Skipped (known phishing from dataset)"
            features["Decision"] = "Phishing by resource data"
            return "Phishing", 99.0, features

        features["Live Status"] = "Skipped (known safe from dataset)"
        features["Decision"] = "Safe by resource data"
        return "Safe", 99.0, features

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=6, verify=False, allow_redirects=True)
        features["Live Status"] = f"Online (HTTP {response.status_code})"
        features["Decision"] = "Safe by real-time availability check"
        return "Safe", 94.0, features
    except requests.RequestException:
        features["Live Status"] = "Offline / Unreachable"
        features["Decision"] = "Phishing by real-time availability check"
        return "Phishing", 94.0, features
