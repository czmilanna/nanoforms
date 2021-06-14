from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from nanoforms_app.cromwell import workflow_outputs


def krona_report(request, workflow_id):
    outputs = workflow_outputs(workflow_id).get('outputs', {})
    out = outputs.get('prz_hybrid_assembly.krona_report')
    paths = [out] if isinstance(out, str) else out
    path = next(x for x in paths if x.endswith('C600_kraken2_krona.html'))
    quast_soup = BeautifulSoup(open(path, 'r').read(), "html.parser")
    quast_soup_string = str(quast_soup)

    return HttpResponse(mark_safe(quast_soup_string))


def krona_report_txt(request, workflow_id):
    outputs = workflow_outputs(workflow_id).get('outputs', {})
    out = outputs.get('prz_hybrid_assembly.kraken2_report')
    paths = [out] if isinstance(out, str) else out
    path = next(x for x in paths if x.endswith('C600_kraken2_report'))
    lines = open(path, 'r').readlines()
    html_string = '<table>'
    html_string += '<tr><th>Percentage of reads covered by the clade rooted at this taxon</th>' \
                   '<th>Number of reads covered by the clade rooted at this taxon</th>' \
                   '<th>Number of reads assigned directly to this taxon</th>' \
                   '<th>A taxonomy rank code</th>' \
                   '<th>NCBI taxonomy ID</th>' \
                   '<th>Indented scientific name</th></tr>'
    for l in lines:
        l = l.strip()
        s = l.split('\t')
        if float(s[0]) > 0.009:
            html_string += '<tr>'
            for ls in s:
                html_string += f'<td>{ls.replace(" ", "&nbsp;")} &nbsp;&nbsp;</td>'
            html_string += '</tr>'
    html_string += '</table>'
    return HttpResponse(mark_safe(html_string))
