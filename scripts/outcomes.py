try:
    from jsonpath_rw import jsonpath as jpath
    from jsonpath_rw import parse as jparse
except ModuleNotFoundError:
    print('jsonpath_rw required for reports and summaries')
    print('\ntry:\n  pip install jsonpath-rw\n')
    print('more info: https://github.com/kennknowles/python-jsonpath-rw')
    raise SystemExit
from stf import parse, config, util, debug
from stf.util import files as futil
from stf.util.colors import termcolor as tc
from stf.util.colors import disable_colors
from stf.util.misc import INFO
import textwrap
import sys


jp_testOverview = jparse

jp_phaseOutcomes = jparse('$.phases.[*].outcome')
jp_phaseNames = jparse('$.phases.[*].name')

jp_measurements = jparse('$.phases.[*].measurements')
meas_name = '$.[*].name'
meas_outcome = '$.[*].outcome'

jp_commsMeasurements = jparse('$.phases.[1].measurements')

tpl_nameoutcome = '{outcome}       {name}\n'

tpl_name_outcome = '{jp_phaseOutcomes}       {jp_phaseNames}\n'

import json
from stf.parse import json_load
from stf.util.misc import jsonify

#doc = json_load('/livebox/scratch/stf/results/alltests::SLO_ADC-v1.0-degg-deadbeef.json')

bullet = tc('>>> ', 'aqua')

def msToDatetime(ms):
    import datetime
    return str(datetime.datetime.utcfromtimestamp(ms / 1000.0))

def dd(label, key):
    return f'<dt>{label}</dt><dd>{{{key}}}</dd>'

def summaryLine(label, key):
    label = tc(label, 'gray').ljust(25)
    return f'\n{label}:  {{{key}}}'

def getSummary(jdoc, output):
    '''
    get summary info by examining a single testresult doc
    '''
    if output in ['consolebrief', 'csv', 'json']:
        return ''
    summary_fields = [
        ('Runset Name', 'runSet'),
        ('Device Type', 'dtype'),
        ('Device ID', 'dut_id'),
        ('FPGA ChipID', 'fpgaChipID'),
        ('Date run', 'runDate'),
        ('Station', 'station'),
        ('STF Version', 'stfVersion'),
        ('FPGA Version', 'fpgaVersion'),
        ('Iceboot', 'softwareInfo')
    ]
    h = ''
    testGroup = jdoc.metadata.test_group.replace('/', '')
    meas = jp_commsMeasurements.find(jdoc)[0].value
    fpgaVersion = meas['fpgaVersion']['measured_value']
    fpgaChipID = meas['fpgaChipID']['measured_value']

    if output == 'html':
        swInfo = f'<strong>v{meas["softwareVersion"]["measured_value"]}</strong> - build {meas["softwareId"]["measured_value"]}'
        for label, key in summary_fields:
            h += dd(label, key).format(**dict(
                runSet=testGroup,
                runDate=msToDatetime(jdoc.start_time_millis),
                dut_id=jdoc.dut_id,
                fpgaChipID=fpgaChipID,
                dtype=jdoc.metadata.device.type,
                station=jdoc.station_id,
                stfVersion=jdoc.metadata.stf_version,
                fpgaVersion=fpgaVersion,
                softwareInfo=swInfo
            ))
        return f'<h1>Runset report for {testGroup}</h1><br><dl>{h}</dl>'
    elif output == 'console':
        swInfo = f'v{meas["softwareVersion"]["measured_value"]} - build {meas["softwareId"]["measured_value"]}'
        for label, key in summary_fields:
            h += summaryLine(label, key).format(**dict(
                runSet=testGroup,
                runDate=msToDatetime(jdoc.start_time_millis),
                dut_id=jdoc.dut_id,
                fpgaChipID=fpgaChipID,
                dtype=jdoc.metadata.device.type,
                station=jdoc.station_id,
                stfVersion=jdoc.metadata.stf_version,
                fpgaVersion=fpgaVersion,
                softwareInfo=swInfo
            ))
        testGroup = tc(testGroup, 'bold')
        testGroup = tc(testGroup, 'gold')
        return bullet + tc(f'Runset report for {testGroup}', 'gray') + f'\n{h}\n\n'


def vals(matches):
    return [x.value for x in matches]


def print_phase_outcomes(out):
    print(print_outcomes(jp_phaseOutcomes, jp_phaseNames, doc), file=out)

