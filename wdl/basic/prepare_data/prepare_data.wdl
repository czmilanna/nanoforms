task gunzip_all {
    File data_directory

    command {
        gunzip -c $(find ${data_directory} -type f -name "*.fastq.gz") > gunzip.fastq
    }

    output {
        File out = "gunzip.fastq"
    }

    runtime {
        docker: "ubuntu:latest"
    }
}

task nanoplot {
    File fastq_file

    command {
        NanoPlot --fastq ${fastq_file}
    }

    output {
        Array[File] images = glob("*.png")
        Array[File] htmls = glob("*.html")
        File stats = "NanoStats.txt"
    }

    runtime {
        docker: "quay.io/biocontainers/nanoplot:1.32.0--py_0"
    }
}

workflow prz_prepare_data {
    File data_directory

    call gunzip_all {
        input:
            data_directory = data_directory
    }

    call nanoplot {
        input:
            fastq_file = gunzip_all.out
    }

    output {
        Array[File] images = nanoplot.images
        Array[File] htmls = nanoplot.htmls
        File stats = nanoplot.stats
    }
}

