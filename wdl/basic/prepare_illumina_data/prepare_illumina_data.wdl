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

task fastqc {
    File fastq_file

    command {
        OUT_DIR=$PWD/out && mkdir -p $OUT_DIR && fastqc -t 8 -o $OUT_DIR ${fastq_file} && unzip out/gunzip_fastqc.zip
    }

    output {
        File out_html = "out/gunzip_fastqc.html"
        File out_txt = "gunzip_fastqc/fastqc_data.txt"
        File ? adapter_content = "gunzip_fastqc/Images/adapter_content.png"
        File ? duplication_levels = "gunzip_fastqc/Images/duplication_levels.png"
        File ? per_base_n_content = "gunzip_fastqc/Images/per_base_n_content.png"
        File ? per_base_quality = "gunzip_fastqc/Images/per_base_quality.png"
        File ? per_base_sequence_content = "gunzip_fastqc/Images/per_base_sequence_content.png"
        File ? per_sequence_gc_content = "gunzip_fastqc/Images/per_sequence_gc_content.png"
        File ? per_sequence_quality = "gunzip_fastqc/Images/per_sequence_quality.png"
        File ? per_tile_quality = "gunzip_fastqc/Images/per_tile_quality.png"
        File ? sequence_length_distribution = "gunzip_fastqc/Images/sequence_length_distribution.png"
    }

    runtime {
        docker: "quay.io/biocontainers/fastqc:0.11.9--0"
    }
}

workflow prz_prepare_illumina_data {
    File data_directory

    call gunzip_all {
        input:
            data_directory = data_directory
    }

    call fastqc {
        input:
            fastq_file = gunzip_all.out
    }

    output {
        File out_html = fastqc.out_html
        File out_txt = fastqc.out_txt
        File ? adapter_content = fastqc.adapter_content
        File ? duplication_levels = fastqc.duplication_levels
        File ? per_base_n_content = fastqc.per_base_n_content
        File ? per_base_quality = fastqc.per_base_quality
        File ? per_base_sequence_content = fastqc.per_base_sequence_content
        File ? per_sequence_gc_content = fastqc.per_sequence_gc_content
        File ? per_sequence_quality = fastqc.per_sequence_quality
        File ? per_tile_quality = fastqc.per_tile_quality
        File ? sequence_length_distribution = fastqc.sequence_length_distribution
    }
}