"""
Plot OBS test results stored in an SDS directory and a StationXML file

Reads parameters from an obstest.yaml file
Plots:
    - time_series of one or more stations/channels
    - stacks of time series from one station/channel
    - spectra from  multiple stations/channels
    - particle_motions between two channels


There are 4 sections in each obstest.yaml file:

- ``input``: input data parameters
    - ``SDS_dir``: The directory containing the data (Seiscomp Data Structure
                   format)
    - ``inv_file``: The file containg the station inventory (StationXML format)
    - ``description``: A text description of these tests
- ``output``: output plot file parameters
    - ``show``: show the plots?  If False, just save them to files
    - ``filebase``: start of each output filename (may include directory)
- ``plots``: the plots to make
    - ``time_series``: a list of waveform plots to make, each item contains:
        - ``description``: plot title
        - ``select``: an optional dict of parameters used to select a subset of
                      the waveforms (see obspy.core.stream.Stream.select())
        - ``start_time``: plot start time
        - ``end_time``: plot end time

    - ``spectra``: list of spectra plots to make, each item contains:
        - ``description``: plot title
        - ``start_time``: data start time
        - ``end_time``: data end time
        - ``select`` (optional): as in ``time_series``
        - ``overlay``(optional): overlay spectra on one plot? (True)
    - ``stack``: a list of stacked waveform plots to make.
               Useful when you performed a test action (tap, lift, jump, etc)
               several times.
               Each item contains:
        - ``description``: plot title
        - ``components``: a list of orientation codes to plot (one plot
                                 for each orientation code)
        - ``times``: list of times to plot at (each one "yyyy-mm-ddTHH:MM:SS")
        - ``offset_before.s``: start plot this many seconds before each `time`
        - ``offset_after.s``: end plot this many seconds after each ``time``
    - ``particle_motion``: a list of particle motion plots to make.
                           Use to evaluate the orientation and polarity of
                           the channels.
                           Each item contains:
        - ``description``**: as in ``time_series``
        - ``component_x``: component to plot on the x axis
        - ``component_y``: component code to plot on the y axis
        - ``times``: as in ``stack```
        - ``particle_offset_before.s``: start particle motion plot this many
                                        seconds before each ``time``
        - ``particle_offset_after.s``: end particle motion plot this many
                                       seconds after each ``time``
        - ``offset_before.s``: start time series plot this many seconds before
                               each ``time``
        - ``offset_after.s``: end time series plot this many seconds after
                              each ``time``

``plot_globals`` [optional]: Default values for each type of plot.
                             Same parameters as for ``plots``
"""
import numpy as np
import yaml
import sys
import re
import argparse
import pkg_resources
import os
import json
import shutil
from pathlib import Path, PurePath
from urllib.parse import unquote

import jsonref
import jsonschema
from matplotlib import pyplot as plt
from obspy.core import UTCDateTime, Stream
from obspy.signal import PPSD
from obspy.clients.filesystem.sds import Client
from obspy.core.inventory import read_inventory
from tiskitpy import SpectralDensity  # PSDs

