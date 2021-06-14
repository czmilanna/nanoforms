from bs4 import BeautifulSoup, Tag
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from nanoforms_app.cromwell import workflow_outputs


def quast(request, workflow_id):
    outputs = workflow_outputs(workflow_id).get('outputs', {})
    out = outputs.get('prz_data_assembly.report_html')
    paths = [out] if isinstance(out, str) else out
    path = next(x for x in paths if x.endswith('report.html'))
    quast_soup = BeautifulSoup(open(path, 'r').read(), "html.parser")

    quast_soup.find_all("script", string="Elsie")

    for tag in quast_soup.select('div.top-panel'):
        tag.extract()
    for tag in quast_soup.select('p#report_date'):
        tag.extract()
    for tag in quast_soup.select('p#icarus'):
        tag.extract()

    quast_soup_string = str(quast_soup)
    quast_soup_string = quast_soup_string.replace('border-bottom: 1px solid', 'border-bottom: 0px solid')
    quast_soup_string = quast_soup_string.replace('margin: 0;', '')
    quast_soup_string = quast_soup_string + "</br><h6>Assembly info</h6>"

    out1 = outputs.get('prz_data_assembly.flye_info')
    paths1 = [out1] if isinstance(out1, str) else out1
    path1 = next(x for x in paths1 if x.endswith('assembly_info.txt'))
    if not path1:
        return ''
    with open(path1, 'r') as f:
        line = f.readline()
        header = '<table style="width:50%"><tr>'
        for word in line.split('\t'):
            header += '<th>' + word + '</th>'
        header += '</tr>'
        lines = f.readlines()
        content = ''
        for line in lines:
            content += '<tr>'
            for word in line.split():
                content += '<td>' + word + '</td>'
            content += '</tr>'
        content += '</table>'
        content = header + content + '</br>'

    scripts_to_fix = """
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/litera/bootstrap.min.css"
          integrity="sha384-enpDwFISL6M3ZGZ50Tjo8m65q06uLVnyvkFO3rsoW0UC15ATBFz3QEhr3hmxpYsn" crossorigin="anonymous">
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"
            integrity="sha384-B4gt1jrGC7Jh4AgTPSdUtOBvfO8shuf57BaghqFfPlYxofvL8/KUEfYiJOMMV+rV"
            crossorigin="anonymous"></script>
        """
    soup_string = quast_soup_string + content + scripts_to_fix

    return HttpResponse(mark_safe(soup_string))


def hybrid_quast(request, workflow_id):
    outputs = workflow_outputs(workflow_id).get('outputs', {})
    out = outputs.get('prz_hybrid_assembly.report_html')
    paths = [out] if isinstance(out, str) else out
    path = next(x for x in paths if x.endswith('report.html'))
    quast_soup = BeautifulSoup(open(path, 'r').read(), "html.parser")
    quast_soup.find_all("script", string="Elsie")

    for tag in quast_soup.select('div.top-panel'):
        tag.extract()
    for tag in quast_soup.select('p#report_date'):
        tag.extract()
    for tag in quast_soup.select('p#icarus'):
        tag.extract()

    quast_soup_string = str(quast_soup)
    quast_soup_string = quast_soup_string.replace('border-bottom: 1px solid', 'border-bottom: 0px solid')
    quast_soup_string = quast_soup_string.replace('margin: 0;', '')

    scripts_to_fix = """
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/litera/bootstrap.min.css"
          integrity="sha384-enpDwFISL6M3ZGZ50Tjo8m65q06uLVnyvkFO3rsoW0UC15ATBFz3QEhr3hmxpYsn" crossorigin="anonymous">
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"
            integrity="sha384-B4gt1jrGC7Jh4AgTPSdUtOBvfO8shuf57BaghqFfPlYxofvL8/KUEfYiJOMMV+rV"
            crossorigin="anonymous"></script>
        """
    soup_string = quast_soup_string + scripts_to_fix

    return HttpResponse(mark_safe(soup_string))
