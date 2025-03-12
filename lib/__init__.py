from srcs.utils import get_project_root

from plotly import graph_objects as go
from plotly.subplots import make_subplots

from .ana_functions import *
from .cal_functions import *
from .cut_functions import *
from .dec_functions import *
from .fig_config import (
    add_grid,
    figure_features,
    format_coustom_plotly,
)  # <--- import customized functions
from .fit_functions import *
from .group_functions import *
from .head_functions import *
from .io_functions import *
from .minuit_functions import *
from .ply_functions import *
from .sty_functions import style_selector, get_prism_colors, get_color
from .unit_functions import *
from .vis_functions import *

root = get_project_root()