def main():
    """
    Read the yaml file and plot the specified tests
    """
    args = get_arguments()
    if args.examples == True:
        print('Copying example files to current directory:')
        example_files =  Path(__file__).parent.joinpath("_examples")
        dest = Path('.').resolve()
        for x in Path(example_files).iterdir():
            if x.is_file() and x.suffix == ".yaml":
                print(f"\t{x.name}")
                shutil.copyfile(x, dest / x.name)
        return
    if args.yaml_file is None:
        raise ValueError('must specify -i or --examples')
    root = read_obstest_yaml(args.yaml_file)
    plot_globals = get_plot_globals(root)
    show = root['output']['show']
    filebase = root['output']['filebase']
    inputs = {'client': Client(root['input']['SDS_dir']),
              'inv':  read_inventory(root['input']['inv_file'],
                                     format='STATIONXML')}
    plots = root['plots']
    if 'time_series' in plots:
        for plot_info in plots['time_series']:
            plot_info = _add_defaults(
                plot_info, plot_globals.get('time_series', None))
            plot_time_series(inputs, plot_info, filebase, show, args.verbose)
    if 'spectra' in plots:
        for plot_info in plots['spectra']:
            plot_info = _add_defaults(
                plot_info, plot_globals.get('spectra', None))
            plot_spect(inputs, plot_info, filebase, show)
    if 'stack' in plots:
        for plot_info in plots['stack']:
            plot_info = _add_defaults(
                plot_info, plot_globals.get('stack', None))
            start_time_str, end_time_str = _get_time_limits(plot_info)
            kwargs = plot_info.get('select', {})
            stream = _read_inputs(inputs, start_time_str, end_time_str,
                                  **kwargs)
            if stream is None:
                break
            for o_code in plot_info['components']:
                for trace in _stream_component(stream, o_code):
                    plot_stack(trace, plot_info, filebase, show)
    if 'particle_motion' in plots:
        for plot_info in plots['particle_motion']:
            plot_info = _add_defaults(
                plot_info, plot_globals.get('particle_motion', None))
            start_time_str, end_time_str = _get_time_limits(plot_info)
            kwargs = plot_info.get('select', {})
            stream = _read_inputs(inputs, start_time_str, end_time_str,
                                  **kwargs)
            if stream is None:
                break
            streamx = _stream_component(stream, plot_info['component_x'])
            streamy = _stream_component(stream, plot_info['component_y'])
            for station in [t.stats.station for t in streamx]:
                plot_particle_motion(streamx.select(station=station)[0],
                                     streamy.select(station=station)[0],
                                     plot_info, filebase, show)


def plot_spect(inputs, plot_info, filebase, show):
    """
    Calculate and plot spectra for the input data

    Args:
        inputs (dict): client and inventory
        plot_info (dict): `spect` subelements
    """
    # Select appropriate channels
    title = plot_info["description"]
    print(f'Plotting spectra, {title}')
    kwargs = plot_info.get('select', {})
    stream = _read_inputs(inputs, plot_info.get('start_time'),
                          plot_info.get('end_time'), **kwargs)
    if stream is None or len(stream)==0:
        print(f'{stream=}')
        return
    # Calculate spectra
    kwargs = {'inv': inputs['inv']}
    if 'window_length.s' in plot_info:
        kwargs['window_s'] = plot_info['window_length.s']
    spect = SpectralDensity.from_stream(stream, **kwargs)

    # Plot spectra
    overlay = plot_info.get('overlay', True)
    if filebase:
        outfile = _make_plot_filename(filebase, plot_info.get('select', None),
                                      'spectra', title)
    else:
        outfile = None
    spect.plot(outfile=outfile, overlay=overlay, show=show, title=title)


def plot_time_series(inputs, plot_info, filebase, show, verbose=False):
    """
    Plot a time series

    Args:
        inputs (dict): client and inventory
        plot_info (dict): information about the current plot
        filebase (str): file basename
        show (bool): show plot on screen
        verbose (bool): be verbose
    """
    print('Plotting time series "{}"'.format(plot_info["description"]))
    title = plot_info["description"]
    kwargs = plot_info.get('select', {})
    stream = _read_inputs(inputs, plot_info.get('start_time'),
                          plot_info.get('end_time'), **kwargs)
    if stream is None or len(stream)==0:
        print(f'{stream=}')
        return
    if verbose:
        print(stream)
    outfile = None
    if filebase:
        outfile = filebase

    fig = plt.figure()
    fig.suptitle(title)

    if filebase:
        outfile = _make_plot_filename(filebase, plot_info.get('select', None),
                                      'ts', title)
        stream.plot(size=(800, 600), equal_scale=False, fig=fig, outfile=outfile)
    if show:
        stream.plot(size=(800, 600), equal_scale=False, fig=fig)
        plt.show()
    plt.close(fig)


