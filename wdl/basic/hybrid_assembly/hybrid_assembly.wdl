task gunzip_all {
    File nanopore_directory

    command {
        gunzip -c $(find ${nanopore_directory} -type f -name "*.fastq.gz") > gunzip.fastq
    }

    output {
        File out = "gunzip.fastq"
    }

    runtime {
        docker: "ubuntu:latest"
    }
}

task nanofilt {
    File nanopore_fastq
    Int nanopore_q
    Int nanopore_headcrop

    command {
        NanoFilt -q ${nanopore_q} --headcrop ${nanopore_headcrop} ${nanopore_fastq} | gzip > nanopore_filt.fastq.gz
    }

    output {
        File nanopore_filt = "nanopore_filt.fastq.gz"
    }

    runtime {
        docker: "quay.io/biocontainers/nanofilt:2.7.1--py_0"
    }
}

task fastp {
    File illumina_fastq1
    File illumina_fastq2
    Int illumina_q

    command {
        fastp -t 8 -5 -3 -q ${illumina_q} -i ${illumina_fastq1} -I ${illumina_fastq2} -o illumina_fastq1.fastq.gz -O illumina_fastq2.fastq.gz
    }

    output {
        File illumina_filt1 = "illumina_fastq1.fastq.gz"
        File illumina_filt2 = "illumina_fastq2.fastq.gz"
        File out1 = "fastp.html"
        File out2 = "fastp.json"
    }

    runtime {
        docker: "quay.io/biocontainers/fastp:0.18.0--hd28b015_0"
    }
}

task kraken2 {
    File illumina_fastq1
    File illumina_fastq2
    File kraken_db

    command {
        kraken2 --db ${kraken_db} --use-names --report C600_kraken2_report --output C600_kraken2_output --gzip-compressed --use-names --paired ${illumina_fastq1} ${illumina_fastq2}
    }

    output {
        File out1 = "C600_kraken2_report"
    }

    runtime {
        docker: "quay.io/biocontainers/kraken2:2.1.0--pl526hc9558a2_0"
    }
}

task krakentools {
    File kraken_report

    command {
        kreport2krona.py -r ${kraken_report} -o C600_kraken2_krona
    }

    output {
        File out1 = "C600_kraken2_krona"
    }

    runtime {
        docker: "quay.io/biocontainers/krakentools:0.1--py_0"
    }
}

task krona {
    File krakentools_report

    command {
        ktImportText ${krakentools_report} -o C600_kraken2_krona.html
    }

    output {
        File out1 = "C600_kraken2_krona.html"
    }

    runtime {
        docker: "quay.io/biocontainers/krona:2.7.1--pl526_3"
    }
}


task unicycler {
    File nanopore_fastq
    File ilumina_1
    File ilumina_2

    command {
        unicycler -t 4 -1 ${ilumina_1} -2 ${ilumina_2} -l ${nanopore_fastq} -o MSP6M_hybrid_out
    }

    output {
        File out = "MSP6M_hybrid_out/assembly.fasta"
        File graph = "MSP6M_hybrid_out/assembly.gfa"
        File out2 = "MSP6M_hybrid_out"
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
        quast ${consensus_fasta} --glimmer --rna-finding
    }

    output {
        File out1 = "quast_results/latest/report.html"
        File out2 = "quast_results/latest"
    }

    runtime {
        docker: "quay.io/biocontainers/quast:5.0.2--py37pl526hb5aa323_2"
    }
}

task prokka {
    File consensus_fasta
    String genus
    String species
    String strain
    String plasmid

    command {
        mv ${consensus_fasta} consensus.fa
        prokka --outdir out --prefix prokka consensus.fa ${genus} ${species} ${strain} ${plasmid}
    }

    output {
        File out1 = "out/prokka.txt"
        File out2 = "out"
    }

    runtime {
        docker: "quay.io/biocontainers/prokka:1.14.6--pl526_0"
    }
}

workflow prz_hybrid_assembly {
    File nanopore_directory
    File illumina_read1
    File illumina_read2
    File kraken_db

    call gunzip_all {
        input:
            nanopore_directory = nanopore_directory
    }

    call nanofilt {
        input:
            nanopore_fastq = gunzip_all.out
    }

    call fastp {
        input:
            illumina_fastq1 = illumina_read1,
            illumina_fastq2 = illumina_read2
    }

    call kraken2 {
        input:
            illumina_fastq1 = illumina_read1,
            illumina_fastq2 = illumina_read2,
            kraken_db = kraken_db
    }

    call krakentools {
        input:
            kraken_report = kraken2.out1
    }

    call krona {
        input:
            krakentools_report = krakentools.out1
    }

    call unicycler {
        input:
            nanopore_fastq = nanofilt.nanopore_filt,
            ilumina_1 = fastp.illumina_filt1,
            ilumina_2 = fastp.illumina_filt2
    }

    call bandage {
        input:
            graph = unicycler.graph
    }

    call quast {
        input:
            consensus_fasta = unicycler.out
    }

    call prokka {
        input:
            consensus_fasta = unicycler.out
    }

    output {
        File consensus = unicycler.out
        File unicycler_graph = unicycler.graph
        File assembly_image = bandage.out
        File report_html = quast.out1
        File quast_logs = quast.out2
        File prokka_txt = prokka.out1
        File prokka_logs = prokka.out2
        File illumina_html = fastp.out1
        File illumina_json = fastp.out2
        File krona_report = krona.out1
        File kraken2_report = kraken2.out1
        File krakentools_report = krakentools.out1
    }
}