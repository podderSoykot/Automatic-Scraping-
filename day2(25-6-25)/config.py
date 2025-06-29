# -----------------------------------------------------------------------------
# Configurable settings
# -----------------------------------------------------------------------------

SCRAPEOPS_API_KEY = "4f65ae0a-b220-4550-a560-321756f96d11"

SERVICES = [
    "Photography",
    "Videography",
    "Drone Photography",
    "Drone Video",
    "3D Virtual Tour",
    "Floor Plans",
    "Virtual Staging",
    "Twilight Photography",
    "Agent Intro/Outro",
    "Voiceover",
]

CITY_LIST_SOURCE = "us"  # or path to custom CSV of cities/states

SCRAPE_TIMEOUT = 10  # seconds
RETRY_COUNT = 3
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/90.0.4430.93 Safari/537.36")

OUTPUT_FOLDER = "output/"
INTERPOLATION_NEAREST_K = 5
REGIONAL_ADJUSTMENT_FACTOR = 1.1  # use higher cost-of-living +10%
