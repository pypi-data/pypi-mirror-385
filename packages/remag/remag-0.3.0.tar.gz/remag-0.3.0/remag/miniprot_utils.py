"""
Miniprot utilities for core gene duplication checking.

This module consolidates the core gene duplication checking functionality
that was previously duplicated between quality.py and refinement.py.
"""

import json
import os
import shutil
import subprocess
from tqdm import tqdm
from loguru import logger

from .utils import extract_base_contig_name, ContigHeaderMapper, initialize_duplication_columns


def check_miniprot_available():
    """Check if miniprot is available in PATH."""
    return shutil.which("miniprot") is not None


def estimate_organisms_from_all_contigs(fragments_dict, args, target_coverage_threshold=0.55, identity_threshold=0.35):
    """
    Run miniprot on all contigs to estimate the number of organisms based on core gene duplications.

    This function treats all contigs as a single group and counts how many times each
    single-copy core gene appears. The duplication counts provide an estimate of organism diversity.

    Args:
        fragments_dict: Dictionary mapping headers to sequences
        args: Arguments object containing output directory, cores, etc.
        target_coverage_threshold: Minimum target coverage for alignments
        identity_threshold: Minimum identity for alignments

    Returns:
        dict: {gene_family: occurrence_count} for all core genes found
    """
    logger.info("Estimating organism count by running miniprot on all contigs...")

    # Check if miniprot is available
    if not check_miniprot_available():
        logger.error("miniprot not found in PATH - cannot estimate organisms")
        logger.error("Install miniprot with: conda install -c bioconda miniprot")
        return {}

    db_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "db", "refseq_db.faa.gz"
    )
    if not os.path.exists(db_path):
        logger.warning("Eukaryotic database not found - cannot estimate organisms")
        return {}

    # Create temporary directory
    temp_dir = os.path.join(args.output, "temp_organism_estimation")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Create a single FASTA file with all contigs
        all_contigs_fasta = os.path.join(temp_dir, "all_contigs.fa")
        with open(all_contigs_fasta, "w") as f:
            for header, data in fragments_dict.items():
                seq = data["sequence"]
                f.write(f">{header}\n")
                for i in range(0, len(seq), 60):
                    f.write(f"{seq[i: i+60]}\n")

        logger.info(f"Running miniprot on {len(fragments_dict)} contigs for organism estimation...")

        # Run miniprot
        miniprot_output = os.path.join(temp_dir, "all_contigs.paf")
        miniprot_stderr = os.path.join(temp_dir, "all_contigs.stderr")

        cmd_list = [
            "miniprot",
            "-I",
            "-t", str(args.cores),
            "--outs=0.95",
            all_contigs_fasta,
            db_path
        ]

        if args.verbose:
            logger.debug(f"Running miniprot command: {' '.join(cmd_list)}")

        with open(miniprot_output, 'w') as stdout_file, \
             open(miniprot_stderr, 'w') as stderr_file:

            process = subprocess.run(
                cmd_list,
                stdout=stdout_file,
                stderr=stderr_file,
                timeout=14400,  # 4 hour timeout
                check=False
            )
            result = process.returncode

        if result != 0:
            logger.error(f"miniprot failed with exit code {result}")
            if os.path.exists(miniprot_stderr) and os.path.getsize(miniprot_stderr) > 0:
                with open(miniprot_stderr, "r") as f:
                    logger.error(f"miniprot error: {f.read().strip()}")
            return {}

        # Parse miniprot output to count gene occurrences and build cache in single pass
        gene_counts = {}  # {gene_family: count}
        gene_mappings = {}  # {contig_name: {gene_family: {score, coverage, identity}}}

        if os.path.exists(miniprot_output) and os.path.getsize(miniprot_output) > 0:
            with open(miniprot_output, "r") as paf_file:
                for line in paf_file:
                    if line.startswith("#") or not line.strip():
                        continue

                    parts = line.strip().split("\t")
                    if len(parts) >= 11:
                        try:
                            query_name = parts[0]  # Protein name
                            target_name = parts[5]  # Contig name
                            target_length = int(parts[6])
                            target_start = int(parts[7])
                            target_end = int(parts[8])
                            matching_bases = int(parts[9])
                            alignment_length = int(parts[10])

                            # Extract gene family code
                            full_gene_id = query_name.split()[0]
                            if ":" in full_gene_id:
                                gene_family_code = full_gene_id.split(":")[-1]
                            else:
                                gene_family_code = full_gene_id

                            # Calculate quality metrics
                            target_coverage = (
                                (target_end - target_start) / target_length
                                if target_length > 0 else 0
                            )
                            identity = (
                                matching_bases / alignment_length
                                if alignment_length > 0 else 0
                            )

                            # Only consider high-quality alignments
                            if target_coverage >= target_coverage_threshold and identity >= identity_threshold:
                                score = target_coverage * identity

                                # Initialize contig entry in gene_mappings if needed
                                if target_name not in gene_mappings:
                                    gene_mappings[target_name] = {}

                                # Keep best alignment per contig-gene pair
                                if (gene_family_code not in gene_mappings[target_name] or
                                    score > gene_mappings[target_name][gene_family_code]["score"]):
                                    gene_mappings[target_name][gene_family_code] = {
                                        "score": score,
                                        "coverage": target_coverage,
                                        "identity": identity
                                    }

                        except (ValueError, IndexError):
                            continue

        # Count occurrences of each gene family from gene_mappings
        for contig_name, genes in gene_mappings.items():
            for gene_family in genes.keys():
                gene_counts[gene_family] = gene_counts.get(gene_family, 0) + 1

        logger.info(f"Found {len(gene_counts)} core genes across all contigs")

        # Log statistics
        if gene_counts:
            counts_list = list(gene_counts.values())
            max_count = max(counts_list)
            median_count = sorted(counts_list)[len(counts_list) // 2]
            logger.info(f"Core gene occurrence statistics: max={max_count}, median={median_count}")

        # Save cache if we have data
        if gene_mappings:
            cache_path = get_gene_mappings_cache_path(args)
            try:
                import json
                with open(cache_path, "w") as f:
                    json.dump(gene_mappings, f, indent=2)
                logger.info(f"Saved gene mappings cache for {len(gene_mappings)} contigs to {cache_path}")
            except Exception as e:
                logger.warning(f"Failed to save gene mappings cache: {e}")

        return gene_counts

    except Exception as e:
        logger.error(f"Error during organism estimation: {e}")
        return {}

    finally:
        # Clean up temp files unless keeping intermediate
        if not getattr(args, "keep_intermediate", False):
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temporary organism estimation files at: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary files: {e}")
        else:
            logger.info(f"Organism estimation files preserved at: {temp_dir}")


def get_core_gene_duplication_results_path(args):
    """Get the path for the core gene duplication results file."""
    return os.path.join(args.output, "core_gene_duplication_results.json")


def get_gene_mappings_cache_path(args):
    """Get the path for the gene-to-contig mappings cache file."""
    return os.path.join(args.output, "gene_contig_mappings.json")


def parse_and_cache_paf_files(temp_dir, filtered_clusters, args,
                            target_coverage_threshold=0.55, identity_threshold=0.35):
    """
    Parse PAF files from miniprot output and cache gene-to-contig mappings.
    
    This function extracts all gene-to-contig mappings from PAF files and stores
    them in a format that can be reused during refinement without re-running miniprot.
    
    Args:
        temp_dir: Directory containing PAF files
        filtered_clusters: Dictionary of cluster_id -> contig_headers
        args: Arguments object
        target_coverage_threshold: Minimum target coverage for alignments
        identity_threshold: Minimum identity for alignments
    
    Returns:
        dict: {contig_name: {gene_family: {score, coverage, identity}}}
    """
    logger.info("Parsing and caching gene-to-contig mappings from PAF files...")
    
    # Global mapping: contig -> gene_family -> alignment_info
    global_gene_mappings = {}
    
    for cluster_id in filtered_clusters.keys():
        paf_file = os.path.join(temp_dir, f"{cluster_id}.paf")
        
        if not os.path.exists(paf_file) or os.path.getsize(paf_file) == 0:
            continue
            
        with open(paf_file, "r") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                    
                parts = line.strip().split("\t")
                if len(parts) >= 11:
                    try:
                        query_name = parts[0]  # Protein name
                        target_name = parts[5]  # Contig name
                        target_length = int(parts[6])
                        target_start = int(parts[7])
                        target_end = int(parts[8])
                        matching_bases = int(parts[9])
                        alignment_length = int(parts[10])

                        # Extract gene family code from protein name (query)
                        full_gene_id = query_name.split()[0]
                        if ":" in full_gene_id:
                            gene_family_code = full_gene_id.split(":")[-1]
                        else:
                            gene_family_code = full_gene_id

                        # Calculate quality metrics
                        target_coverage = (
                            (target_end - target_start) / target_length
                            if target_length > 0 else 0
                        )
                        identity = (
                            matching_bases / alignment_length
                            if alignment_length > 0 else 0
                        )

                        # Only consider high-quality alignments
                        if target_coverage >= target_coverage_threshold and identity >= identity_threshold:
                            score = target_coverage * identity
                            
                            # Initialize contig entry if needed
                            if target_name not in global_gene_mappings:
                                global_gene_mappings[target_name] = {}
                            
                            # Keep only the best alignment per contig-gene pair
                            if (gene_family_code not in global_gene_mappings[target_name] or
                                score > global_gene_mappings[target_name][gene_family_code]["score"]):
                                global_gene_mappings[target_name][gene_family_code] = {
                                    "score": score,
                                    "coverage": target_coverage,
                                    "identity": identity,
                                }

                    except (ValueError, IndexError):
                        continue
    
    # Save cache if keeping intermediate files
    if getattr(args, "keep_intermediate", False):
        cache_path = get_gene_mappings_cache_path(args)
        with open(cache_path, "w") as f:
            json.dump(global_gene_mappings, f, indent=2)
        logger.info(f"Gene-to-contig mappings cached to {cache_path}")
    
    logger.info(f"Cached gene mappings for {len(global_gene_mappings)} contigs")
    return global_gene_mappings


def check_core_gene_duplications_from_cache(clusters_df, gene_mappings_cache, args):
    """
    Check for duplicated core genes using cached gene-to-contig mappings.
    
    This function reuses existing gene mappings instead of re-running miniprot,
    making it much faster for refinement steps.
    
    Args:
        clusters_df: DataFrame with cluster assignments
        gene_mappings_cache: Dict from parse_and_cache_paf_files()
        args: Arguments object
        
    Returns:
        DataFrame: Updated clusters_df with duplication information
    """
    logger.debug("Checking core gene duplications using cached mappings...")
    
    # Group contigs by cluster
    cluster_contig_dict = {}
    for _, row in clusters_df.iterrows():
        contig_name = row["contig"]
        cluster_id = row["cluster"]
        
        if cluster_id not in cluster_contig_dict:
            cluster_contig_dict[cluster_id] = set()
        cluster_contig_dict[cluster_id].add(contig_name)
    
    duplication_results = {}
    
    for cluster_id, contig_names in cluster_contig_dict.items():
        if cluster_id == "noise":
            continue
            
        # Count gene families present in each contig in this cluster
        contig_genes = {}
        for contig_name in contig_names:
            if contig_name in gene_mappings_cache:
                contig_genes[contig_name] = set(gene_mappings_cache[contig_name].keys())
        
        # Count total occurrences of each gene family across the cluster
        gene_counts = {}
        for contig, gene_families in contig_genes.items():
            for gene_family in gene_families:
                if gene_family not in gene_counts:
                    gene_counts[gene_family] = 0
                gene_counts[gene_family] += 1
        
        # Check for duplications
        duplicated_genes = {
            gene: count for gene, count in gene_counts.items() if count > 1
        }
        has_duplications = len(duplicated_genes) > 0
        
        duplication_results[cluster_id] = {
            "has_duplications": has_duplications,
            "duplicated_genes": duplicated_genes,
            "total_genes_found": len(gene_counts),
        }
    
    # Add duplication information to clusters_df
    clusters_df = initialize_duplication_columns(clusters_df)

    for cluster_id, result in duplication_results.items():
        mask = clusters_df["cluster"] == cluster_id
        clusters_df.loc[mask, "has_duplicated_core_genes"] = result["has_duplications"]
        clusters_df.loc[mask, "duplicated_core_genes_count"] = len(result["duplicated_genes"])
        clusters_df.loc[mask, "total_core_genes_found"] = result["total_genes_found"]

    # Log summary
    bins_with_duplications = sum(
        1 for r in duplication_results.values() if r["has_duplications"]
    )
    total_bins_checked = len(duplication_results)
    logger.info(
        f"Checked {total_bins_checked} bins using cache: {bins_with_duplications} have duplicated core genes"
    )

    # Save results only if keeping intermediate files (consistent with check_core_gene_duplications)
    if getattr(args, "keep_intermediate", False):
        results_path = get_core_gene_duplication_results_path(args)
        try:
            with open(results_path, "w") as f:
                json.dump(duplication_results, f, indent=2)
            logger.debug(f"Saved duplication results to {results_path}")
        except Exception as e:
            logger.warning(f"Failed to save duplication results: {e}")

    return clusters_df


def check_core_gene_duplications(clusters_df, fragments_dict, args, 
                                target_coverage_threshold=0.55, 
                                identity_threshold=0.55,
                                use_header_cache=False):
    """
    Check for duplicated core genes using miniprot.
    
    This function consolidates the logic previously duplicated between
    quality.py and refinement.py with configurable thresholds.
    
    Args:
        clusters_df: DataFrame with cluster assignments
        fragments_dict: Dictionary mapping headers to sequences
        args: Arguments object containing output directory, cores, etc.
        target_coverage_threshold: Minimum target coverage (0.55 for quality, 0.60 for refinement)
        identity_threshold: Minimum identity (0.35 for quality, 0.40 for refinement)
        use_header_cache: Whether to use function-level caching for header lookup
    
    Returns:
        DataFrame: Updated clusters_df with duplication information
    """
    # Check if miniprot is available
    if not check_miniprot_available():
        logger.error("miniprot not found in PATH")
        logger.error("Install miniprot with: conda install -c bioconda miniprot")
        logger.warning("Skipping core gene duplication analysis")
        return initialize_duplication_columns(clusters_df)

    db_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "db", "refseq_db.faa.gz"
    )
    if not os.path.exists(db_path):
        logger.warning(
            "Eukaryotic database not found, skipping core gene duplication check"
        )
        return initialize_duplication_columns(clusters_df)

    logger.info("Checking for duplicated core genes using miniprot...")

    # Create temporary directory
    temp_dir = os.path.join(args.output, "temp_miniprot")
    os.makedirs(temp_dir, exist_ok=True)

    # Group contigs by cluster (clusters_df is now contig-level)
    # Use ContigHeaderMapper for efficient lookups
    if use_header_cache:
        # Use cached mapper if available
        if not hasattr(check_core_gene_duplications, '_mapper_cache'):
            check_core_gene_duplications._mapper_cache = ContigHeaderMapper(fragments_dict)
        mapper = check_core_gene_duplications._mapper_cache
    else:
        # Create new mapper
        mapper = ContigHeaderMapper(fragments_dict)
    
    cluster_contig_dict = {}
    for _, row in clusters_df.iterrows():
        contig_name = row["contig"]
        cluster_id = row["cluster"]

        original_header = mapper.get_header(contig_name)
        if original_header:
            if cluster_id not in cluster_contig_dict:
                cluster_contig_dict[cluster_id] = set()
            cluster_contig_dict[cluster_id].add(original_header)

    # Filter clusters by size and exclude noise
    filtered_clusters = {}
    for cluster_id, contig_headers in cluster_contig_dict.items():
        if cluster_id == "noise":
            continue
        total_size = sum(len(fragments_dict[h]["sequence"]) for h in contig_headers)
        if total_size >= args.min_bin_size:
            filtered_clusters[cluster_id] = contig_headers

    duplication_results = {}

    try:
        for cluster_id, contig_headers in tqdm(
            filtered_clusters.items(), desc="Checking core gene duplications"
        ):
            # Create temporary FASTA file
            bin_fasta = os.path.join(temp_dir, f"{cluster_id}.fa")
            with open(bin_fasta, "w") as f:
                for header in contig_headers:
                    seq = fragments_dict[header]["sequence"]
                    f.write(f">{header}\n")
                    for i in range(0, len(seq), 60):
                        f.write(f"{seq[i: i+60]}\n")

            # Run miniprot
            miniprot_output = os.path.join(temp_dir, f"{cluster_id}.paf")
            miniprot_stderr = os.path.join(temp_dir, f"{cluster_id}.stderr")
            db_to_use = db_path  # Use the compressed file directly
            
            # Build secure command list (no shell injection possible)
            cmd_list = [
                "miniprot",
                "-I",
                "-t", str(args.cores),
                "--outs=0.95",
                bin_fasta,
                db_to_use
            ]

            if args.verbose:
                logger.debug(f"Running miniprot command: {' '.join(cmd_list)}")

            try:
                # Use secure subprocess with proper I/O redirection
                with open(miniprot_output, 'w') as stdout_file, \
                     open(miniprot_stderr, 'w') as stderr_file:
                    
                    process = subprocess.run(
                        cmd_list,
                        stdout=stdout_file,
                        stderr=stderr_file,
                        timeout=14400,  # 4 hour timeout for large datasets
                        check=False    # Don't raise exception on non-zero exit
                    )
                    result = process.returncode
                if result == 0:
                    # Parse miniprot output
                    best_alignments = (
                        {}
                    )  # {(contig, gene_family): {score, coverage, identity}}

                    if (
                        os.path.exists(miniprot_output)
                        and os.path.getsize(miniprot_output) > 0
                    ):
                        if args.verbose:
                            logger.debug(
                                f"Miniprot output file exists and has size: {os.path.getsize(miniprot_output)} bytes"
                            )
                        with open(miniprot_output, "r") as paf_file:
                            for line in paf_file:
                                if line.startswith("#") or not line.strip():
                                    continue

                                parts = line.strip().split("\t")
                                if len(parts) >= 11:
                                    try:
                                        query_name = parts[0]  # Protein name
                                        target_name = parts[5]  # Contig name
                                        target_length = int(parts[6])
                                        target_start = int(parts[7])
                                        target_end = int(parts[8])
                                        matching_bases = int(parts[9])
                                        alignment_length = int(parts[10])

                                        # Extract gene family code from protein name (query)
                                        full_gene_id = query_name.split()[0]
                                        if ":" in full_gene_id:
                                            gene_family_code = full_gene_id.split(":")[
                                                -1
                                            ]
                                        else:
                                            gene_family_code = full_gene_id

                                        # Calculate quality metrics
                                        target_coverage = (
                                            (target_end - target_start) / target_length
                                            if target_length > 0
                                            else 0
                                        )
                                        identity = (
                                            matching_bases / alignment_length
                                            if alignment_length > 0
                                            else 0
                                        )

                                        # Only consider high-quality alignments with configurable thresholds
                                        if target_coverage >= target_coverage_threshold and identity >= identity_threshold:
                                            score = target_coverage * identity
                                            key = (
                                                target_name,
                                                gene_family_code,
                                            )  # Use contig name as key

                                            if (
                                                key not in best_alignments
                                                or score > best_alignments[key]["score"]
                                            ):
                                                best_alignments[key] = {
                                                    "score": score,
                                                    "coverage": target_coverage,
                                                    "identity": identity,
                                                    "gene_family": gene_family_code,
                                                }

                                    except (ValueError, IndexError):
                                        continue

                    # Count gene families present in each contig
                    contig_genes = {}
                    for (contig, gene_family), alignment in best_alignments.items():
                        if contig not in contig_genes:
                            contig_genes[contig] = set()
                        contig_genes[contig].add(gene_family)

                    # Count total occurrences of each gene family
                    gene_counts = {}
                    for contig, gene_families in contig_genes.items():
                        for gene_family in gene_families:
                            if gene_family not in gene_counts:
                                gene_counts[gene_family] = 0
                            gene_counts[gene_family] += 1

                    # Check for duplications
                    duplicated_genes = {
                        gene: count for gene, count in gene_counts.items() if count > 1
                    }
                    has_duplications = len(duplicated_genes) > 0

                    duplication_results[cluster_id] = {
                        "has_duplications": has_duplications,
                        "duplicated_genes": duplicated_genes,
                        "total_genes_found": len(gene_counts),
                    }

                else:
                    # Log miniprot error if available
                    error_msg = f"miniprot failed for {cluster_id} (exit code: {result})"
                    if os.path.exists(miniprot_stderr) and os.path.getsize(miniprot_stderr) > 0:
                        with open(miniprot_stderr, "r") as stderr_file:
                            stderr_content = stderr_file.read().strip()
                            if stderr_content:
                                error_msg += f" - Error: {stderr_content}"
                    logger.warning(error_msg)
                    
                    duplication_results[cluster_id] = {
                        "has_duplications": False,
                        "duplicated_genes": {},
                        "total_genes_found": 0,
                    }

            except Exception as e:
                logger.warning(f"Error running miniprot for {cluster_id}: {e}")
                duplication_results[cluster_id] = {
                    "has_duplications": False,
                    "duplicated_genes": {},
                    "total_genes_found": 0,
                }

        # Parse and cache gene mappings for potential reuse during refinement
        gene_mappings_cache = parse_and_cache_paf_files(
            temp_dir, filtered_clusters, args, target_coverage_threshold, identity_threshold
        )
        
        # Store cache in args for immediate use during refinement
        args._gene_mappings_cache = gene_mappings_cache

    finally:
        # Clean up temp_miniprot folder unless keeping intermediate files
        if not getattr(args, "keep_intermediate", False):
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temporary miniprot files at: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary miniprot files: {e}")
        else:
            logger.info(f"Miniprot files preserved at: {temp_dir}")

    # Add duplication information to clusters_df
    clusters_df = initialize_duplication_columns(clusters_df)

    for cluster_id, result in duplication_results.items():
        mask = clusters_df["cluster"] == cluster_id
        clusters_df.loc[mask, "has_duplicated_core_genes"] = result["has_duplications"]
        clusters_df.loc[mask, "duplicated_core_genes_count"] = len(
            result["duplicated_genes"]
        )
        clusters_df.loc[mask, "total_core_genes_found"] = result["total_genes_found"]

    # Log summary
    bins_with_duplications = sum(
        1 for r in duplication_results.values() if r["has_duplications"]
    )
    total_bins_checked = len(duplication_results)
    logger.info(
        f"Checked {total_bins_checked} bins: {bins_with_duplications} have duplicated core genes"
    )

    # Save results only if keeping intermediate files
    if getattr(args, "keep_intermediate", False):
        results_path = get_core_gene_duplication_results_path(args)
        with open(results_path, "w") as f:
            json.dump(duplication_results, f, indent=2)

    return clusters_df
