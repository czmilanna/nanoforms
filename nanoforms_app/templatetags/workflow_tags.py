from bs4 import BeautifulSoup
from django import template
from django.utils.safestring import mark_safe

from nanoforms_app.cromwell import workflow_outputs, workflow_timing
from nanoforms_app.models import Workflow

register = template.Library()


@register.simple_tag
def workflow_timing_html(workflow: Workflow, string_to_remove=None):
    if workflow.running:
        html = workflow_timing(workflow.id)
        html = html.replace('./metadata', f'/metadata/{workflow.id}')
        if string_to_remove:
            html = html.replace(string_to_remove, '')
        return mark_safe(html)
    return mark_safe('<span></span>')


@register.simple_tag
def workflow_output_link(workflow_id, output_key, file_name):
    return f'/download/{workflow_id}/{output_key}/{file_name}'


@register.simple_tag
def workflow_quast_report(workflow_id, output_key, file_name):
    outputs = workflow_outputs(workflow_id).get('outputs', {})
    out = outputs.get(output_key)
    paths = [out] if isinstance(out, str) else out
    path = next(x for x in paths if x.endswith(file_name))
    soup = BeautifulSoup(open(path, 'r').read(), "html.parser")
    for tag in soup.select('div#header'):
        tag.decompose()
    soup_string = str(soup)
    soup_string = soup_string.replace('border-bottom: 1px solid', 'border-bottom: 0px solid')
    return mark_safe(soup_string)


@register.simple_tag
def workflow_nanoplot_report(workflow_id, output_key, file_name):
    outputs = workflow_outputs(workflow_id).get('outputs', {})
    out = outputs.get(output_key)
    paths = [out] if isinstance(out, str) else out
    path = next(x for x in paths if x.endswith(file_name))
    soup = BeautifulSoup(open(path, 'r').read(), "html.parser")
    for tag in soup.select('div.panel.panelC'):
        tag.decompose()

    soup_string = str(soup)
    soup_string = soup_string.replace('0px 0px 5px 5px #C9C9C9;', '0px 0px 0px 0px #C9C9C9;')
    soup_string = soup_string.replace('2px 2px 5px 5px #C9C9C9;', '0px 0px 0px 0px #C9C9C9;')
    soup_string = soup_string.replace('Summary statistics', '')
    soup_string = soup_string.replace('<h1>NanoPlot report</h1>', '')
    return mark_safe(soup_string)


@register.simple_tag
def workflow_pdf_report(workflow: Workflow, output_parent_key, parent_file_name, output_ass_key, ass_file_name):
    parent_outputs = workflow_outputs(workflow.parent.id).get('outputs', {})
    parent_out = parent_outputs.get(output_parent_key)
    parent_paths = [parent_out] if isinstance(parent_out, str) else parent_out
    parent_path = next(x for x in parent_paths if x.endswith(parent_file_name))
    parent_content = open(parent_path, 'r').read()

    ass_outputs = workflow_outputs(workflow.id).get('outputs', {})
    ass_out = ass_outputs.get(output_ass_key)
    ass_paths = [ass_out] if isinstance(ass_out, str) else ass_out
    ass_path = next(x for x in ass_paths if x.endswith(ass_file_name))
    ass_content = open(ass_path, 'r').read()

    return mark_safe(parent_content + ass_content)


@register.simple_tag
def workflow_output_text(workflow_id, output_key, file_name, start=None, stop=None):
    try:
        outputs = workflow_outputs(workflow_id).get('outputs', {})
        out = outputs.get(output_key)
        paths = [out] if isinstance(out, str) else out
        path = next(x for x in paths if x.endswith(file_name))
        if not path:
            return ''
        with open(path, 'r') as f:
            lines = f.readlines()
            lines = lines[start:stop]
            return mark_safe('<br/>'.join(lines))
    except:
        return mark_safe('<br/>')