def print_outcomes(jp_oc, jp_name, doc, indent=0):
    out_outcomes = jp_oc.find(doc)
    out_names = jp_name.find(doc)
    data = zip(vals(out_outcomes), vals(out_names))
    return outcomes(data, indent=indent)
    

def colorize_outcome(x):
    outcome_colors = {
        'PASS': 'green',
        'FAIL': 'red',
        'ERROR': 'gold'
    }

    return tc(x, outcome_colors.get(x, 'gray'))

def outcomes(_data, indent=0):
    str_phase_outcomes = ''
    data = []
    tpl_nameoutcome = indent * ' ' + '{outcome}       {name}\n'

    #if isinstance(data[0], dict):
    #    for d in _data:
    #        data.append((d['outcome'], d['name']))
    #else:
    #    data = _data
    data = _data

    for _outcome, name in data:
        outcome = colorize_outcome(_outcome)
        str_phase_outcomes += tpl_nameoutcome.format(**locals())


    #s = f'''OUTCOME    PHASE\n{str_phase_outcomes}\n'''
       
    return str_phase_outcomes

#def outcome_dict(data, tpl):
#    for s in sel:

def measurements():
    p = jparse('$.phases.[2].measurements.*')
    pn = jparse('$.phases.[2].measurements.*.name')
    po = jparse('$.phases.[2].measurements.*.outcome')
    
    print_outcomes(
        jparse(meas_outcome),
        jparse(meas_name),
        doc=vals(p.find(doc))
    )

    #for m in p.find(doc):
    #    s = outcomes(m.value)
    #print(s)
    return vals(p.find(doc)), pn, po
    


def _jformat(doc, tpl, root='ROOT'):
    return tpl.format(**{root: jsonify(doc)})

def jformat(doc, tpl, root='ROOT'):
    s = ''
    if isinstance(doc, list):
        s = '\n'.join([_jformat(d, tpl) for d in doc])
    else:
        s = _jformat(doc, tpl, root=root)

    return s

# helper
def get_instanceName(s):
    try:
        x, y = s.split(':')
        return x, y
    except ValueError:
        return s, 'base'

def runset_summary_all(files, outputs):
    jp_meas = jparse('$.phases.[2].measurements.*')

    # create output buffers
    o_s = {k: '' for k in outputs}
    o_summary = {k: '' for k in outputs}
    o_report = {k: '' for k in outputs}

    #files = runset_getFiles(runset_name)
    report = bullet + tc(f'Summary of Test Results \n\n', 'gray')
    # for html output
    outcome_colors = {
        'PASS': 'green',
        'FAIL': 'red',
        'ERROR': 'orange'
    }

    summary = ''


    #dash = (len(report) * '=')
    #report = f'{dash}\n{report}\n{dash}'
    s = ''
    j = []

    ### summary info
    # list of tests?

    ### details on test pass/fail
    for f in files:
        doc = json_load(f)
        jdoc = jsonify(doc)
        if not o_summary['html']:
            o_summary['html'] = getSummary(jdoc, 'html')
        if not o_summary['console']:
            o_summary['console'] = getSummary(jdoc, 'console')

        name = jdoc.metadata.test_name
        inst = jdoc.metadata.test_instance
        o_s['console'] += f'''{colorize_outcome(jdoc.outcome)}   {jdoc.metadata.test_name} v{jdoc.metadata.test_version}\n'''
        o_s['consolebrief'] += f'''{colorize_outcome(jdoc.outcome)}   {name}\n'''
        o_s['csv'] += f'"{jdoc.outcome}","{name}","{inst}","{jdoc.metadata.test_version}","{jdoc.metadata.stf_version}"\n'
        c = outcome_colors.get(jdoc.outcome, 'black')
        o_s['html'] += f'<tr><td><span style="color: {c}">{jdoc.outcome}</span></td><td>{name}</td><td>{inst}</td><td>{jdoc.metadata.test_version}</td></tr>\n'

        j.append({
            'outcome': jdoc.outcome,
            'test_name': name,
            'test_instance': inst,
            'test_version': jdoc.metadata.test_version,
            'stf_version': jdoc.metadata.stf_version
        })

    # speci
    o_report['json'] = json.dumps(j, indent=2)

    o_report['csv'] = "OUTCOME,TEST_NAME,TEST_INSTANCE,TEST_VERSION,STF_VERSION\n" + o_s['csv']

    o_report['console'] = textwrap.dedent(o_s['console'])
    o_report['consolebrief'] = textwrap.dedent(o_s['consolebrief'])

    o_report['html'] = '<table><thead><th>Outcome</th><th>Test Name</th><th>Instance</th><th>Test Version</th></thead><tbody>{s}</tbody></table>'.format(s=o_s['html'])

    for o, fname in outputs.items():
        debug(f'outputs: {o} -> {fname}')
        with open(fname, 'w') as f:
            f.write(o_summary[o] + o_report[o])




