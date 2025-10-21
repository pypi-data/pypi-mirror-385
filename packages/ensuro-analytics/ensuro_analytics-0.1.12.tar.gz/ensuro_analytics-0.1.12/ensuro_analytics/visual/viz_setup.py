"""
Setup plotting libraries
"""

from pathlib import Path

import matplotlib as mpl
import plotly.graph_objects as go
import plotly.io as pio
import yaml

# Get directory of this python file

DIR = Path(__file__).parent.absolute()
VISUAL_CONFIGS_PATH = DIR / "visual_configs.yaml"

_ensuro_colors = None


def get_ensuro_colors() -> dict:
    global _ensuro_colors
    if _ensuro_colors is not None:
        return _ensuro_colors
    else:
        with open(VISUAL_CONFIGS_PATH) as f:
            _ensuro_colors = yaml.safe_load(f)["ensuro_colors"]
        return _ensuro_colors


class VizSetup:
    def __init__(self, configs: str | None = None):
        self.configs = configs

    def _get_params(self) -> dict:
        """
        Loads default parameters for boh matplotlib and plotly from a yaml file
        """
        if self.configs is not None:
            with open(self.configs) as f:
                _params = yaml.safe_load(f)
            return _params
        else:
            with open(VISUAL_CONFIGS_PATH) as f:
                _params = yaml.safe_load(f)
            return _params

    def _get_mpl_params(self) -> dict:
        """
        Loads parameters for matplotlib
        """
        if self.configs is not None:
            with open(self.configs) as f:
                _params = yaml.safe_load(f)["matplotlib"]
            return _params
        else:
            with open(VISUAL_CONFIGS_PATH) as f:
                _params = yaml.safe_load(f)["matplotlib"]
            return _params

    def _get_plotly_params(self) -> dict:
        """
        Loads parameters for plotly
        """
        if self.configs is not None:
            with open(self.configs) as f:
                _params = yaml.safe_load(f)["plotly"]
            return _params
        else:
            with open(VISUAL_CONFIGS_PATH) as f:
                _params = yaml.safe_load(f)["plotly"]
            return _params

    def setup_matplotlib(self) -> None:
        # custom_rcparams = self._get_mpl_params()
        custom_rcparams = self._get_mpl_params()

        # Handle the color cycle separately
        if "axes.prop_cycle_colors" in custom_rcparams:
            colors = custom_rcparams.pop("axes.prop_cycle_colors")
            mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=colors)

        mpl.rcParams.update(custom_rcparams)
        return None

    def setup_plotly(self) -> None:
        # plotly_params = self._mpl_params_to_plotly_template()
        plotly_plain = self._get_plotly_params()
        plotly_params = dict(layout=go.Layout(plotly_plain["layout"]), data=plotly_plain["data"])
        pio.templates["ensuro"] = plotly_params
        pio.templates.default = "ensuro"
        return None

    @staticmethod
    def to_pink_blue_green_rotation() -> None:
        ensuro_colors = get_ensuro_colors()
        colors = [
            ensuro_colors["fluo"][0],
            ensuro_colors["blues"][2],
            ensuro_colors["fluo"][1],
            ensuro_colors["blues"][1],
        ]
        # For matplotlib
        mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=colors)
        # For plotly
        pio.templates["ensuro"]["layout"]["colorway"] = colors
        return None

    def to_configs_rotation(self) -> None:
        mpl_params = self._get_mpl_params()
        colors = mpl_params.get("axes.prop_cycle_colors", None)
        if colors is None:
            Warning("No color cycle found in configs")
        else:
            # For matplotlib
            mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=colors)
            # For plotly
            pio.templates["ensuro"]["layout"]["colorway"] = colors
        return None


def setup_matplotlib(configs: str | None = None) -> VizSetup:
    """
    Setup matplotlib configuration
    """
    vizsetup = VizSetup(configs=configs)
    vizsetup.setup_matplotlib()
    return vizsetup


def setup_plotly(configs: str | None = None) -> VizSetup:
    """
    Setup plotly configuration
    """
    vizsetup = VizSetup(configs=configs)
    vizsetup.setup_plotly()
    return vizsetup