def plot_stack(trace, plot_info, filebase, show):
    """
    Plot a stack of time series from one trace

    Args:
        trace is an obspy Trace object
        plot_info (dict): information about the current plot
        filebase (str): base filename to write the plot to (None)
        show (bool): show plot on screen
    """
    title = plot_info['description'] + f', {trace.get_id()}'
    print(f'Plotting stack "{title}"')
    times = [UTCDateTime(t) for t in plot_info['times']]
    offset_before = plot_info.get('offset_before.s', None)
    offset_after = plot_info.get('offset_after.s', None)
    plot_span = plot_info.get('plot_span', None)
    # print(f'{offset_before=}, {offset_after=}, {plot_span=}')
    assert offset_before >= 0,\
        f'plot_stack "{title}": offset_before < 0 ({offset_before:g})'
    assert offset_after > 0,\
        f'plot_stack "{title}": offset_after <= 0 ({offset_after:g})'
    if plot_span:
        _plot_span(times, Stream(traces=[trace]))
    colors = plt.cm.rainbow(np.linspace(0, 1, len(times)))
    offset_vertical = 0
    # time_zero = UTCDateTime(times[0])
    fig, ax = plt.subplots()
    max_val = 0
    # Set up y axis range
    for time in times:
        temp = trace.slice(time - offset_before, time + offset_after)
        if abs(temp.max()) > max_val:
            max_val = abs(temp.max())
    # Plot the subtraces
    for time, c in zip(times, colors):
        offset_vertical += max_val
        t = trace.slice(time - offset_before, time + offset_after)
        t.detrend('linear')
        ax.plot(t.times("utcdatetime") - time,
                t.data, color=c,
                label=time.strftime('%H:%M:%S') +
                '.{:02d}'.format(int(time.microsecond / 1e4)))
        offset_vertical += max_val
    ax.set_title(title)
    ax.grid()
    ax.legend()
    if filebase:
        outfile = _make_plot_filename(filebase, plot_info.get('select', None),
                                      'stack', title)
        plt.savefig(outfile)
    if show:
        plt.show()
    plt.close(fig)


def plot_particle_motion(tracex, tracey, plot_info, filebase, show):
    """
    Plot particle motions

    Args:
        tracex (:class:`obspy.core.stream.Stream): to plot on x axis
        tracey (:class:`obspy.core.stream.Stream): to plot on y axis
        plot_info (dict): information about the current plot
        filebase (str): base filename to write the plot to (None)
        show (bool): show plot on screen
    """
    description = plot_info['description']
    title = '{}, {} vs {}'.format(description, tracex.get_id(),
                                  tracey.get_id())
    print(f'Plotting particle motion "{title}"')
    times = [UTCDateTime(t) for t in plot_info['times']]
    offset_before = plot_info.get('particle_offset_before.s', None)
    offset_after = plot_info.get('particle_offset_after.s', None)
    offset_before_ts = plot_info.get('offset_before.s', None)
    offset_after_ts = plot_info.get('offset_after.s', None)
    plot_span = plot_info.get('plot_span', None)
    if plot_span:
        _plot_span(times, Stream(traces=[tracex, tracey]))
    # Setup axis grid
    fig = plt.figure()
    gs = fig.add_gridspec(2, 3, hspace=0, wspace=0)
    # two columns, one row:
    axx = fig.add_subplot(gs[0, :2])
    axy = fig.add_subplot(gs[1, :2], sharex=axx, sharey=axx)
    # one column, one row
    axxy = fig.add_subplot(gs[1, 2], sharey=axy)
    tx_comp = tracex.stats.channel[-1]
    ty_comp = tracey.stats.channel[-1]
    for time in times:
        # time series plots
        _plot_one_ts(axx, tracex, tx_comp, time,
                     offset_before, offset_after,
                     offset_before_ts, offset_after_ts)
        _plot_one_ts(axy, tracey, ty_comp, time,
                     offset_before, offset_after,
                     offset_before_ts, offset_after_ts)

        # partical motion plot
        tx = tracex.slice(time - offset_before, time + offset_after)
        ty = tracey.slice(time - offset_before, time + offset_after)
        tx.detrend('linear')
        ty.detrend('linear')
        axxy.plot(tx.data, ty.data)
        axxy.axvline(0)
        axxy.axhline(0)
        axxy.set_aspect('equal', 'datalim')
        axxy.set_xlabel(tx_comp)
        # axxy.set_yticklabels([])
    fig.suptitle(title)
    if filebase:
        outfile = _make_plot_filename(filebase, plot_info.get('select', None),
                                      'pm', title)
        plt.savefig(outfile)
    if show:
        plt.show()
    plt.close(fig)


