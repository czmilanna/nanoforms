task nanofilt {
    File fastq_file
    Int headcrop
    Int q

    command {
        NanoFilt -q ${q} --headcrop ${headcrop} ${fastq_file} | gzip > nanofilt.fastq.gz
    }

    output {
        File out = "nanofilt.fastq.gz"
    }

    runtime {
        docker: "quay.io/biocontainers/nanofilt:2.7.1--py_0"
    }
}

task unicycler {
    File fastq_file
    File ilumina_1
    File ilumina_2

    command {
        unicycler -t 8 -1 ${ilumina_1} -2 ${ilumina_2} -l ${fastq_file} -o MSP6M_hybrid_out
    }

    output {
        File out = "MSP6M_hybrid_out/assembly.fasta"
        File graph = "MSP6M_hybrid_out/assembly.gfa"
    }

    runtime {
        docker: "quay.io/biocontainers/unicycler:0.3.0b--py35_1"
    }
}


task bandage {
    File graph

    command {
        Bandage image ${graph} assembly_image.jpg
    }

    output {
        File out = "assembly_image.jpg"
    }

    runtime {
        docker: "quay.io/biocontainers/bandage:0.8.1--hc9558a2_2"
    }
}

task quast {
    File consensus_fasta

    command {
        quast ${consensus_fasta}
    }

    output {
        File report_html = "quast_results/latest/report.html"
        Array[File] reports = glob("quast_results/latest/*.txt")
        Array[File] pdfs = glob("quast_results/latest/basic_stats/*.pdf")
    }

    runtime {
        docker: "quay.io/biocontainers/quast:3.2"
    }
}

workflow prz_hybrid_assembly {
    File fastq_file

    call nanofilt {
        input:
            fastq_file = fastq_file
    }

    call unicycler {
        input:
            fastq_file = nanofilt.out
    }

    call bandage {
        input:
            graph = unicycler.graph
    }

    call quast {
        input:
            consensus_fasta = unicycler.out
    }

    output {
        File consensus = unicycler.out
        File assembly_image = bandage.out
        File report_html = quast.report_html
        Array[File] reports = quast.reports
        Array[File] pdfs = quast.pdfs
    }
}