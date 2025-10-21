# Export the version given in project metadata
from importlib import metadata

__version__ = metadata.version(__package__)
del metadata

from _pylinearfold import fold
from _pylinearpartition import partition