def _stream_component(stream, component):
    """ Return the traces corresponding to the given component """
    try:
        return stream.select(component=component)
    except IndexError:
        print(f'Did not find component {component}')
        sys.exit()


def _get_time_limits(plot_info):
    """
    Get time limits for an object containing offsets and a list of `times`

    Args:
        plot_info (dict): dictionary containing ``times``, `offset_before.s`
                          and `offset_after.s` elements
    """
    max_offset_before = plot_info['offset_before.s']
    if 'offset_before_ts.s' in plot_info:
        max_offset_before = max(max_offset_before,
                                plot_info['offset_before_ts.s'])
    max_offset_after = plot_info['offset_after.s']
    if 'offset_after_ts.s' in plot_info:
        max_offset_after = max(max_offset_after,
                               plot_info['offset_after_ts.s'])

    min_time = UTCDateTime(plot_info['times'][0]) - max_offset_before
    max_time = UTCDateTime(plot_info['times'][0]) + max_offset_after
    if len(plot_info['times']) > 1:
        for time_str in plot_info['times'][1:]:
            time_obj = UTCDateTime(time_str)
            if time_obj - max_offset_before < min_time:
                min_time = time_obj - max_offset_before
            if time_obj + max_offset_after > max_time:
                max_time = time_obj + max_offset_after
    return min_time.isoformat(), max_time.isoformat()


def _read_inputs(inputs, start_time_str, end_time_str, verbose=False,
                 network='*', station='*', location='*', channel='*'):
    """
    Read selected time range from input files

    Args:
        inputs (dict): client and inventory
        start_time_str (str): string representation of start time
        end_time_str (str): string representation of end time
        network (str): Network code. Wildcards ‘*’ and ‘?’ are supported.
        station (str): Station code. Wildcards ‘*’ and ‘?’ are supported.
        location (str): Location code. Wildcards ‘*’ and ‘?’ are supported.
        channel (str): Channel code. Wildcards ‘*’ and ‘?’ are supported.
    """
    try:
        starttime = UTCDateTime(start_time_str)
        endtime = UTCDateTime(end_time_str)
        assert endtime > starttime, f"{starttime=} is after {endtime=}"
    except Exception:
        print('start_ or end_time badly formatted')
        return None
    if verbose:
        print("Reading from SDS directory")
    stream = inputs['client'].get_waveforms(
        network, station, location, channel, starttime, endtime, merge=0)
    if stream is None or len(stream)==0:
        print(f'{stream=}')
        return None
    return stream


def _make_plot_filename(filebase, selectargs, plot_type, type_info,
                        suffix='.png'):
    """
    Makes a valid filename from the list of elements

    Args:
        filebase (str): start of filename (may include directories)
        selectargs (dict): arguments provided to "select()""
        plot_type (str)): 'spectra', 'ts', 'stack', 'pm'
        type_info (str)): information specific to the plot type
    """
    filepath = Path(filebase)
    filebase = filepath.name
    fileparent = filepath.parent
    fileparent.mkdir(exist_ok=True)
    if selectargs is not None:
        select_strs = '_'.join([key+arg for key, arg in selectargs.items()])
    else:
        select_strs = ''
    cleaned = [_get_valid_filename(e) for e in (filebase, plot_type,
                                                select_strs, type_info)]
    assert suffix[0] == '.'
    return str(fileparent / ('_'.join(cleaned) + suffix))


def _plot_one_ts(ax, trace, comp, time, offset_before_pm, offset_after_pm,
                 offset_before, offset_after):
    t = trace.slice(time - offset_before, time + offset_after)
    t.detrend('linear')
    ax.plot(t.times("utcdatetime") - time, t.data)
    ax.axvline(-offset_before_pm, color='k', linestyle='--')
    ax.axvline(offset_after_pm, color='k', linestyle='--')
    ax.set_ylabel(comp)


