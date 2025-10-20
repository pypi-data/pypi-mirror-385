#!/usr/bin/python

# Copyright 2024 Ferdinand Popp, Lina Sieverling, Philip Ginsbach, Lars Feuerbach

# This file is part of TelomereHunter2.

# TelomereHunter2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# TelomereHunter2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with TelomereHunter2. If not, see <http://www.gnu.org/licenses/>.

import cProfile
import io
import logging
import os
import pstats
import re
import shutil
import stat
import sys
import tempfile
import time

import pandas as pd
import pysam


def measure_time(func):
    """Wrapper function to simply print the execution time for a function"""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time for {func.__name__}: {elapsed_time} seconds")
        return result

    return wrapper


def profile_function(func, *args, **kwargs):
    """Wrapper function to profile a function"""
    pr = cProfile.Profile()
    pr.enable()
    result = func(*args, **kwargs)
    pr.disable()
    s = io.StringIO()
    sortby = "cumulative"
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(5)  # This will print only the top 10 entries
    print(s.getvalue())
    return result


def get_reverse_complement(dna_sequence):
    """Get the reverse complement of a DNA sequence."""
    complement_dict = {"A": "T", "T": "A", "C": "G", "G": "C", "N": "N"}
    complemented_sequence = (complement_dict[base] for base in reversed(dna_sequence))
    return "".join(complemented_sequence)


def get_band_info(banding_file):
    # Get band lengths
    band_info = pd.read_table(
        banding_file, sep="\t", names=["chr", "start", "end", "band_name", "stain"]
    )  # maybe not specify col names?
    band_info["chr"] = band_info["chr"].str.replace("chr", "")
    band_info["length"] = band_info["end"] - band_info["start"]
    chrs = band_info["chr"].unique()
    sorted_chromosomes = sorted(
        chrs, key=lambda x: (int(x) if x.isdigit() else float("inf"), x)
    )
    return band_info, sorted_chromosomes


def assure_dir_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)


def file_exists(parser, path):
    if path is None:
        return None
    if not os.path.exists(path):
        parser.error("The file %s does not exist!" % path)
    return path


def check_banding_file(banding_file, outdir=None):
    try:
        try:
            df = pd.read_csv(banding_file, sep="\t", header=None)
        except Exception:
            try:
                df = pd.read_csv(banding_file, header=None)
            except Exception:
                raise ValueError("Banding file could not be read as TSV or CSV.")

        if df.shape[1] < 4:
            raise ValueError(
                f"File has fewer than 4 columns. Found {df.shape[1]} columns."
            )
        type_errors = []
        if not all(isinstance(x, str) for x in df[0].dropna()):
            type_errors.append("Column 1 should contain strings (chromosome names)")
        for col_idx in [1, 2]:
            df[col_idx] = pd.to_numeric(df[col_idx], errors="coerce")
            if df[col_idx].isna().any():
                type_errors.append(f"Column {col_idx + 1} should contain integers")
        if not all(isinstance(x, str) for x in df[3].dropna()):
            type_errors.append("Column 4 should contain strings (band names)")
        if type_errors:
            error_msg = "Invalid column types:\n" + "\n".join(
                f"- {err}" for err in type_errors
            )
            raise ValueError(error_msg)
        chromosome_level_only = df[0].nunique() == len(df)
        if chromosome_level_only:
            print("!!! Only chromosome-level data found, no band information. !!!")
            print("The banding file should be discarded.")
            subs_cytobands_df = generate_banding_file(df)
            print(
                "\nGenerated substitution cytoband information (5% from chromosome ends):"
            )
            print(subs_cytobands_df.head())
            print(f"Total generated bands: {len(subs_cytobands_df)}")
            generated_banding_file_path = (
                f"{outdir}/generated_bandingfile_5percent_ends.txt"
            )
            subs_cytobands_df.to_csv(generated_banding_file_path, sep="\t", index=False)
            print(
                f"Saved cytoband information (5% from chromosome ends): {generated_banding_file_path}"
            )
            return generated_banding_file_path
        else:
            print("Band-level information found. File is valid for detailed analysis.")
            return banding_file
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)


