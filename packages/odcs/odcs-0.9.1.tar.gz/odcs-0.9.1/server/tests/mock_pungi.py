import sys
from mock import MagicMock

# Mock pungi module as it's hard to install all the required deps in virtual env.
sys.modules["pungi.compose"] = MagicMock()
