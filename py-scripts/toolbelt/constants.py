import os

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# k8s config dir hard coding
INTERNAL_DIR = os.path.abspath(os.path.join(ROOT_DIR, "../../9c-internal/"))
ONBOARDING_DIR = os.path.abspath(os.path.join(ROOT_DIR, "../../9c-onboarding/"))
MAIN_DIR = os.path.abspath(os.path.join(ROOT_DIR, "../../9c-main/"))

RELEASE_BASE_URL = "https://release.nine-chronicles.com"
MAIN_REPO = "9c-k8s-config"
