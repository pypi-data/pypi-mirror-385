import copy
import logging
from tqdm import trange
from pathlib import Path
from typing import Union

import lmfit
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d


logger = logging.getLogger(__name__)


class CurveFit(object):
    """Class encapsulating data, model and fit result for curve fitting.

    Examples:
        >>> def sine(x, amp, freq, phase):
        ...     return amp * np.sin(2*np.pi*freq*x + phase)
        >>> xdata = np.linspace(0, 1)
        >>> np.random.seed(0)
        >>> ydata = sine(xdata, 1.1, 1.1, 0.1) + np.random.normal(size=len(xdata), scale=0.1)
        >>> cfit = CurveFit(xdata, ydata, sine, dict(amp=1, freq=1, phase=0))
        >>> cfit.params
        chi          0.747171
        amp          1.117566
        amp_err      0.022657
        freq         1.076386
        freq_err     0.009642
        phase        0.178043
        phase_err    0.037869
        dtype: float64
        >>> cfit.plot()
        <Figure size 640x640 with 2 Axes>
    """
    def __init__(
        self, 
        xdata:np.ndarray, 
        ydata:np.ndarray, 
        model:lmfit.Model, 
        fit_kws: dict[str, float] = None,
        hold:bool=False, 
    ):
        if not isinstance(model, lmfit.Model) and callable(model):
            model = lmfit.Model(model)
        self.xdata = np.asarray(xdata)
        self.ydata = np.asarray(ydata)
        self.model = model
        self.result:lmfit.model.ModelResult = None
        self.params:pd.Series = None
        self.fit_kws = fit_kws if fit_kws is not None else {}

        if not hold:
            try:
                self.fit()
            except Exception:
                logger.exception("Error in fitting.")

    def _update_result(self, result:lmfit.model.ModelResult) -> None:
        self.result = result

        # Update params.
        d = {'chi': np.sqrt(result.chisqr)}
        for key in self.model.param_names:
            d[key] = result.params[key].value
            err = result.params[key].stderr
            if err is None:
                d[key+'_err'] = np.nan
            else:
                d[key+'_err'] = err
        self.params = pd.Series(d)

    def __getitem__(self, key):
        return self.params[key]

    @property
    def fit_report(self):
        return self.result.fit_report()
    
    @property
    def kws(self):
        """For quick access to fit parameters."""
        return {k: v.value for k, v in self.result.params.items() if v.expr is None}

    def fit(self, **kws) -> None:
        """Perform fit with given kws as initial values of parameters."""
        try:
            params = self.model.guess(self.ydata, x=self.xdata)
        except NotImplementedError:
            params = None
        except:
            logger.exception("Error in guessing parameters.")
            params = None

        if params is not None:
            for hint in self.model.param_hints:
                if 'value' in hint:
                    params[hint['name']].set(value=hint['value'])

        _kws = self.fit_kws.copy()
        _kws.update(kws)
        result = self.model.fit(self.ydata, x=self.xdata, params=params, **_kws)
        self._update_result(result)

    def fdata(self, x: Union[int, np.ndarray]=None) -> tuple[np.ndarray, np.ndarray]:
        """Return x and y values of fitted curve."""
        if x is None:
            return self.xdata, self.result.best_fit
        elif np.isscalar(x):
            ip = np.linspace(0, 1, num=len(self.xdata))
            i = np.linspace(0, 1, num=x)
            x = np.interp(i, ip, np.sort(self.xdata))
            return x, self.result.eval(x=x)
        else:
            return x, self.result.eval(x=x)

    def plot(self, show_init=False, x_for_fdata=None) -> plt.Figure:
        """Plot the fit result. If no result, plot data with guess params."""
        is_complex = np.iscomplexobj(self.ydata)
        if self.result is None: print("No fit result, plotting data with guess params.")
        if self.result is not None and not is_complex:
            return self.result.plot(show_init=show_init)
        
        fig, ax = plt.subplots()
        ax.set_title(self.model.name)
        if is_complex:
            ax.set(
                xlabel='Re(y)',
                ylabel='Im(y)',
                aspect='equal',
            )
            ax.plot(self.ydata.real, self.ydata.imag, 'o')
        else:
            ax.set(
                xlabel='x',
                ylabel='y',
            )
            ax.plot(self.xdata, self.ydata, 'o')

        if self.result is None:
            try:
                p_guess = self.model.guess(self.ydata, x=self.xdata)
                y_guess = self.model.eval(p_guess, x=self.xdata)
                if is_complex:
                    ax.plot(y_guess.real, y_guess.imag, '--', color='gray', label='guess')
                else:
                    ax.plot(self.xdata, y_guess, '--', color='gray', label='guess')
            except:
                logger.exception("Error in guessing parameters.")
        else:  # self.result is not None and is_complex.
            if show_init:
                y0 = self.result.init_fit
                if is_complex:
                    ax.plot(y0.real, y0.imag, '--', color='gray', label='init')
                else:
                    ax.plot(self.xdata, y0, '--', color='gray', label='init')

            fx, fy = self.fdata(x=x_for_fdata)
            if is_complex:
                ax.plot(fy.real, fy.imag, label='best fit')
            else:
                ax.plot(fx, fy, label='best fit')

        ax.legend()
        return ax
    

    @classmethod
    def from_result(cls, result:lmfit.model.ModelResult, xdata=None):
        if xdata is None:
            xdata = result.userkws['x']  # x for most of LabCodes models.
        ydata = result.data
        model = result.model
        cfit = cls(xdata, ydata, model, hold=True)
        cfit._update_result(result)
        return cfit

    @classmethod
    def load(cls, path:Path):
        raise NotImplementedError()  # TODO: require a dict of model def functions.

    def dump(self, path:Path):
        path = Path(path)
        path.touch()
        with path.open('w') as f:
            self.result.dump(f)


