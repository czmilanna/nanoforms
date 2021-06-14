import glob
import gzip
import os
import tarfile
import zipfile


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


def unpack_tars(directory, is_gz=False):
    g = os.path.join(directory, f'*.tar{".gz" if is_gz else ""}')
    for file in glob.glob(g):
        print(file)
        with tarfile.open(file, f'r:{"gz" if is_gz else ""}') as tar:
            for tarinfo in tar:
                if not tarinfo.isdir():
                    tarinfo.name = os.path.basename(tarinfo.name)
                    tar.extract(tarinfo, directory)


def unpack_zips(directory):
    for file in glob.glob(os.path.join(directory, '*.zip')):
        print(file)
        with zipfile.ZipFile(file, 'r') as z:
            for zipinfo in z.infolist():
                if not zipinfo.is_dir():
                    zipinfo.filename = os.path.basename(zipinfo.filename)
                    z.extract(zipinfo, directory)


def gzip_fastq(directory):
    g = os.path.join(directory, '*.fastq')
    for file in glob.glob(g):
        print(file)
        with open(file, 'rb') as f_in, gzip.open(f'{file}.gz', 'wb') as f_out:
            f_out.writelines(f_in)


def remove_files_with_extension_other_than_fastq_gz(directory):
    files_in_directory = os.listdir(directory)
    files_to_delete = [file for file in files_in_directory if not file.endswith(".fastq.gz")]
    for file in files_to_delete:
        path_to_file = os.path.join(directory, file)
        os.remove(path_to_file)