def plot_PPSD(trace, inv, start_time, interval=7200, filebase=None,
              show=True):
    """
    Plot a Probabilistic Power Spectral Desnsity for the trace

    trace = obspy Trace objet
    inv = obspy Inventory object
    start_time = time at which to start spectra
    interval=offset between PSDs (seconds, minimum=3600)
    """
    now_time = trace.start_time
    first_read = True
    while now_time < trace.end_time-interval:
        if first_read:
            if trace.stats.component[1] == 'D':
                ppsd = PPSD(trace.stats, metadata=inv,
                            special_handling='hydrophone')
            else:
                ppsd = PPSD(trace.stats, metadata=inv)
            first_read = False
        ppsd.add(trace)
        now_time += interval

    ppsd.save_npz(f'{filebase}_PPSD.npz')
    if filebase:
        description = '{}.{}.{}.{}'.format(trace.stats.network,
                                           trace.stats.station,
                                           trace.stats.location,
                                           trace.stats.channel)
        ppsd.plot(filebase + '_' + description
                  + '_PPSD.png')
    if show:
        plt.plot()
    # ppsd.plot_temporal([0.1,1,10])
    # ppsd.plot_spectrogram()
    return 0


def _UTCDateTimeorNone(input):
    """
    Converts input string to UTCDateTime or None if it doesn't work
    """
    try:
        return UTCDateTime(input)
    except TypeError:
        return None


def _add_defaults(localdict, defaultdict):
    """
    Returns localdict, completed by defaultdict

    If a key is in defaultdict and not in localdict, add to localdict
    """
    if defaultdict is None:
        return localdict
    for k, v in defaultdict.items():
        if k not in localdict:
            localdict[k] = v
    return localdict


def get_plot_globals(root):
    """
    Return global plot values
    """
    globals = root.get('plot_globals', None)
    return globals


def get_arguments():
    """
    Get command line arguments
    """
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    group = p.add_mutually_exclusive_group()
    group.add_argument('-i', dest='yaml_file', help='YAML parameter file')
    group.add_argument('--examples', default=False, action='store_true',
                   help='put examples files in current directory')
    p.add_argument("-v", "--verbose", default=False, action='store_true',
                   help="verbose")
    return p.parse_args()


def _get_valid_filename(s):
    assert isinstance(s, str)
    s = s.strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def _plot_span(times, stream):
    first = min(times)
    last = max(times)
    span = last-first
    stream.slice(first - span / 2, last + span / 2).plot()


def read_obstest_yaml(filename):
    """
    Verify and read in an obsttest yaml file
    """
    with open(filename) as f:
        root = yaml.safe_load(f)
        if not validate_schema(root, 'obstest'):
            sys.exit()
    return root


def validate_schema(instance: dict, type: str = 'obstest', verbose=False):
    """
    Validates a data structure against a draft7 jsonschema

    Args:
        instance: data structure read from a yaml or json filebase
        type: type of the data structure
    """
    base_path = Path(__file__).parent / 'data'
    schema_file = PurePath(base_path) / 'obstest.schema.json'
    base_uri = unquote(PurePath(schema_file).as_uri())


    # schema_file = pkg_resources.resource_filename(
    #     "lcheapo", f"data/{type}.schema.json")
    # base_path = os.path.dirname(schema_file)
    # base_uri = f"file:{base_path}/"
    with open(schema_file, "r") as f:
        try:
            schema = jsonref.loads(f.read(), base_uri=base_uri, jsonschema=True)
        except json.decoder.JSONDecodeError as e:
            print(f"JSONDecodeError: Error loading schema file: {schema_file}")
            print(str(e))
            return False

    # _check_schema(schema)

    # Lazily report all errors in the instance
    v = jsonschema.Draft7Validator(schema)

    if not v.is_valid(instance):
        errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
        for error in errors:
            err_path = ''.join([f"['{e}']" for e in error.path])
            msg = f"{err_path}: {error.message} \tFAILED"
            print(msg)  # errors get printed to console
        return False
    else:
        if verbose:
            print("OK")
        return True



def _check_schema(schema):
    """
    Returns:
        result (bool): True if schema checks out, false if not
    """
    try:
        jsonschema.Draft7Validator.check_schema(schema)
    except jsonschema.ValidationError as e:
        print("SCHEMA ERROR: " + e.message)
        return False
    return True


if __name__ == '__main__':
    sys.exit(main())
