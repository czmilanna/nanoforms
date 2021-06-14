from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from nanoforms_app.cromwell import workflow_outputs


def nanoplot(request, workflow_id):
    outputs = workflow_outputs(workflow_id).get('outputs', {})
    out = outputs.get('prz_prepare_data.htmls')
    paths = [out] if isinstance(out, str) else out
    path = next(x for x in paths if x.endswith('NanoPlot-report.html'))
    soup = BeautifulSoup(open(path, 'r').read(), "html.parser")
    for tag in soup.select('div.panel.panelC'):
        tag.decompose()

    soup_string = str(soup)
    soup_string = soup_string.replace('0px 0px 5px 5px #C9C9C9;', '0px 0px 0px 0px #C9C9C9;')
    soup_string = soup_string.replace('2px 2px 5px 5px #C9C9C9;', '0px 0px 0px 0px #C9C9C9;')
    soup_string = soup_string.replace('Summary statistics', '')
    soup_string = soup_string.replace('<h1>NanoPlot report</h1>', '')
    return HttpResponse(mark_safe(soup_string))
