task gunzip_all {
    File fastq_directory

    command {
        gunzip -c $(find ${fastq_directory} -type f -name "*.fastq.gz") > gunzip.fastq
    }

    output {
        File out = "gunzip.fastq"
    }

    runtime {
        docker: "ubuntu:latest"
    }
}

task nanofilt {
    File fastq_file
    Int q
    Int headcrop

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

task filtlong {
    File fastq_file
    Int target_bases
    Int min_length

    command {
        filtlong --min_length ${min_length} --target_bases ${target_bases} ${fastq_file} | gzip > filtlong.fastq.gz
    }

    output {
        File out = "filtlong.fastq.gz"
    }

    runtime {
        docker: "quay.io/biocontainers/filtlong:0.1.0--0"
    }
}

task flye {
    File fastq_gz_file
    String g

    command {
        mkdir -p /tmp && export TMPDIR=/tmp && flye -t 8 --nano-raw ${fastq_gz_file} ${g} -o out
    }

    output {
        File out1 = "out/assembly_graph.gfa"
        File out2 = "out/assembly.fasta"
        File out3 = "out/assembly_info.txt"
        File out4 = "out"
    }

    runtime {
        docker: "quay.io/biocontainers/flye:2.8.1--py38h1c8e9b9_1"
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

task rebaler {
    File fastq_gz_file
    File assembly_fasta

    command {
        rebaler -t 8 ${assembly_fasta} ${fastq_gz_file} > rebaler.fasta
    }

    output {
        File out = "rebaler.fasta"
    }

    runtime {
        docker: "quay.io/biocontainers/rebaler:0.2.0--py_1"
    }
}

task medaka {
    File fastq_gz_file
    File assembly_fasta

    command {
        medaka_consensus -i ${fastq_gz_file} -d ${assembly_fasta} -o racon_4_medaka_MSP5 -t 8
    }

    output {
        File out1 = "racon_4_medaka_MSP5/consensus.fasta"
        File out2 = "racon_4_medaka_MSP5"

    }

    runtime {
        docker: "quay.io/biocontainers/medaka:1.0.1--py36h148d290_0"
    }
}

task quast {
    File consensus_medaka
    File consensus_rebaler
    File consensus_flye

    command {
        mv ${consensus_flye} assembly.fasta
        mv ${consensus_rebaler} polished_genome.fasta
        mv ${consensus_medaka} consensus.fasta

        quast assembly.fasta polished_genome.fasta consensus.fasta --glimmer --rna-finding
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

workflow prz_data_assembly {
    File fastq_directory

    call gunzip_all {
        input:
            fastq_directory = fastq_directory
    }

    call nanofilt {
        input:
            fastq_file = gunzip_all.out
    }

    call filtlong {
        input:
            fastq_file = nanofilt.out
    }

    call flye {
        input:
            fastq_gz_file = filtlong.out
    }

    call bandage {
        input:
            graph = flye.out1
    }

    call rebaler {
        input:
            fastq_gz_file = nanofilt.out,
            assembly_fasta = flye.out2
    }

    call medaka {
        input:
            fastq_gz_file = nanofilt.out,
            assembly_fasta = rebaler.out
    }

    call quast {
        input:
            consensus_medaka = medaka.out1,
            consensus_rebaler = rebaler.out,
            consensus_flye = flye.out2
    }

    call prokka {
        input:
            consensus_fasta = medaka.out1
    }

    output {
        File assembly_graph = flye.out1
        File flye_info = flye.out3
        File flye_logs = flye.out4
        File assembly_image = bandage.out
        File consensus_fasta = medaka.out1
        File medaka_logs = medaka.out2
        File report_html = quast.out1
        File quast_logs = quast.out2
        File prokka_txt = prokka.out1
        File prokka_logs = prokka.out2
    }
}