class BatchFit(object):
    """Hold a batch of data, fit them with lmfit.model like CurveFit and hold the results.

    Attributes:
        xbatch, ybatch: the fit datas.
        model: lmfit.Model.
        result: list(lmfit.ModelResult).
        num_of_fits: int.
        params: pandas.DataFrame, collection of fitted parameter values, stderrs, and chi.
        fbatch: 2d array, fitted data, same shape as ybatch.
    """
    def __init__(self, xbatch, ybatch, model, hold=False):
        """Initialize a batch fit.
        
        Args:
            xbatch, ybatch: 2d array with same shape.
                list of data traces which may has different length.
            model: lmfit.Model,
            hold: boolean,
                if False, try to do fit right after initialization.
        """
        self.xbatch = xbatch
        self.ybatch = ybatch
        self.model = model
        if not hold:
            try:
                self.fit()
            except:
                logger.exception("Error in fitting.")
        else:
            self.result = None

    @property
    def num_of_fits(self):
        return len(self.ybatch)

    @property
    def params(self):
        return self._params

    def get_params(self):
        """Return params from self.result."""

        params = {'chi': []}
        for key in self.model.param_names:
            params.update({key: [], key+'_err': []})

        for res in self.result:
            params['chi'].append(np.sqrt(res.chisqr))
            for key in self.model.param_names:
                params[key].append(res.params[key].value)
                err = res.params[key].stderr
                if err is None:
                    params[key+'_err'].append(np.nan)
                else:
                    params[key+'_err'].append(err)

        params = pd.DataFrame(params)  # More efficient for not using DataFrame.append.
        return params

    @property
    def fbatch(self):
        return self._fbatch

    def get_fbatch(self, n_pts=None):
        """Return fbatch from self.result
        
        Args:
            n_pts: int, number of sample points for the curve.
                if None, keep it same as xdata.

        Return:
            y, if n_pts is None,
            x, y, np.array of values of fitted curve, if n_pts is not None.
        """
        if not n_pts:
            return [res.best_fit for res in self.result]
        else:
            new_xbatch = []
            fbatch = []
            for i_fit, xdata in enumerate(self.xbatch):
                ip = np.linspace(0, 1, num=len(xdata))
                i = np.linspace(0, 1, num=n_pts)
                new_sample_pt = np.interp(i, ip, xdata)
                fdata = self.result[i_fit].eval(x=new_sample_pt)
                fbatch.append(fdata)
                new_xbatch.append(new_sample_pt)
            return new_xbatch, fbatch

    def curvefit(self, index):
        """Return curvefit at given fit index."""
        try:
            result = self.result[index]
        except IndexError:  # FIXME: the reported error should not be IndexError.
            result = None
            print(f'WARNING: fit #{index} failed at batch fit. The result of '
                'curvefit may be different.')
        if result:
            cfit = CurveFit.from_result(result, xdata=self.xbatch[index])
        else:
            cfit = CurveFit(self.xbatch[index], self.ybatch[index], self.model)
        return cfit

    def plot_param(self, show_param: str):
        """Plot the fit parameter with its stderr along fit_index.
        
        Args:
            show_param: str, name of parameter to be shown.
                name with '_err' not accepted.

        Returns:
            fig, ax_val, ax_err of matplotlib.
        """

        if show_param == 'chi':
            fig = plt.figure(figsize=(5,3))
            fig.suptitle(self.model.name)
            ax = fig.subplots()
            ax.plot(self.params['chi'].to_numpy(), '.')
            ax.grid(True, linestyle='--')
            ax.set(
                xlabel='fit index',
                ylabel=show_param,
            )
            return fig, ax, None
        else:
            fig = plt.figure(figsize=(10,3))
            fig.suptitle(self.model.name)
            ax_val = fig.add_subplot(121)
            ax_val.plot(self.params[show_param].values, '.')
            ax_val.grid(True, linestyle='--')
            ax_val.set(
                xlabel='fit index',
                ylabel=show_param,
            )

            ax_err = fig.add_subplot(122)
            ax_err.plot(self.params[show_param+'_err'].values, '.')
            ax_err.grid(True, linestyle='--')
            ax_err.set(
                xlabel='fit index',
                ylabel=show_param+'_err',
            )
            return fig, ax_val, ax_err

    def plot_fit(self, index=None, ax=None):
        """Plot the fit result at specified fit index.
        
        Args:
            index: list(int), index of fit to show.
                if None, all fits will be shown.

        Returns:
            ax of matplotlib.
        """

        if isinstance(index, int):
            i = index
            cfit = CurveFit(self.xbatch[i], self.ybatch[i], model=self.model, 
                        hold=True)
            cfit.result = self.result[i]
            return cfit.plot(ax)

        if index is None:
            index = np.arange(self.num_of_fits)
        if ax is None:
            fig, ax = plt.subplots(figsize=(4,3))
            
        color_idx = -1
        for i in index:
            color_idx += 1
            ax.plot(self.xbatch[i], self.ybatch[i], '.', color=f'C{color_idx}')
            ax.plot(self.xbatch[i], self.fbatch[i], '-', color=f'C{color_idx}')

        ax.set(
            title='fitted data at '+str(index),
            xlabel='x',
        )
        if np.iscomplexobj(self.ybatch):
            ax.set_ylabel('|y|')
        else:
            ax.set_ylabel('y')

        return ax

    def fit(self, **kwargs):
        """Perform fits with self.xbatch and self.ybatch.
        
        Args:
            kwargs: fit initial values of parameters passed to model.
        """
        self.result = []
        for i in trange(self.num_of_fits, desc='Fitting'):
            try:
                cfit = CurveFit(self.xbatch[i], self.ybatch[i], self.model)
                self.result.append(cfit.result)
            except Exception as error:
                raise Exception(f'Something went wrong at fit#{i}') from error
        self._params = self.get_params()
        self._fbatch = self.get_fbatch()
        self.fix_none()

    def fix_none(self):
        """Fix None in self.params with self.fit_with_params_around()."""
        print('Trying to remove NaN in params with fit_with_params_around.')
        def judge_nan(bf):
            mask = np.any(np.isnan(bf.params.to_numpy()), axis=1)
            idx = np.arange(len(mask))[mask]
            return idx
        self.fit_with_params_around(judge=judge_nan)

    def fit_with_params_around(self, judge, max_trial=None, cancel_if_fail=True):
        """Re-fit the data batch with fitted parameters around.
        
        Example:
            def judge(bf):
                mask = np.logical_or(
                    (bf.params['amp_err'].values > 0.2e-3),
                    np.any(np.isnan(bf.params.to_numpy()), axis=1)
                )
                idx = np.arange(len(mask))[mask]
                if len(idx) < 1:
                    return []
                else:
                    return idx
            bfit.fit_with_params_around(judge)
            bfit.plot_param('amp')

        Arg:
            judge: function that takes the bfit as argument, 
                and returns list of indices of fit that need refit.
            max_trial: int, max number of trial.
                Default is half of number of fits.
            cancel_if_fail: boolean,
                Whether to cancel all the changes to bfit if fit failed.
        """

        if max_trial is None:
            max_trial = int(0.5 * self.num_of_fits)

        if len(judge(self)) >= 0.5*self.num_of_fits:
            print('More than half of data are going to be re-fitted!')

        result_backup = copy.copy(self.result)
        try:
            counter = 0
            while (len(judge(self)) != 0) and (counter <= max_trial):
                counter += 1
                for idx in judge(self):
                    shift = ((counter // 2) + 1) * (-1)**counter
                    params_around = self.result[(idx+shift) % self.num_of_fits].params
                    self.result[idx] = self.model.fit(self.ybatch[idx], params_around, x=self.xbatch[idx])
                self._params = self.get_params()
                self._fbatch = self.get_fbatch()
        except:
            if cancel_if_fail:
                last_judge = judge(self)
                self.result = result_backup
                self._params = self.get_params()
                self._fbatch = self.get_fbatch()
                print('Re-fit failed! All changes has been cancelled. '
                    f'The furthest shift is {shift}. '
                    f'These remianing fits are judged broken:\n{last_judge}')
            else:
                print(f'Max_trial reached with furthest shift: {shift}. '
                    f'These remianing fits are judged broken:\n{judge(self)}')
            raise

        if (len(judge(self)) != 0):
            if cancel_if_fail:
                last_judge = judge(self)
                self.result = result_backup
                self._params = self.get_params()
                self._fbatch = self.get_fbatch()
                print('Re-fit failed! All changes has been cancelled. '
                    f'The furthest shift is {shift}. '
                    f'These remianing fits are judged broken:\n{last_judge}')
            else:
                print(f'Max_trial reached with furthest shift: {shift}. '
                f'These remianing fits are judged broken:\n{judge(self)}')
        else:
            print(f'All fits pass the judge by {counter} times of trial.')

    def replace_outliers(self, mask_out=None, watch_param=None):
        """Replace the outliers with inpolated parameter value.
        
        Args:
            mask_out: np.array of boolean values.
                Mask for selecting outlying fits.
                Default is fits whose 'chi' or other watch_param has zsroce greater than 3.
            watch_param: str, name of fit parameter.
                Fits with zsroce of watched parameter greater than 3 will be interpolated.
                Disabled if mask_out is not None.
        """

        if watch_param is None:
            watch_param = 'chi'
        if mask_out is None:
            df_data = self.params.loc[:, lambda df: [(watch_param in col) for col in df.columns]]
            df_zsroce = pd.DataFrame(columns=df_data.columns)
            for col in list(df_data.columns):
                df_zsroce[col] = abs(df_data[col]-df_data[col].mean())/df_data[col].std(ddof=0)
            mask_out = (df_zsroce.to_numpy() > 3).any(axis=1)
        else:
            mask_out = np.array(mask_out)

        if mask_out.min() == True:
            print('Replacement cancelled due to all elements in mask_out is True.')
            return None

        # remove the failure points at head and tail, to avoid interpolating error.
        head_idx = 0
        while mask_out[head_idx] == True:
            head_idx += 1
        mask_out[:head_idx] = False
        print(f'the first {head_idx} failures are ignored for avoiding interpolating error.')

        tail_idx = 1
        while mask_out[-tail_idx] == True:
            tail_idx += 1
        if tail_idx > 1:  # Avoiding mask_out[-1+1:]=False.
            mask_out[-tail_idx+1:] = False
        print(f'the last {tail_idx-1} failures are ignored for avoiding interpolating error.')

        # Interpolate vals and errs of fit parameters for outliers.
        for key in self.model.param_names:
            x = self.params.reset_index().index.values[~mask_out]  # pylint: disable=invalid-unary-operand-type
            y = self.params.loc[:,key].values[~mask_out]  # pylint: disable=invalid-unary-operand-type
            f = interp1d(x, y, kind='linear')
            x_interp = self.params.reset_index().index.values[mask_out]
            y_interp = f(x_interp)
            self._params.loc[mask_out, key] = y_interp
            self._params.loc[mask_out, key+'_err'] = np.nan

        # Reset fitter_data and chi with new parameter values.
        for idx in np.arange(self.num_of_fits)[mask_out]:
            # params = copy.deepcopy(self.result[idx].params)
            # for name in params:  # iterating instant of lmfit.Parameters() gives parameter names.
            #     params[name].set(value=self.params.loc[idx, name])
            ftrace = self.model.eval(
                x=self.xbatch[idx], 
                **self.params.iloc[idx,:].to_dict()
            )
            self._fbatch[idx] = ftrace
            self._params.iloc[idx,:]['chi'] = np.sqrt(np.sum((ftrace - self.ybatch[idx])**2))
        print(f'Fit below has been replaced: \n{np.arange(len(mask_out))[mask_out]}')


class BatchFit_withDots(BatchFit):
    """Subclass of BatchFit, work directly on Dots.
    
    Attributes:
        dots: pandas.DataFrame. Data to fit.
        x_name: str. Column name of xdatas in dots.
        y_name: str. Column name of ydatas in dots.
        stepper_name: List(str). 
            Column names of stepper values along with traces in dots.
        stepper_value: pandas.Index.

    besides, also inherents attributes from BatchFit.
    BatchFit:
    """
    __doc__ += BatchFit.__doc__
    # TODO: Rewrite replace_outliers for better trace_index compatibility.

    def __init__(self, dots, x_name, y_name, stepper_name, model, hold=False):
        """Create a instant of BatchFitter directly by data in dots.
        
        Args:
            x_name: str. Column name of xdatas in dots.
            y_name: str. Column name of ydatas in dots.
            stepper_name: List(str). 
                Column names of stepper values along with traces in dots.
                Note other columns will be ignored.
            model: lmfit.Model.
            verbose: Boolean,
                Whether to print message of loading success in terminal.
            hold: boolean,
                if False, try to do fit right after initialization.
        """
        xbatch, ybatch, stepper_value = df_to_traces(dots, stepper_name, x_name, y_name)
        self.stepper_value = stepper_value
        self.stepper_name = stepper_name
        self.x_name = x_name
        self.y_name = y_name
        # if verbose:
        #     print(f'{len(ybatch)} traces are loaded.')
        super().__init__(xbatch, ybatch, model, hold)

    def get_params(self):
        params = super().get_params()
        params = params.set_index(self.stepper_value)
        return params


def bfit_check(batch_fit, name, min=-np.inf, max=np.inf, tolerance=0):
    """Returns index of fits with parameter values violating giving conditions.
    
    For bfit.fit_with_params_around.
    Usage:
        bfit.fit_with_params_around(
            lambda bf: fitter.bfit_check(bf, 'amp_err', max=0.1),
        )

    Args:
        batch_fit: BatchFit, with non-empty params.
        name: str, name of column to check in bfit.params.
        min: float, the min permittable value.
        max: float, the max permittable value.
        tolerence: int, 
            function returns [] if number of invalid values is less than tolerance.

    Returns:
        np.array of fit indices with parameter values violating giving conditions.
    """
    mask = np.logical_or(
        (batch_fit.params[name].values > max),
        (batch_fit.params[name].values < min),
    )
    mask = np.logical_or(
        mask,
        np.any(np.isnan(batch_fit.params.to_numpy()), axis=1),
    )
    idx = np.arange(len(mask))[mask]
    if len(idx) <= tolerance:
        return np.array([])
    else:
        return idx

def df_to_traces(df, index, columns, values):
    """Split pandas.DataFrame into lists.

    Args:
        df: pandas.DataFrme to convert.
        index, columns, values: str, name of columns. Refers to trace steppers, x_name, y_name.
    
    Returns:
        Two 2d lists of xdata and ydata of the traces, as well as list of stepper values
        by which the traces are distinguished.
        i.e. [trace x values], [trace y values], [stepper values].

    Notes:
        Function signature mimics pandas.DataFrame.pivot. It is actually an extension to
        pivot, in case where traces has different x values or lengths.
    """
    # New method with native functions by pandas.
    gp = df.groupby(index)
    x_series = gp[columns].apply(lambda se: se.values)  # se to np array.
    y_series = gp[values].apply(lambda se: se.values)
    xbatch = x_series.to_list()
    ybatch = y_series.to_list()
    stepper_value = x_series.index

    return xbatch, ybatch, stepper_value


def resample(y: np.ndarray, n_pts: int) -> np.ndarray:
    """Return yp by resampling y for n_pts points.

    >>> resample([0, 3, 33], 7)
    array([ 0.,  1.,  2.,  3., 13., 23., 33.])
    """
    y = np.ravel(y)
    x = np.linspace(0, 1, num=len(y))
    xp = np.linspace(0, 1, num=n_pts)
    return np.interp(xp, x, y)


def getitem_from_fit_result(res: lmfit.model.ModelResult, k: str) -> float:
    """Get parameter value or stderr from a fit result.

    For quick implementation of __getitem__ of fitters.
    """
    if res is None:
        raise ValueError("No valid result yet.")

    if k == "chi":
        return np.sqrt(res.chisqr)
    elif k in res.model.param_names:
        return res.params[k].value
    elif k.removesuffix("_err") in res.model.param_names:
        k = k.removesuffix("_err")
        v = res.params[k].stderr
        if v is None:
            return np.nan
        else:
            return v
    else:
        raise KeyError("Invalid key: %s", k)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
