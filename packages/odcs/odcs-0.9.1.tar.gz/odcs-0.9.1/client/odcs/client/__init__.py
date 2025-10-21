import pkg_resources

try:
    version = pkg_resources.get_distribution("odcs").version
except pkg_resources.DistributionNotFound:
    version = "unknown"