def generate_banding_file(df):
    bands_df = []
    for _, row in df.iterrows():
        chrom = row[0]
        start = row[1]
        end = row[2]
        band_width = end - start
        p_terminal = start + int(0.05 * band_width)
        q_terminal = end - int(0.05 * band_width)
        bands_df.append([chrom, start, p_terminal, f"{chrom}pter"])
        bands_df.append([chrom, p_terminal, q_terminal, f"{chrom}pq"])
        bands_df.append([chrom, q_terminal, end, f"{chrom}qter"])
    return pd.DataFrame(bands_df)


def get_bamfile_reference_genome(bam_file_path):
    try:
        mode = "rb" if bam_file_path.endswith(".bam") else "rc"
        with pysam.AlignmentFile(bam_file_path, mode=mode) as bam_file:
            header = bam_file.header.to_dict()
            reference_genome_string = header["SQ"][0]
            print(f"Input file is based on reference genome: {reference_genome_string}")
    except KeyError:
        return "Error when extracting reference genome from bam file."


def check_and_create_index(bam_path):
    bam_path = os.path.abspath(bam_path)
    index_path = bam_path + ".bai"
    if os.path.exists(index_path):
        return_bam = bam_path
    else:
        if os.access(os.path.dirname(bam_path), os.W_OK):
            pysam.index(bam_path)
            return_bam = bam_path
        else:
            temp_dir = os.path.abspath(tempfile.mkdtemp("tmp_TH2"))
            os.chmod(temp_dir, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            temp_bam_path = os.path.join(temp_dir, os.path.basename(bam_path))
            try:
                os.symlink(bam_path, temp_bam_path)
            except OSError as e:
                print(f"Symbolic link creation failed: {e}")
            pysam.index(temp_bam_path)
            return_bam = temp_bam_path
    return return_bam


def delete_temp_dir(tumor_bam, control_bam, temp_dir):
    temp_exist = [
        os.path.dirname(path)
        for path in [tumor_bam, control_bam]
        if path is not None and temp_dir in path
    ]
    if temp_exist:
        try:
            shutil.rmtree(temp_exist[0])
            print(f"Folder '{temp_exist}' successfully deleted.")
        except Exception as e:
            print(f"Error deleting folder '{temp_exist}': {e}")


def has_filtering_output(outdir, pid, sample_id):
    sample_dir = os.path.join(outdir, f"{sample_id}_TelomerCnt_{pid}")
    files = [
        os.path.join(sample_dir, f"{pid}_filtered.bam"),
        os.path.join(sample_dir, f"{pid}_filtered_name_sorted.bam"),
        os.path.join(sample_dir, f"{pid}_readcount.tsv"),
        os.path.join(sample_dir, f"{pid}_{sample_id}_gc_content.tsv"),
    ]
    return all(os.path.exists(file) for file in files)


def check_and_prompt_filtering(
    filter_telomere_reads_flag, tumor_flag, control_flag, outdir, pid, no_filtering
):
    tumor_output_missing = (
        not has_filtering_output(outdir, pid, "tumor") if tumor_flag else False
    )
    control_output_missing = (
        not has_filtering_output(outdir, pid, "control") if control_flag else False
    )
    if tumor_output_missing and control_output_missing:
        print("Running filtering step as no output files are present")
        if filter_telomere_reads_flag and no_filtering:
            print(
                "!Denied skipping the filtering with --noFiltering, as no output files were present!"
            )
        filter_T, filter_C = True, True
    elif control_output_missing or tumor_output_missing:
        print("Running filtering step as not all output files are already present")
        if filter_telomere_reads_flag and no_filtering:
            print(
                "!Denied skipping the filtering with --noFiltering, as not all output files were present!"
            )
        filter_T, filter_C = tumor_output_missing, control_output_missing
    else:
        if filter_telomere_reads_flag:
            print(
                "Filtering samples, but output files are already present. Consider using the --noFiltering flag"
            )
            filter_T, filter_C = tumor_flag, control_flag
        else:
            print("Skipped filtering samples with --noFiltering flag")
            filter_T, filter_C = False, False
    return filter_T, filter_C


def get_repeat_threshold_from_summary(args):
    summary_file = os.path.join(args.outdir, f"{args.pid}_summary.tsv")
    try:
        summary = pd.read_csv(summary_file, sep="\t")
        if "repeat_threshold_used" in summary.columns:
            unique_thresholds = summary["repeat_threshold_used"].dropna().unique()
            if len(unique_thresholds) == 1:
                return str(int(unique_thresholds[0]))
            elif len(unique_thresholds) > 1:
                return "n"
        else:
            print(f"Error: Column 'repeat_threshold_used' not found in {summary_file}.")
            return "n"
    except Exception as e:
        print(f"Error reading file {summary_file}: {e}")
        return "n"


def validate_args(args):
    # check which bam files were specified
    if not args.plot_mode and not any([args.tumor_bam, args.control_bam]):
        raise ValueError(
            "argument -ibt/--inputBamTumor or -ibc/--inputBamControl or -icc or -ict is required"
        )

    if not args.tumor_bam:
        args.tumor_flag = False
        print(
            "Tumor BAM/CRAM file was not specified. Only running control BAM/CRAM file."
        )
    elif not args.control_bam:
        args.control_flag = False
        print(
            "Control BAM/CRAM file was not specified. Only running tumor BAM/CRAM file."
        )

    # Check band file format
    if args.banding_file:
        if args.tumor_bam or args.control_bam:
            get_bamfile_reference_genome(args.tumor_bam or args.control_bam)

        # check banding file and if only chromosomes, create 5% bands
        args.banding_file = check_banding_file(args.banding_file, args.outdir)
    else:
        print(
            "No banding file supplied, so all banding steps will be skipped and specific plots omitted."
        )

    # check if repeats only contains ACGT and are between 4 and 9 bases
    for repeat in args.repeats:
        if len(repeat) < 4 or len(repeat) > 9:
            raise ValueError(
                "argument -r/--repeats should be between 4 and 9 bases long."
            )
        x = re.search(r"[^ACGT]", repeat)
        if x is not None:
            raise ValueError(
                "argument -r/--repeats should only contain the letters ACGT."
            )

    for repeat in args.TVRs_for_context:
        x = re.search(r"[^ACGT]", repeat)
        if x is not None:
            raise ValueError(
                "argument -rc/--repeatsContext should only contain the letters ACGT."
            )

    # check if repeat threshold is min 4 else print warning
    if args.repeat_threshold_set and args.repeat_threshold_set < 4:
        print("!! Warning: Repeat thresholds should be at least 4.")

    # check that str input from fixedrepeatthreshold is either int or two ints separated by comma
    if args.fixed_repeat_thresholds:
        try:
            thresholds = list(map(int, args.fixed_repeat_thresholds.split(",")))
            if len(thresholds) not in [1, 2]:
                raise ValueError(
                    "Invalid number of thresholds provided. Use one value or two values separated by a comma."
                )
            if any(threshold < 4 for threshold in thresholds):
                print("!! Warning: Repeat thresholds should be at least 4.")
        except ValueError as e:
            raise ValueError(f"Invalid input for --fixedRepeatThresholds: {e}")

    # check if bp for sequencing context is divisible by 6 or base telomere sequence given
    if args.bp_context % len(args.repeats[0]) != 0:
        raise ValueError(
            f"argument -bp/--bpContext must be a multiple of length of first telomere repeat sequence /"
            f'{len(args.repeats[0])}. By default "TTAGGG" so multiple of 6 (e.g. 6, 12, 18, ...).'
        )

    if args.mapq_threshold < 0 or args.mapq_threshold > 40:
        raise ValueError(
            "argument -mqt/--mappingQualityThreshold must be an integer between 0 and 40."
        )

    if args.gc_lower < 0 or args.gc_lower > 100:
        raise ValueError(
            "argument -gc1/--lowerGC must be an integer between 0 and 100."
        )

    if args.gc_upper < 0 or args.gc_upper > 100:
        raise ValueError(
            "argument -gc2/--upperGC must be an integer between 0 and 100."
        )

    if args.gc_lower >= args.gc_upper:
        raise ValueError(
            "argument -gc1/--lowerGC must be less than argument -gc2/--upperGC."
        )


def validate_plotting_options(args):
    if args.plotNone and (
        args.plotChr
        or args.plotFractions
        or args.plotTelContent
        or args.plotGC
        or args.plotRepeatFreq
        or args.plotTVR
        or args.plotSingleton
    ):
        raise ValueError(
            "argument -pno/--plotNone should not be specified when other plotting options are selected."
        )

    # can be str or list so change to list
    if isinstance(args.plotFileFormat, str):
        args.plotFileFormat = [args.plotFileFormat]
    if args.plotFileFormat == ["all"] or args.plotFileFormat == "all":
        args.plotFileFormat = ["pdf", "png", "svg", "html"]

    if not args.plotNone and any(fmt != "html" for fmt in args.plotFileFormat):
        # Kaleido check static export
        static_export_failed = False
        try:
            import plotly.graph_objects as go

            fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
            img_path = "test_plot.png"
            logging.getLogger("choreographer.browser_async").setLevel(logging.ERROR)
            fig.write_image(img_path)
            del fig
            if os.path.exists(img_path):
                os.remove(img_path)
        except ImportError:
            print(
                "Warning: Plotly is not installed. Removing plotting with --plotNone."
            )
            args.plotNone = True
            static_export_failed = True
        except Exception as e:
            print(
                "Warning: Kaleido package or Chromium is not installed or an error occurred. "
                f"Removing all formats except HTML from --plotFileFormat. Details: {e}"
            )
            static_export_failed = True
        if static_export_failed:
            args.plotFileFormat = ["html"]

    # if no plotting options are selected: plot all diagrams.
    if (
        not args.plotChr
        and not args.plotFractions
        and not args.plotTelContent
        and not args.plotGC
        and not args.plotRepeatFreq
        and not args.plotTVR
        and not args.plotSingleton
        and not args.plotNone
    ):
        args.plotChr = True
        args.plotFractions = True
        args.plotTelContent = True
        args.plotGC = True
        args.plotRepeatFreq = True
        args.plotTVR = True
        args.plotSingleton = True
    # no banding info remove plots
    if not args.banding_file:
        args.plotChr = False
        args.plotFractions = False


def set_execution_flags(args):
    args.filter_telomere_reads_flag = not args.noFiltering
    args.sort_telomere_reads_flag = args.estimate_telomere_content_flag = True
    args.TVR_screen_flag = args.TVR_context_flag = True

    if args.repeats[0] != "TTAGGG":
        print(
            "The first repeat to screen for is not canonical TTAGGG! Please double check."
        )
        args.TVR_screen_flag = args.TVR_context_flag = args.plotTVR = (
            args.plotSingleton
        ) = False


def combine_summary_files(outdir, pid, tumor_flag, control_flag):
    # Define the path for the combined summary file
    summary_path = os.path.join(outdir, f"{pid}_summary.tsv")

    tumor_summary_path = os.path.join(
        outdir, f"tumor_TelomerCnt_{pid}", f"{pid}_tumor_summary.tsv"
    )
    control_summary_path = os.path.join(
        outdir, f"control_TelomerCnt_{pid}", f"{pid}_control_summary.tsv"
    )

    # Check if both tumor and control flags are True
    if tumor_flag and control_flag:
        # Copy the tumor summary file to the combined summary file
        shutil.copyfile(tumor_summary_path, summary_path)

        # Append the last line of the control summary file to the combined summary file
        with open(control_summary_path, "r") as control_file, open(
            summary_path, "a"
        ) as combined_file:
            last_line = control_file.readlines()[-1]
            combined_file.write(last_line)

    # Check if only the tumor flag is True
    elif tumor_flag:
        # Copy the tumor summary file to the combined summary file
        shutil.copyfile(tumor_summary_path, summary_path)
    # Check if only the control flag is True
    elif control_flag:
        # Copy the control summary file to the combined summary file
        shutil.copyfile(control_summary_path, summary_path)


def get_version_from_package():
    """
    Read the project version from pyproject.toml using regex parsing.

    Returns:
        str: The project version string, or "unknown" if not found
    """
    try:
        from importlib.metadata import PackageNotFoundError, version

        try:
            return version("telomerehunter2")
        except PackageNotFoundError:
            return "unknown - check pyproject.toml file"
    except ImportError:
        return "unknown - check pyproject.toml file"


def print_copyright_message():
    version = get_version_from_package()
    print("\n")
    print(
        "\tTelomereHunter2 Copyright 2024 Ferdinand Popp, Lina Sieverling, Philip Ginsbach, Chen Hong, Lars Feuerbach"
    )
    print("\tThis program comes with ABSOLUTELY NO WARRANTY.")
    print("\tThis is free software, and you are welcome to redistribute it")
    print(
        "\tunder certain conditions. For details see the GNU General Public License v3.0"
    )
    print(
        "\tin the license copy received with TelomereHunter2 or <http://www.gnu.org/licenses/>."
    )
    print("\n")
    print(f"TelomereHunter2 {version}")
    print("\n")
