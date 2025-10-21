import logging

import lmfit
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from labcodes import misc, plotter
from labcodes.calc import Calculator, dept
from scipy.signal import find_peaks

logger = logging.getLogger(__name__)


class EnrCross(Calculator):
    """Model for the avoid level crossing on spectrums."""

    x = np.linspace(3.5, 4.5, 21)
    g = 0.1
    k1 = 0
    b1 = 4
    k2 = 1
    b2 = 0

    @dept
    def f1(self, x, k1, b1):
        return k1 * x + b1

    @dept
    def f2(self, x, k2, b2):
        return k2 * x + b2

    @dept
    def center(self, k1, b1, k2, b2):
        x = (b1 - b2) / (k2 - k1)
        y = k1 * x + b1
        return x, y

    @dept
    def coupled_freqs(self, g, f1, f2):
        tr = f1 + f2
        det = f1 * f2 - g**2
        fdown = (tr - np.sqrt(tr**2 - 4 * det)) / 2
        fup = (tr + np.sqrt(tr**2 - 4 * det)) / 2
        return fdown, fup


class FitEnrCross:
    def __init__(self, upper: pd.DataFrame, lower: pd.DataFrame):
        """upper, lower with columns "x" and "freq".

        e.g. `upper = pd.DataFrame(dict(x=[-1, 0, 1], freq=[4,5,6])))`

        e.g. `lower = pd.DataFrame(dict(x=[-0.5, 0.5, 1], freq=[5,5,5])))`
        """
        self.upper = upper[["x", "freq"]]
        self.lower = lower[["x", "freq"]]
        self.params = None
        self.guess_and_update_params()
        self.result: lmfit.minimizer.MinimizerResult = None
        try:
            self.fit()
        except:
            logger.exception("Error in fitting.")

    def residue(self, pars: lmfit.Parameters):
        model = EnrCross(**pars.valuesdict())
        resi_dn = self.lower["freq"] - model.coupled_freqs(x=self.lower["x"])[0]
        resi_up = self.upper["freq"] - model.coupled_freqs(x=self.upper["x"])[1]
        return np.concatenate([resi_dn, resi_up])

    def fit(self) -> lmfit.minimizer.MinimizerResult:
        self.result = lmfit.minimize(self.residue, self.params)
        return self.result

    def guess_and_update_params(self) -> lmfit.Parameters:
        try:
            g = self.guess_g()["g"]
            kbs = self.guess_f12_vs_x()
        except:
            logger.exception("Failed to guess parameters. Using default values.")
            g = 0.1
            kbs = dict(k1=0, b1=4, k2=1, b2=0)
        params = lmfit.Parameters()
        params.set(g=g, **kbs)
        self.params = params
        return params

    def guess_g(self, xp: np.ndarray = None) -> dict[str, float]:
        if xp is None:
            xmin = min(self.upper["x"].min(), self.lower["x"].min())
            xmax = max(self.upper["x"].max(), self.lower["x"].max())
            xp = np.linspace(xmin, xmax, 1001)
        # up_interp = np.interp(xp, self.upper["x"], self.upper["freq"])
        # lo_interp = np.interp(xp, self.lower["x"], self.lower["freq"])
        up_interp = misc.simple_interp(xp, self.upper["x"], self.upper["freq"])
        lo_interp = misc.simple_interp(xp, self.lower["x"], self.lower["freq"])
        imin = np.argmin(up_interp - lo_interp)
        g = 0.5 * (up_interp - lo_interp)[imin]
        x_res = xp[imin]
        fdown_res = lo_interp[imin]
        fup_res = up_interp[imin]
        # return g, x_res, fdown_res, fup_res
        return dict(g=g, x_res=x_res, fdown_res=fdown_res, fup_res=fup_res)

    def guess_f12_vs_x(self) -> dict[str, float]:
        x1l, y1l = self.upper.iloc[0, :][["x", "freq"]]
        x1r, y1r = self.lower.iloc[-1, :][["x", "freq"]]
        x2l, y2l = self.lower.iloc[0, :][["x", "freq"]]
        x2r, y2r = self.upper.iloc[-1, :][["x", "freq"]]
        k1 = (y1r - y1l) / (x1r - x1l)
        b1 = y1l - k1 * x1l
        k2 = (y2r - y2l) / (x2r - x2l)
        b2 = y2l - k2 * x2l
        return dict(k1=k1, b1=b1, k2=k2, b2=b2)

    @property
    def result_model(self):
        return EnrCross(**self.result.params.valuesdict())

    @property
    def init_model(self):
        return EnrCross(**self.params.valuesdict())

    def __getitem__(self, key: str):
        if self.result is None:
            ret = self.params[key].value
        else:
            if key == "chi":
                ret = np.sqrt(self.result.chisqr)
            elif key.endswith("_err"):
                ret = self.result.params[key[:-4]].stderr
            else:
                ret = self.result.params[key].value
        
        if ret is None:
            return np.nan
        else:
            return ret

    def plot(
        self,
        ax: plt.Axes = None,
        x: np.ndarray = None,
        plot_data: bool = True,
        plot_init: bool = True,
        plot_center: bool = True,
        plot_bare: bool = False,
    ):
        if ax is None:
            _, ax = plt.subplots()
            ax.set_xlabel("x")
            ax.set_ylabel("freq")
        if x is None:
            xmin = min(self.upper["x"].min(), self.lower["x"].min())
            xmax = max(self.upper["x"].max(), self.lower["x"].max())
            x = np.linspace(xmin, xmax, 1001)

        if plot_data:
            ax.scatter("x", "freq", data=self.lower, color="C0")
            ax.scatter("x", "freq", data=self.upper, color="C1")

        if self.result is not None:
            freqs = self.result_model.coupled_freqs(x=x)
            ax.plot(x, freqs[0], color="C0", scaley=False)
            ax.plot(x, freqs[1], color="C1", scaley=False)

        if plot_init:
            freqs = self.init_model.coupled_freqs(x=x)
            ax.plot(x, freqs[0], color="C0", ls=":", scaley=False)
            ax.plot(x, freqs[1], color="C1", ls=":", scaley=False)

        if plot_bare:
            ax.plot(x, self["k1"] * x + self["b1"], scaley=False)
            ax.plot(x, self["k2"] * x + self["b2"], scaley=False)

        if plot_center:
            if self.result is not None:
                model = self.result_model
            else:
                model = self.init_model
            x, y = model.center()
            fup, fdown = model.coupled_freqs(x=x)
            ax.plot([x, x], [fdown, fup], "k-", scaley=False)
            if self["k1"] + self["k2"] > 0:
                ax.annotate(
                    f'g={self["g"]:.3f}±{self["g_err"]:.3f}\n({x:.3f}, {y:.3f})',
                    (1, 0),
                    xycoords="axes fraction",
                    ha="right",
                    va="bottom",
                    path_effects=[plotter.txt_effect()],
                )
            else:
                ax.annotate(
                    f'g={self["g"]:.3f}±{self["g_err"]:.3f}\n({x:.3f}, {y:.3f})',
                    (0, 0),
                    xycoords="axes fraction",
                    ha="left",
                    va="bottom",
                    path_effects=[plotter.txt_effect()],
                )
        return ax

    @staticmethod
    def extract_from_2d_spec(
        df: pd.DataFrame,
        xname: str | int = 0,
        yname: str | int = 1,
        zname: str | int = 2,
        div_x: float = None,
        upper_at_left: bool = True,
    ):
        if isinstance(xname, int):
            xname = df.columns[xname]
        if isinstance(yname, int):
            yname = df.columns[yname]
        if isinstance(zname, int):
            zname = df.columns[zname]
        if div_x is None:
            div_x = df[xname].mean()

        upper = []
        lower = []
        for x in df[xname].unique():
            tr = df.query(f"{xname}=={x}").reset_index(drop=True)
            peaks, *_ = find_peaks(tr[zname])
            if np.size(peaks) >= 2:
                upper.append({"x": x, "freq": tr.loc[peaks[1], yname]})
                lower.append({"x": x, "freq": tr.loc[peaks[0], yname]})
            elif np.size(peaks) == 1:
                if ((x <= div_x) and upper_at_left) or (
                    (x > div_x) and (not upper_at_left)
                ):
                    upper.append({"x": x, "freq": tr.loc[peaks[0], yname]})
                else:
                    lower.append({"x": x, "freq": tr.loc[peaks[0], yname]})
            else:
                logger.warning(f"No peaks found at {xname}={x}")

        upper = pd.DataFrame.from_records(upper)
        lower = pd.DataFrame.from_records(lower)
        return upper, lower

    @classmethod
    def from_2d_spec(
        cls,
        df: pd.DataFrame,
        xname: str | int = 0,
        yname: str | int = 1,
        zname: str | int = 2,
        div_x: float = None,
    ):
        upper, lower = cls.extract_from_2d_spec(df, xname, yname, zname, div_x)
        return cls(upper, lower)


if __name__ == "__main__":
    mod = EnrCross()  # An arbitrary model to get example datas.
    upper = pd.DataFrame({"x": mod.x, "freq": mod["coupled_freqs"][1]})
    lower = pd.DataFrame({"x": mod.x, "freq": mod["coupled_freqs"][0]})

    xfit = FitEnrCross(upper, lower)
    # xfit2.params.set(g=dict(min=0, max=1))
    xfit.plot()
    xfit.result

    upper = pd.DataFrame({"x": -mod.x, "freq": mod["coupled_freqs"][1]})
    lower = pd.DataFrame({"x": -mod.x, "freq": mod["coupled_freqs"][0]})
    xfit2 = FitEnrCross(upper, lower)
    xfit2.plot(plot_bare=True)
    xfit2.result
