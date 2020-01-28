from jsonpath_rw import jsonpath as jpath
from jsonpath_rw import parse as jparse
from stf import parse
from stf.util.colors import termcolor as tc
import textwrap


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
import stf.util as util

#doc = json_load('/livebox/scratch/stf/results/alltests::SLO_ADC-v1.0-degg-deadbeef.json')

def msToDatetime(ms):
    import datetime
    return str(datetime.datetime.fromtimestamp(ms / 1000.0))

def dd(label, key):
    return f'<dt>{label}</dt><dd>{{{key}}}</dd>'

def getHtmlSummary(jdoc):
    summary_fields = [
        ('Runset Name', 'runSet'),
        ('Date run', 'runDate'),
        ('Station', 'station'),
        ('STF Version', 'stfVersion'),
        ('FPGA Version', 'fpgaVersion'),
        ('Iceboot', 'softwareInfo')
    ]
    h = ''
    testGroup = jdoc.metadata.test_group.replace(':', '')
    meas = jp_commsMeasurements.find(jdoc)[0].value
    fpgaVersion = meas['fpgaVersion']['measured_value']
    swInfo = f'<strong>v{meas["softwareVersion"]["measured_value"]}</strong> - build {meas["softwareId"]["measured_value"]}'
    for label, key in summary_fields:
        h += dd(label, key).format(**dict(
            runSet=testGroup,
            runDate=msToDatetime(jdoc.start_time_millis),
            station=jdoc.station_id,
            stfVersion=jdoc.metadata.stf_version,
            fpgaVersion=fpgaVersion,
            softwareInfo=swInfo
        ))
    return f'<h1>Runset report for {testGroup}</h1><br><dl>{h}</dl>'


def vals(matches):
    return [x.value for x in matches]


def print_phase_outcomes():
    print(print_outcomes(jp_phaseOutcomes, jp_phaseNames, doc))

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

def runset_summary(runset_name, out='console'):
    jp_meas = jparse('$.phases.[2].measurements.*')
    files = runset_getFiles(runset_name)
    report = f'RUNSET SUMMARY RESULTS FOR {tc(runset_name, "gold")}\n'
    # for html output
    outcome_colors = {
        'PASS': 'green',
        'FAIL': 'red',
        'ERROR': 'orange'
    }

    html_summary = ''


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
        if not html_summary and out == 'html':

            html_summary = getHtmlSummary(jdoc)

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
                'framework_version': jdoc.metadata.stf_version
            })


    if out == 'csv':
        report = "OUTCOME,TEST_NAME,TEST_INSTANCE,TEST_VERSION"
        #print(s)
    if out == 'json':
        print(json.dumps(j, indent=2))
        return
    if out == 'html':
        print(html_summary)
        print(f'<table><thead><th>Outcome</th><th>Test Name</th><th>Instance</th><th>Test Version</th></thead><tbody>{s}</tbody></table>')
        return
    print(report + textwrap.dedent(s))

def runset_report(runset_name):
    jp_meas = jparse('$.phases.[2].measurements.*')

    files = runset_getFiles(runset_name)
    report = f'RUNSET RESULTS FOR {tc(runset_name, "gold")}\n'

    #dash = (len(report) * '=')
    #report = f'{dash}\n{report}\n{dash}'
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
    print(report + textwrap.dedent(s))

def runset_getFiles(runset_name, results_dir=None):
    import stf
    if not results_dir:
        results_dir = stf.config.get_path('results', filename=runset_name)

    return util.files.globFiles(results_dir, pattern='*.json')