def runset_summary(runset_name, out='console'):
    jp_meas = jparse('$.phases.[2].measurements.*')
    files = runset_getFiles(runset_name)
    report = bullet + tc(f'Summary of Test Results \n\n', 'gray')
    # for html output
    outcome_colors = {
        'PASS': 'green',
        'FAIL': 'red',
        'ERROR': 'orange'
    }

    summary = ''


    #dash = (len(report) * '=')
    #report = f'{dash}\n{report}\n{dash}'
    s = ''
    j = []

    ### summary info
    # list of tests?

    ### details on test pass/fail
    for f in files:
        doc = json_load(f)
        jdoc = jsonify(doc)
        if not summary: 
            summary = getSummary(jdoc, out)

        name = jdoc.metadata.test_name
        inst = jdoc.metadata.test_instance
        if out == 'console':
            s += f'''{colorize_outcome(jdoc.outcome)}   {jdoc.metadata.test_name} v{jdoc.metadata.test_version}\n'''
        elif out == 'consolebrief':
            s += f'''{colorize_outcome(jdoc.outcome)}   {name}\n'''
        elif out == 'csv':
            s += f'"{jdoc.outcome}","{name}","{inst}","{jdoc.metadata.test_version}","{jdoc.metadata.stf_version}"\n'
        elif out == 'html':
            c = outcome_colors.get(jdoc.outcome, 'black')
            s += f'<tr><td><span style="color: {c}">{jdoc.outcome}</span></td><td>{name}</td><td>{inst}</td><td>{jdoc.metadata.test_version}</td></tr>\n'
        elif out == 'json':
            j.append({
                'outcome': jdoc.outcome,
                'test_name': name,
                'test_instance': inst,
                'test_version': jdoc.metadata.test_version,
                'stf_version': jdoc.metadata.stf_version
            })


    if out == 'csv':
        summary = ''
        report = "OUTCOME,TEST_NAME,TEST_INSTANCE,TEST_VERSION,STF_VERSION\n" + s
        #print(s)
    if out == 'json':
        print(json.dumps(j, indent=2), file=out)
        return
    if out in ['console', 'consolebrief']:
        report = textwrap.dedent(s)
    if out == 'html':
        report = '<table><thead><th>Outcome</th><th>Test Name</th><th>Instance</th><th>Test Version</th></thead><tbody>{s}</tbody></table>'.format(s=s)
    print(summary + report)


def runset_report_dir(runset_path):
    # XXX: unused; couldn't get python to print to file for some reason...
    # plus reports make more sense for a single result set
    '''
    runset_path is a path relative to results dir which we should crawl and
    resursively generate reports

    like:

    alltests
    alltests/2020.02.06_223344
    alltests/2020.02.06_223344/degg-<mbid>

    bonus (TODO):
        support wildcards? or change script to use args like

        --allsets       (all testsets)
        --t 2020.02     (all tests run that day)
        --device degg   (all degg devices)
        --device <mbid> (all devices with mbid)
    '''

    
    path = futil.getFilePath(config.get_path('results', filename=runset_path))
    debug('path: {path}'.format(path=path))
    runset_name = runset_path.split('/')[0]

    files = runset_getFiles(None, path)
    if not files:
        paths = futil.getDirs(path)
        for p in paths:
            runset_report_dir(p)
    else:
        # not sure why this doesn't work?!
        #report = futil.getFilePath(path, filename='report.txt')
        #debug('reppath: {report}'.format(report=report))
        #with open(report, 'w') as f:
        #runset_report(runset_name, files=files, out=f)
        runset_report(runset_name, files=files)

def getFiles_resurse(runset_path):
    debug(runset_path) 

    files = runset_getFiles(None, runset_path)
    if not files:
        paths = futil.getDirs(runset_path)
        for p in paths:
            runset_summary_dir(p)
    return files

