from .chart import Chart
from .lib.utils import to_float, to_date, guess_date_interval

import numpy as np
from math import inf
from dateutil.relativedelta import relativedelta
# from adjustText import adjust_text
from labellines import labelLines


class SerialChart(Chart):
    """Plot a timeseries, as a line or bar plot.

    Data should be a list of iterables of (value, date string) tuples, eg:
    `[ [("2010-01-01", 2), ("2010-02-01", 2.3)] ]`
    """
    _uses_categorical_data = False

    def __init__(self, *args, **kwargs):
        super(SerialChart, self).__init__(*args, **kwargs)
        self.type = "bars"

        # Percent of period. 0.85 means a bar in a chart with yearly data will
        # be around 310 or 311 days wide.
        self.bar_width = 0.9

        self.allow_broken_y_axis = kwargs.get("allow_broken_y_axis", None)
        # draw bars and cut ay axis from this line
        self.baseline = kwargs.get("baseline", 0)
        self.baseline_annotation = kwargs.get("baseline_annotation", None)
        self.accentuate_baseline = True

        self.color_labels = kwargs.get("color_labels", None)

        # Set with of lines explicitly (otherwise determined by style file)
        self.line_width = None

        self.grid = True
        self.point_marker = "."
        self.line_marker = None
        self.line_marker_size = 3

        self.max_ticks = 10

        # Manually set tick locations and labels? Provide a list of tuples:
        # [(2013-01-01, "-13"), (2014-01-01, "-14"), (2015-01-01, "-15")]
        self.ticks = None
        self._ymin = None
        self._ymax = None

        # Optional: specify a list of colors (one color for each dataset)
        self.colors = None

        # Optional: where to place series label
        # Could be set already by subclass
        if not hasattr(self, "label_placement"):
            self.label_placement = "legend"  # legend|inline|outside|line

        # Optional: annotate each point with a value label
        self.value_labels = False

        # Optional: Adds background color to part of charts
        self.highlighted_x_ranges = []
        self.x_range_labels = []

    @property
    def ymin(self):
        # WIP
        return self._ymin

    @ymin.setter
    def ymin(self, val):
        self._ymin = val

    @property
    def ymax(self):
        return self._ymax

    @ymax.setter
    def ymax(self, val):
        self._ymax = val

    def _days_in(self, interval, d=None):
        """
        Return number of days in a given period. This is used to set bar widths, so approximate is fine.

        If only interval is given, use a typical number of days.
        >>>> _days_in(monthly)
        30
        >>>> _days_in(monthly, datetime(2004, 02, 05))
        29
        """
        if d is None:
            return {
                'decennial': 3652,
                'yearly': 365,
                'quarterly': 91,
                'monthly': 30,
                'weekly': 7,
                'daily': 1,
            }[interval]
        else:
            # https://stackoverflow.com/questions/4938429/how-do-we-determine-the-number-of-days-for-a-given-month-in-python

            if interval == "yearly":
                return (
                    (d + relativedelta(years=1)).replace(day=1, month=1) - d.replace(day=1, month=1)
                ).days
            elif interval == "quarterly":
                return (
                    (d + relativedelta(months=3)).replace(day=1) - d.replace(day=1)
                ).days
            elif interval == "monthly":
                return (
                    (d + relativedelta(months=1)).replace(day=1) - d.replace(day=1)
                ).days
            elif interval == "weekly":
                # Assuming ISO 8601 here
                return 7
            elif interval == "daily":
                return 1
            elif interval == "decennial":
                return (
                    (d + relativedelta(years=10)).replace(day=1, month=1) - d.replace(day=1, month=1)
                ).days

    def _get_annotation_direction(self, index, values):
        """ Given an index and series of values, provide the estimated best
        direction for an annotation. This will be an educated guess, and the
        annotation is not guaranteed to be free from overlapping,
        """
        num_vals = len(values)
        if num_vals < 2:
            return "up"
        if index == 0:
            if values[0] < values[1]:
                return "down"
            else:
                return "up"
        if index == num_vals - 1:
            # get previous non-None value
            latest_not_null = [x for x in values[:-1] if x is not None][-1]
            if latest_not_null <= values[-1]:
                return "up"
            else:
                return "down"
        val = values[index]
        if val == max(values[index - 1:index + 2]):
            return "up"
        if val == min(values[index - 1:index + 2]):
            return "down"
        return "up"

    @property
    def values_will_be_stacked(self):
        return (len(self.data) > 1) and all([t == "bars" for t in self.type])

    def _add_data(self):

        series = self.data

        # For backwards compatibility: Convert type = "line" -> type = ["line"]
        if type(self.type) is str:
            self.type = [self.type] * len(series)

        if self.allow_broken_y_axis is None:
            if "bars" in self.type:
                self.allow_broken_y_axis = False
            else:
                self.allow_broken_y_axis = True

        # parse values
        serie_values = []
        for i, serie in enumerate(series):
            # make sure all timepoints are unique
            _timepoints = [x[0] for x in serie]
            if len(_timepoints) > len(set(_timepoints)):
                raise ValueError(f"Duplicated timepoints: {_timepoints}")
            _values = [to_float(x[1]) for x in serie]
            if self.type[i] == "bars":
                # Replace None values with 0's to be able to plot bars
                _values = [0 if v is None else v for v in _values]
            serie_values.append(_values)
        self.serie_values = serie_values

        #  Select a date to highlight
        highlight_date = None
        if self.highlight is not None:
            try:
                highlight_date = to_date(self.highlight)
            except ValueError:
                # in case we are highlighting something else (like a whole serie)
                highlight_date = None

        # Make an educated guess about the interval of the data
        if self.interval is None:
            self.interval = guess_date_interval(self.data)

        # Formatters for axis and annotations
        y_formatter = self._get_value_axis_formatter()
        a_formatter = self._get_annotation_formatter()

        # Store y values while we are looping the data, to adjust axis,
        # and highlight diff
        highlight_diff = {
            'y0': inf,
            'y1': -inf
        }
        highlight_values = []

        # For storing elements for later position adjustment
        line_label_elems = []
        value_label_elems = []

        bar_elems = []

        for i, serie in enumerate(series):

            values = np.array(serie_values[i], dtype=float)
            dates = [to_date(x[0]) for x in serie]
            dates_str = [x[0] for x in serie]

            highlight_value = None
            if self.highlight:
                try:
                    highlight_value = values[dates.index(highlight_date)]
                    highlight_values.append(highlight_value)
                except ValueError:
                    # If this date is not in series, silently ignore
                    pass

            if self.highlight and (highlight_value is not None):
                highlight_diff['y0'] = min(highlight_diff['y0'],
                                           highlight_value)
                highlight_diff['y1'] = max(highlight_diff['y1'],
                                           highlight_value)
            if self.type[i] in ["line", "markers"]:
                # Put first series on top
                zo = len(series) - i + 1
                zo += 10  # Make sure lines are on top of bars

                lw = self.line_width
                mz = self.line_marker_size
                lm = self.line_marker
                if self.type[i] == "markers":
                    if lm is None:
                        lm = "o"
                    if lw is None:
                        lw = self._nwc_style.get("lines.linewidth", 2) / 2
                    mz *= 3
                else:
                    if lm is None:
                        lm = "-"
                    if lw is None:
                        lw = self._nwc_style.get("lines.linewidth", 2)

                if hasattr(self, "_get_line_colors"):
                    # Hook for sub classes
                    color = self._get_line_colors(i)
                elif self.colors is not None:
                    if self.colors == "qualitative_colors":
                        color = self._nwc_style["qualitative_colors"][i]
                    else:
                        color = self.colors[i]
                elif self.highlight in dates_str and self.type[i] == "markers":
                    # For markers, will will use a logic similar to bars
                    color = self._nwc_style["neutral_color"]
                elif i == 0:
                    color = self._nwc_style["strong_color"]
                else:
                    color = self._nwc_style["neutral_color"]
                marker_fill = None
                if hasattr(self, "_get_marker_fill"):
                    marker_fill = self._get_marker_fill(i)

                line, = self.ax.plot(
                    dates,
                    values,
                    lm,
                    markersize=mz,
                    color=color,
                    markerfacecolor=marker_fill,
                    markeredgewidth=0,
                    zorder=zo,
                    lw=lw,
                )
                if self.highlight in dates_str and self.type[i] == "markers":
                    # Highlight specific date (Motplotlib has no better option than to overwrite the marker)
                    self.ax.plot(
                        highlight_date,
                        highlight_value,
                        c=self._nwc_style["strong_color"],
                        marker=lm,
                        markersize=mz,
                        markerfacecolor=marker_fill,
                        markeredgewidth=0,
                        zorder=zo + 1,
                    )

                if self.type[i] == "markers":
                    # Join the dots with a line
                    self.ax.plot(
                        dates,
                        values,
                        color=color,
                        zorder=zo - 1,
                        lw=lw,
                    )
                else:
                    # Add single, orphaned data points as markers
                    # None, 1, None, 1, 1, 1 =>  . ---
                    num_values = len(values)
                    if num_values == 1:
                        self.ax.plot(
                            dates[0],
                            values[0],
                            c=color,
                            marker=self.point_marker,
                            zorder=12,
                        )
                    elif num_values > 1:
                        for j, v in enumerate(values):
                            def nullish(val):
                                return val is None or np.isnan(val)
                            plot_me = False
                            if not nullish(v):
                                if j == 0 and nullish(values[1]):
                                    plot_me = True
                                elif j == num_values - 1 and nullish(values[j - 1]):
                                    plot_me = True
                                elif nullish(values[j - 1]) and nullish(values[j + 1]):
                                    plot_me = True
                            if plot_me:
                                self.ax.plot(
                                    dates[j], v,
                                    c=color,
                                    marker=self.point_marker,
                                    zorder=12
                                )

                if len(self.labels) > i and any([x[1] for x in serie]):
                    line.set_label(self.labels[i])

                if self.label_placement == "line":
                    # TODO: Offset should be dynamic
                    lbl = self._annotate_point(
                        self.labels[i],
                        (dates[-1], values[-1]),
                        "right",
                        offset=15,
                        color=color,
                        va="center",
                        # arrowprops=dict(arrowstyle="->", color=color),
                    )
                    # store labels to check for overlap later
                    line_label_elems.append(lbl)

                # add highlight marker
                if highlight_value:
                    self.ax.plot(
                        highlight_date,
                        highlight_value,
                        c=color,
                        marker='o',
                        markersize=5,
                        zorder=zo,
                    )

            elif self.type[i] == "bars":
                # Put first series on top
                zo = len(series) - i + 1

                # Create colors
                colors = None
                if hasattr(self, "_get_bar_colors"):
                    # Hook for sub classes
                    colors = self._get_bar_colors(i)
                elif self.color_fn:
                    # Custom function has priority
                    # TODO: These functions probably want to know
                    # about stacking and highlighting, but we have
                    # no such usecase yet
                    colors = [
                        self._color_by(v, baseline=self.baseline) for v in values
                    ]
                elif self.colors:
                    colors = [self.colors[i]] * len(values)
                elif i == 0 and self.highlight:
                    base_color_for_series = self._nwc_style["neutral_color"]
                    hl_color_for_series = self._nwc_style["strong_color"]
                elif i == 0:
                    base_color_for_series = self._nwc_style["strong_color"]
                elif self.values_will_be_stacked:
                    hl_color_for_series = self._nwc_style["strong_color"]
                    base_color_for_series = self._nwc_style["qualitative_colors"][i]
                else:
                    """ i > 0 in mixed mode charts. Use secondary hl color """
                    base_color_for_series = self._nwc_style["neutral_color"]
                    hl_color_for_series = self._nwc_style["qualitative_colors"][i]

                if not colors:
                    if self.highlight in dates_str:
                        colors = []
                        for v in dates_str:
                            if v == self.highlight:
                                colors.append(hl_color_for_series)
                            else:
                                colors.append(base_color_for_series)
                    else:
                        colors = [base_color_for_series] * len(values)
                # Set bar width, based on interval
                """
                if self.interval == "monthly":
                    # Keep all months the same width, to make it look cleaner
                    bar_widths_ = [self._days_in(self.interval) for d in dates]
                else:
                    bar_widths_ = [self._days_in(self.interval, d) for d in dates]
                """
                bar_widths_ = [self._days_in(self.interval, d) for d in dates]

                bbox = self.ax.get_window_extent()
                if (sum(bar_widths_) * 2 / len(dates)) > bbox.width:
                    bar_widths = bar_widths_
                else:
                    bar_widths = [round(w * 0.85) for w in bar_widths_]

                bar_kwargs = dict(
                    color=colors,
                    width=bar_widths,
                    zorder=zo,
                )
                # if len(dates) < 100:
                #    # FIXME: This complements the bar_width hack above
                #    # For some charts edges give better results (n_bars ~50?)
                #    # This should be better tested, and implemented in a
                #    # more robust way
                #    bar_kwargs["edgecolor"] = "white"
                #    bar_kwargs["linewidth"] = 0  # 1

                if self.values_will_be_stacked and i > 0:
                    if self.baseline != 0:
                        raise Exception("Setting a baseline is not supported for stacked bars")
                    # To make stacked bars we need to set bottom value
                    # aggregate values for stacked bar chart
                    cum_values = np.cumsum(serie_values, axis=0).tolist()
                    bar_kwargs["bottom"] = cum_values[i - 1]
                    # But only do this if both values have the same sign!
                    # We want to be able to have opposing (+/-) bars
                    for j, x in enumerate(values):
                        last_serie = serie_values[i - 1]
                        if x != 0 and last_serie[j] != 0 and (np.sign(x) != np.sign(last_serie[j])):
                            # assert cum_values[i][j] == 0
                            bar_kwargs["bottom"][j] = 0
                else:
                    bar_kwargs["bottom"] = self.baseline

                bars = self.ax.bar(dates, values, **bar_kwargs)
                bar_elems.append(bars)

                if len(self.labels) > i and any([x[1] for x in serie]):
                    bars.set_label(self.labels[i])

            # Add annotations
            for idx, p in enumerate(serie):
                if p[2]:
                    dir = "up" if p[1] > self.baseline else "down"
                    self._annotate_point(p[2], (dates[idx], p[1]), direction=dir)

            if self.value_labels:
                for date, value in zip(dates, values):
                    dir = "up"
                    value_label = a_formatter(value)
                    xy = (date, value)
                    elem = self._annotate_point(value_label, xy, direction=dir)
                    value_label_elems.append(elem)
            if self.color_labels:
                import matplotlib.patches as mpatches
                patches = []
                for color, label in self.color_labels.items():
                    # A bit of an hack:
                    # Check if this corresponds to one of our predefined
                    # color names:
                    if f"{color}_color" in self._nwc_style:
                        color = self._nwc_style[f"{color}_color"]
                    patch = mpatches.Patch(color=color, label=label)
                    patches.append(patch)
                self.ax.legend(handles=patches)

        # Annotate highlighted points/bars
        if self.highlight_annotation:
            for hv in highlight_values:
                value_label = a_formatter(hv)
                xy = (highlight_date, hv)
                if self.type[i] == "bars":
                    if hv >= self.baseline:
                        dir = "up"
                    else:
                        dir = "down"
                if self.type[i] in ["line", "markers"]:
                    if len(highlight_values) > 1:
                        # When highlighting two values on the same point,
                        # put them in opposite direction
                        if hv == max(highlight_values):
                            dir = "up"
                        elif hv == min(highlight_values):
                            dir = "down"
                        else:
                            dir = "left"  # To the right we have diff annotation
                    else:
                        # Otherwise, use what works best with the line shape
                        if highlight_date in dates:
                            i = dates.index(highlight_date)
                            dir = self._get_annotation_direction(i, values)
                        else:
                            # This highlight is probably out of range for this dataset
                            # Could happen if we have two or more lines,
                            # with different start and end points.
                            continue
                self._annotate_point(value_label, xy, direction=dir, zorder=15)

        # Add some padding around bars, but only left/right to avoid lines in stacked bars
        if len(dates) < 100:
            for bars in bar_elems:
                # for container in self.ax.containers:
                for bar in bars:
                    x, y = bar.get_xy()
                    w, h = bar.get_width(), bar.get_height()
                    self.ax.plot([x + w, x + w], [y, y + h], color='white', lw=1, zorder=10)
                    self.ax.plot([x, x], [y, y + h], color='white', lw=1, zorder=10)

        # Add background highlights
        for (x0, x1) in self.highlighted_x_ranges:
            x0 = to_date(x0)
            x1 = to_date(x1)
            self.ax.axvspan(x0, x1, alpha=.4, color="lightgrey", lw=0)
        for idx, t in enumerate(self.x_range_labels):
            if idx >= len(self.highlighted_x_ranges):
                continue
            (x0, x1) = self.highlighted_x_ranges[idx]
            x0 = to_date(x0)
            x1 = to_date(x1)
            # Put label betwen top value and axis limit
            _y = self.ymax or self.data.max_val + self.baseline
            _y_top = self.ax.get_ylim()[1]
            _y = _y_top - (_y_top - _y) / 2
            self.ax.text(
                x0 + (x1 - x0) / 2,
                _y,
                t,
                ha='center',
                color=self._nwc_style["dark_gray_color"],
            )

        # Accentuate y=0 || y=baseline
        # if (self.data.min_val < self.baseline) or self.baseline_annotation:
        if self.accentuate_baseline:
            self.ax.axhline(
                y=self.baseline,
                linewidth=1,
                color="#444444",
                zorder=11 if "bars" in self.type else 9,
                linestyle="--" if self.baseline else "-",
            )
        if self.baseline_annotation:
            xy = (to_date(self.data.outer_min_x), self.baseline)
            # We only allow baseline to be set for single series bar charts
            first_val = self.data.values[0][0]
            self._annotate_point(
                self.baseline_annotation,
                xy,
                direction="down" if first_val and first_val >= self.baseline else "up",
                color=self._nwc_style["neutral_color"],
                zorder=12,
            )

        if self.data.min_val < self.baseline:
            self.ax.spines['bottom'].set_visible(False)

        # Shade area between lines if there are exactly 2 series
        # and both are lines
        # For more series, the chart will get messy with shading
        if len(series) == 2 and self.type[0] == "line" and self.type[0] == "bars":
            # Fill any gaps in series
            filled_values = self.data.filled_values
            min_x = self.data.inner_min_x
            max_x = self.data.inner_max_x
            self.ax.fill_between([to_date(x) for x in self.data.x_points],
                                 filled_values[0],  # already a float1w
                                 filled_values[1],
                                 where=[(x >= min_x and x <= max_x)
                                        for x in self.data.x_points],
                                 facecolor=self._nwc_style["fill_between_color"],
                                 alpha=self._nwc_style["fill_between_alpha"])

        # Y axis formatting
        padding_bottom = 0
        if self.ymin is not None:
            # Override ymin if the smallest value is smaller than the suggested ymin
            # For example bar charts with negative values wants a forced ymin=0 if
            # all values are positive, but also show negatives
            ymin = min(self.ymin, self.data.min_val)
            padding_bottom = abs(ymin * 0.15)
        elif self.data.min_val > 0 and self.allow_broken_y_axis:
            # Boken y axis?
            if (self.data.max_val - self.data.min_val) < self.data.min_val:
                # Only break y axis if data variation is less than distance from ymin to 0
                ymin = self.data.min_val
                padding_bottom = abs(self.data.min_val * 0.15)
            else:
                ymin = self.baseline
                padding_bottom = abs(self.baseline * 0.15)
        elif self.data.min_val < 0:
            ymin = self.baseline + self.data.min_val
            padding_bottom = abs(-ymin * 0.15)
        else:
            ymin = self.baseline
            padding_bottom = abs(self.baseline * 0.15)

        if self.ymax is not None:
            ymax = self.ymax
            padding_top = 0
        else:
            if self.values_will_be_stacked:
                ymax = self.data.stacked_max_val
            else:
                ymax = self.data.max_val + self.baseline

            padding_top = ymax * 0.15

        if not self.revert_value_axis:
            self.ax.set_ylim(
                ymin=ymin - padding_bottom,
                ymax=ymax + padding_top,
            )

        self.ax.yaxis.set_major_formatter(y_formatter)
        self.ax.yaxis.grid(self.grid)

        if ymin > self.baseline and self.allow_broken_y_axis:
            self._mark_broken_axis()

        """
        if all([x == "markers" for x in self.type]):
            # ....
        else:
        """
        self._set_date_ticks(dates)

        # Add labels in legend if there are multiple series, otherwise
        # title is assumed to self-explanatory
        if len(self.labels) > 1:
            if self.label_placement == "legend":
                _ = self.ax.legend(loc="best", reverse=True)
                _.set(zorder=20)
            elif self.label_placement == "outside":
                # mpl 3.7 has loc=outside, but it will lead to overlaps with titles
                # also, has to be set on the figure, causing image size to change
                _ = self.ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left", reverse=True)
                # self._fig.subplots_adjust(right=0.8)
                # self._fig.tight_layout()
                _.set(zorder=20)
            elif self.label_placement == "inline":
                labelLines(self.ax.get_lines(), align=False, zorder=13, outline_width=4, fontweight="bold")

        # Trend/change line
        if hasattr(self, "trendlines") and self.trendlines:
            trendlines = self.trendlines
        else:
            trendlines = self.trendline
        if trendlines:
            # Backwards compat:
            # We support single trendlines like
            # - [str, str]
            # - [[str, val], [str, val]]
            # OR multiple trendlines:
            # - [[str, str], [str, str]]
            # - [[[str, val], [str, val]], [[str, val], [str, val]]]
            if (type(trendlines[0]) is str) or (type(trendlines[0][1]) in [int, float]):
                trendlines = [trendlines]
            trendline_color = self._nwc_style["strong_color"]
            if (
                len(set(self.type)) == 1
                and self.type[0] == "bars"
                and colors
                and len(set(colors)) == 1
                and colors[0] == self._nwc_style["strong_color"]
            ):
                # All bar charts, there are colors, and
                # all series are the same, strong color.
                # Use neutral color for trendline
                trendline_color = self._nwc_style["neutral_color"]

            if len(self.data) == 1 and self.type[0] == "line":
                # If we have a single line,
                # avoid using the same color for trendline
                trendline_color = self._nwc_style["neutral_color"]
            for trendline in trendlines:
                # Check if we have a list of single (x-) values, or data points
                if all(len(x) == 2 for x in trendline):
                    # data points
                    dates = [to_date(x[0]) for x in trendline]
                    values = [to_float(x[1]) for x in trendline]
                    marker = "_"
                else:
                    # timepoints, get values from first series
                    dates = [to_date(x) for x in trendline]
                    alldates = [to_date(x[0]) for x in self.data[0]]
                    values = [self.data[0][alldates.index(d)][1] for d in dates]
                    marker = 'o'

                self.ax.plot(
                    dates, values,
                    color=trendline_color,
                    zorder=14,
                    linewidth=0.9,
                    marker=marker,
                    linestyle='dashed',
                )

                # Annotate points in trendline
                if self.annotate_trend:
                    for i, date in enumerate(dates):
                        if i and values[i] == values[i - 1]:
                            # If flat, only annotate first point
                            continue
                        xy = (date, values[i])
                        dir = self._get_annotation_direction(i, values)
                        self._annotate_point(
                            a_formatter(values[i]),
                            xy,
                            color=trendline_color,
                            direction=dir,
                            zorder=15
                        )

            # x = [a.xy[0] for a in self._annotations]
            # y = [a.xy[1] for a in self._annotations]
            # adjust_text(self._annotations,
            #             x=x, y=y)

        if len(line_label_elems) > 1:
            self._adust_texts_vertically(line_label_elems)

        if len(value_label_elems) > 1:
            self._adust_texts_vertically(value_label_elems, ha="center")

        # yline
        if self.yline:
            self.ax.axhline(
                y=self.yline,
                color=self._nwc_style["neutral_color"],
                linewidth=0.8,
                xmin=0,
                xmax=1,
                clip_on=False,
                zorder=11,
            )
        if self.yline_label:
            font_size = self._nwc_style.get("annotation.fontsize", 8)
            self.ax.text(
                to_date(self.data.outer_max_x),
                self.yline,
                " " + self.yline_label,
                color=self._nwc_style["neutral_color"],
                fontsize=font_size,
                va="bottom",
                ha="right",
                zorder=12,
            )

    def _adust_texts_vertically(self, elements, ha="left"):
        """
        from adjustText import get_bboxes
        if len(elements) == 2:
            # Hack: check for overlap and adjust labels only
            # if such overlap exist.
            # `adjust_text` tended to offset labels unnecessarily
            # but it might just be that I haven't worked out how to use it properly
            bb1, bb2 = get_bboxes(elements, self._fig.canvas.get_renderer(), (1.0, 1.0), self.ax)
            if (
                # first label is above
                (bb1.y0 < bb2.y0) and (bb1.y1 > bb2.y0)
                # first label is below
                or (bb1.y0 > bb2.y0) and (bb1.y0 < bb2.y1)
            ):
                adjust_text(elements, autoalign="y", ha=ha)

        else:
            adjust_text(
                elements,
                autoalign="y",
                only_move="y",  # will replace autoalign in newer versions
                ax=self.ax,
                max_move=(0, 10), # (10, 10) is default
            )
        """
        overlap = True
        loops = 0
        while overlap:
            for i, bb in enumerate(elements):
                if i == len(elements) - 1:
                    overlap = False
                    break
                bbox1 = elements[i].get_window_extent()
                bbox2 = elements[i + 1].get_window_extent()
                if bbox1.y1 > bbox2.y0 + 10 and bbox1.x1 > bbox2.x0 + 5:  # allow for some overlap
                    loops += 1
                    xy1 = elements[i].xyann
                    # xy2 = elements[i + 1].xyann
                    # elements[i].update_positions((bbox1.x0, bbox1.y0 - 5))
                    # elements[i].update_positions((xy1[0], xy1[1] - 0.02))
                    elements[i].xyann = (xy1[0], xy1[1] - 0.01)
                    # elements[i].set(arrowprops=dict(arrowstyle="->"))
                    # elements[i + 1].xyann = (xy2[0], xy2[1] + 0.005)
                    break
            if loops > 5_000:
                break