def runset_summary_dir(runset_path):
    '''
    runset_path is a path relative to results dir which we should crawl and
    resursively generate reports

    like:

    alltests
    alltests/2020.02.06_223344
    alltests/2020.02.06_223344/degg-<mbid>

    bonus (TODO):
        support wildcards? or change script to use args like

        --allsets       (all testsets)
        --t 2020.02     (all tests run that day)
        --device degg   (all degg devices)
        --device <mbid> (all devices with mbid)
    '''
    path = futil.getFilePath('results', runset_path)
    dirs = futil.getDirs(path)
    if not dirs:
        files = runset_getFiles(results_dir=path)
        if files:
            gen_summary(files)
        else:
            debug(f"SKIpPING {runset_path}")
        return
    for d in dirs:
        if d == 'report':
            continue
        debug(f'XXX trying : {d}')
        files = runset_getFiles(results_dir=d)
        if not files:
            runset_summary_dir(d)
        else: 
            gen_summary(files)

    #if not dirs:
    #    debug(f'XXX trying : {path}')
    #    files = runset_getFiles(results_dir=path)

    if not files:
        files = runset_getFiles(results_dir=path)
        if files:
            gen_summary(files)
        else:
            debug(f"(no files) SKIPPING {runset_path}")

    #debug(f'XXX gen_Summary: {path} -> {files}')
    #gen_summary(files)
 
def gen_summary(files):
    out_path = futil.popPath(files[0])[0]
    futil.mkdir(out_path, 'report')
    rp = lambda f: futil.getFilePath(out_path, 'report', filename=f)
    xx = futil.getFilePath(out_path, 'report', filename='<out>')
    debug(f'repout: {xx}')
    outputs = {
        'json': rp('summary.json'),
        'console': rp('summary.txt'),
        'consolebrief': rp('summary-brief.txt'),
        'html': rp('summary.html'),
        'csv': rp('summary.csv'),
    }
    INFO(f'generating reports... {outputs}')

    disable_colors()
    runset_summary_all(files, outputs)

def runset_report(runset_name, files=[], out=sys.stdout):
    jp_meas = jparse('$.phases.[2].measurements.*')

    if not files:
        # XXX: coverage?
        files = runset_getFiles(runset_name)


    report = f'RUNSET RESULTS FOR {tc(runset_name, "gold")}\n'

    s = ''

    ### summary info
    # list of tests?

    ### details on test pass/fail
    for f in files:
        doc = json_load(f)
        jdoc = jsonify(doc)

        #measurements(doc)

        #jp_phaseOutcomes = jparse('$.phases.[*].outcome')
        #jp_phaseNames = jparse('$.phases.[*].name')
        #s += outcomes(vals(doc))
        meas_subdocs = vals(jp_meas.find(doc))
        measurements = print_outcomes(jparse(meas_outcome), jparse(meas_name), meas_subdocs, indent=10)

        failed_measurements = ''
        for _d in meas_subdocs:
            d = jsonify(_d)
            if d.outcome != 'PASS':
                #failed_measurements += jformat(d, '        {m.name}: {m.measured_value}  validator={m.validators}\n', 'm')
                failed_measurements += 8 * ' ' + f'  {d.name}: {d.measured_value}  validator={d.validators}\n'

            #failed_measurements += jformat(meas_subdocs, '{colorize_outcome(d.outcome)}

        if not failed_measurements:
            failed_measurements = 'No Failed Measurements'
        else:
            failed_measurements = f'Failed Measurements:\n{failed_measurements}'
        m = jdoc.metadata
        dash = (len(m.test_name) + len(m.test_instance) + 13) * '-'
        if m.test_instance == 'base':
            inst = tc(m.test_instance, 'gray')
        else:
            inst = tc(m.test_instance, 'aqua')
        s += f'''
        {dash}
        {colorize_outcome(jdoc.outcome)}   {m.test_name}:{inst} v{m.test_version}
        {dash}
        Measurements:
{measurements}

        {failed_measurements}
        '''
    #with open(outfile, 'w') as f:
    print(report + textwrap.dedent(s), file=out)

def runset_getFiles(runset_name='', results_dir=None):
    if not results_dir:
        results_dir = config.get_path('results', filename=runset_name)

    # XXX: file pattern -- change output fname? include stf.json extension?
    files = util.files.globFiles(results_dir, pattern='*degg*.json')
    #if len(files) == 0:
    #    print(f'No output files found for set "{runset_name}"')
    #    debug('No output files found')
    #    raise SystemExit
    debug(f'files: {results_dir} -> {files}')
    return files
