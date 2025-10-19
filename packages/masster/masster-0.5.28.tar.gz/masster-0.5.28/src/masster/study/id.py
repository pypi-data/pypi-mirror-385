"""study/id.py

Identification helpers for Study: load a Lib and identify consensus features
by matching m/z (and optionally RT).
"""

from __future__ import annotations


import polars as pl


def lib_load(
    study,
    lib_source,
    polarity: str | None = None,
    adducts: list | None = None,
    iso: str | None = None,
):
    """Load a compound library into the study.

    Args:
        study: Study instance
        lib_source: either a CSV/JSON file path (str) or a Lib instance
        polarity: ionization polarity ("positive" or "negative") - used when lib_source is a CSV/JSON path.
                 If None, uses study.polarity automatically.
        adducts: specific adducts to generate - used when lib_source is a CSV/JSON path
        iso: isotope generation mode ("13C" to generate 13C isotopes, None for no isotopes)

    Side effects:
        sets study.lib_df to a Polars DataFrame and stores the lib object on
        study._lib for later reference.
    """
    # Lazy import to avoid circular imports at module import time
    try:
        from masster.lib.lib import Lib
    except Exception:
        Lib = None

    if lib_source is None:
        raise ValueError("lib_source must be a CSV/JSON file path (str) or a Lib instance")

    # Use study polarity if not explicitly provided
    if polarity is None:
        study_polarity = getattr(study, "polarity", "positive")
        # Normalize polarity names
        if study_polarity in ["pos", "positive"]:
            polarity = "positive"
        elif study_polarity in ["neg", "negative"]:
            polarity = "negative"
        else:
            polarity = "positive"  # Default fallback
        study.logger.debug(f"Using study polarity: {polarity}")

    # Handle string input (CSV or JSON file path)
    if isinstance(lib_source, str):
        if Lib is None:
            raise ImportError(
                "Could not import masster.lib.lib.Lib - required for CSV/JSON loading",
            )

        lib_obj = Lib()

        # Determine file type by extension
        if lib_source.lower().endswith(".json"):
            lib_obj.import_json(lib_source, polarity=polarity, adducts=adducts)
        elif lib_source.lower().endswith(".csv"):
            lib_obj.import_csv(lib_source, polarity=polarity, adducts=adducts)
        else:
            # Default to CSV behavior for backward compatibility
            lib_obj.import_csv(lib_source, polarity=polarity, adducts=adducts)

    # Handle Lib instance
    elif Lib is not None and isinstance(lib_source, Lib):
        lib_obj = lib_source

    # Handle other objects with lib_df attribute
    elif hasattr(lib_source, "lib_df"):
        lib_obj = lib_source

    else:
        raise TypeError(
            "lib_source must be a CSV/JSON file path (str), a masster.lib.Lib instance, or have a 'lib_df' attribute",
        )

    # Ensure lib_df is populated
    lf = getattr(lib_obj, "lib_df", None)
    if lf is None or (hasattr(lf, "is_empty") and lf.is_empty()):
        raise ValueError("Library has no data populated in lib_df")

    # Filter by polarity to match study
    # Map polarity to charge signs
    if polarity == "positive":
        target_charges = [1, 2]  # positive charges
    elif polarity == "negative":
        target_charges = [-1, -2]  # negative charges
    else:
        target_charges = [-2, -1, 1, 2]  # all charges

    # Filter library entries by charge sign (which corresponds to polarity)
    filtered_lf = lf.filter(pl.col("z").is_in(target_charges))

    if filtered_lf.is_empty():
        print(
            f"Warning: No library entries found for polarity '{polarity}'. Using all entries.",
        )
        filtered_lf = lf

    # Store pointer and DataFrame on study
    study._lib = lib_obj

    # Add source_id column with filename (without path) if loading from CSV/JSON
    if isinstance(lib_source, str):
        import os

        filename_only = os.path.basename(lib_source)
        filtered_lf = filtered_lf.with_columns(pl.lit(filename_only).alias("source_id"))

    # Ensure required columns exist and set correct values
    required_columns = {"quant_group": pl.Int64, "iso": pl.Int64}

    for col_name, col_dtype in required_columns.items():
        if col_name == "quant_group":
            # Set quant_group using cmpd_uid (same for isotopomers of same compound)
            if "cmpd_uid" in filtered_lf.columns:
                filtered_lf = filtered_lf.with_columns(pl.col("cmpd_uid").cast(col_dtype).alias("quant_group"))
            else:
                # Fallback to lib_uid if cmpd_uid doesn't exist
                filtered_lf = filtered_lf.with_columns(pl.col("lib_uid").cast(col_dtype).alias("quant_group"))
        elif col_name == "iso":
            if col_name not in filtered_lf.columns:
                # Default to zero for iso
                filtered_lf = filtered_lf.with_columns(pl.lit(0).cast(col_dtype).alias(col_name))

    # Generate 13C isotopes if requested
    original_count = len(filtered_lf)
    if iso == "13C":
        filtered_lf = _generate_13c_isotopes(filtered_lf)
        # Update the log message to show the correct count after isotope generation
        if isinstance(lib_source, str):
            import os

            filename_only = os.path.basename(lib_source)
            print(
                f"Generated 13C isotopes: {len(filtered_lf)} total entries ({original_count} original + {len(filtered_lf) - original_count} isotopes) from {filename_only}"
            )

    # Reorder columns to place quant_group after rt and iso after formula
    column_order = []
    columns_list = list(filtered_lf.columns)

    for col in columns_list:
        if col not in column_order:  # Only add if not already added
            column_order.append(col)
            if col == "rt" and "quant_group" in columns_list and "quant_group" not in column_order:
                column_order.append("quant_group")
            elif col == "formula" and "iso" in columns_list and "iso" not in column_order:
                column_order.append("iso")

    # Add to existing lib_df instead of replacing
    if hasattr(study, "lib_df") and study.lib_df is not None and not study.lib_df.is_empty():
        # Check for schema compatibility and handle mismatches
        existing_cols = set(study.lib_df.columns)
        new_cols = set(filtered_lf.columns)

        # If schemas don't match, we need to align them
        if existing_cols != new_cols:
            # Get union of all columns
            all_cols = existing_cols.union(new_cols)

            # Add missing columns to existing data with appropriate defaults
            for col in new_cols - existing_cols:
                if col == "probability":
                    # Add probability column to existing data - try to calculate from adduct
                    if "adduct" in study.lib_df.columns:
                        try:
                            adduct_prob_map = _get_adduct_probabilities(study)
                            study.lib_df = study.lib_df.with_columns(
                                pl.col("adduct")
                                .map_elements(
                                    lambda adduct: adduct_prob_map.get(adduct, 1.0) if adduct is not None else 1.0,
                                    return_dtype=pl.Float64,
                                )
                                .alias("probability")
                            )
                        except Exception:
                            study.lib_df = study.lib_df.with_columns(pl.lit(1.0).alias("probability"))
                    else:
                        study.lib_df = study.lib_df.with_columns(pl.lit(1.0).alias("probability"))
                elif col == "iso":
                    study.lib_df = study.lib_df.with_columns(pl.lit(0).cast(pl.Int64).alias("iso"))
                elif col == "quant_group":
                    # Set quant_group using cmpd_uid or lib_uid
                    if "cmpd_uid" in study.lib_df.columns:
                        study.lib_df = study.lib_df.with_columns(pl.col("cmpd_uid").cast(pl.Int64).alias("quant_group"))
                    else:
                        study.lib_df = study.lib_df.with_columns(pl.col("lib_uid").cast(pl.Int64).alias("quant_group"))
                else:
                    # Default to null for other columns
                    study.lib_df = study.lib_df.with_columns(pl.lit(None).alias(col))

            # Add missing columns to new data with appropriate defaults
            for col in existing_cols - new_cols:
                if col not in ["probability", "iso", "quant_group"]:  # These should already be handled
                    filtered_lf = filtered_lf.with_columns(pl.lit(None).alias(col))

        # Ensure column order matches for concatenation - use existing column order
        existing_column_order = list(study.lib_df.columns)
        filtered_lf = filtered_lf.select(existing_column_order)

        # Concatenate with existing data
        study.lib_df = pl.concat([study.lib_df, filtered_lf])
    else:
        # First time loading - create new
        try:
            study.lib_df = (
                filtered_lf.clone()
                if hasattr(filtered_lf, "clone")
                else pl.DataFrame(filtered_lf.to_dict() if hasattr(filtered_lf, "to_dict") else filtered_lf)
            )
        except Exception:
            try:
                study.lib_df = (
                    pl.from_pandas(filtered_lf)
                    if hasattr(filtered_lf, "to_pandas")
                    else pl.DataFrame(filtered_lf.to_dict() if hasattr(filtered_lf, "to_dict") else filtered_lf)
                )
            except Exception:
                study.lib_df = pl.DataFrame()

    # Store this operation in history
    if hasattr(study, "update_history"):
        study.update_history(
            ["lib_load"],
            {"lib_source": str(lib_source), "polarity": polarity, "adducts": adducts, "iso": iso},
        )


def _setup_identify_parameters(params, kwargs):
    """Setup identification parameters with fallbacks and overrides."""
    # Import defaults class
    try:
        from masster.study.defaults.identify_def import identify_defaults
    except ImportError:
        identify_defaults = None

    # Use provided params or create defaults
    if params is None:
        if identify_defaults is not None:
            params = identify_defaults()
        else:
            # Fallback if imports fail
            class FallbackParams:
                mz_tol = 0.01
                rt_tol = 2.0
                heteroatom_penalty = 0.7
                multiple_formulas_penalty = 0.8
                multiple_compounds_penalty = 0.8
                heteroatoms = ["Cl", "Br", "F", "I"]

            params = FallbackParams()

    # Override parameters with any provided kwargs
    if kwargs:
        # Handle parameter name mapping for backwards compatibility
        param_mapping = {"rt_tolerance": "rt_tol", "mz_tolerance": "mz_tol"}

        for param_name, value in kwargs.items():
            # Check if we need to map the parameter name
            mapped_name = param_mapping.get(param_name, param_name)

            if hasattr(params, mapped_name):
                setattr(params, mapped_name, value)
            elif hasattr(params, param_name):
                setattr(params, param_name, value)

    return params


def _smart_reset_id_results(study, target_uids, logger):
    """Smart reset of identification results - only clear what's being re-identified."""
    if target_uids is not None:
        # Selective reset: only clear results for features being re-identified
        if hasattr(study, "id_df") and study.id_df is not None and not study.id_df.is_empty():
            study.id_df = study.id_df.filter(~pl.col("consensus_uid").is_in(target_uids))
            if logger:
                logger.debug(f"Cleared previous results for {len(target_uids)} specific features")
        elif not hasattr(study, "id_df"):
            study.id_df = pl.DataFrame()
    else:
        # Full reset: clear all results
        study.id_df = pl.DataFrame()
        if logger:
            logger.debug("Cleared all previous identification results")


def _get_cached_adduct_probabilities(study, logger):
    """Get adduct probabilities with caching to avoid repeated expensive computation."""
    # Check if we have cached results and cache key matches current parameters
    current_cache_key = _get_adduct_cache_key(study)

    if (
        hasattr(study, "_cached_adduct_probs")
        and hasattr(study, "_cached_adduct_key")
        and study._cached_adduct_key == current_cache_key
    ):
        if logger:
            logger.debug("Using cached adduct probabilities")
        return study._cached_adduct_probs

    # Compute and cache
    if logger:
        logger.debug("Computing adduct probabilities...")
    adduct_prob_map = _get_adduct_probabilities(study)
    study._cached_adduct_probs = adduct_prob_map
    study._cached_adduct_key = current_cache_key

    if logger:
        logger.debug(f"Computed and cached probabilities for {len(adduct_prob_map)} adducts")
    return adduct_prob_map


def _get_adduct_cache_key(study):
    """Generate a cache key based on adduct-related parameters."""
    if hasattr(study, "parameters") and hasattr(study.parameters, "adducts"):
        adducts_str = "|".join(sorted(study.parameters.adducts)) if study.parameters.adducts else ""
        min_prob = getattr(study.parameters, "adduct_min_probability", 0.04)
        return f"adducts:{adducts_str}:min_prob:{min_prob}"
    return "default"


def clear_identification_cache(study):
    """Clear cached identification data (useful when parameters change)."""
    cache_attrs = ["_cached_adduct_probs", "_cached_adduct_key"]
    for attr in cache_attrs:
        if hasattr(study, attr):
            delattr(study, attr)


def _perform_identification_matching(
    consensus_to_process, study, effective_mz_tol, effective_rt_tol, adduct_prob_map, logger
):
    """Perform optimized identification matching using vectorized operations where possible."""
    results = []

    # Get library data as arrays for faster access
    lib_df = study.lib_df

    if logger:
        consensus_count = len(consensus_to_process)
        lib_count = len(lib_df)
        logger.debug(
            f"Identifying {consensus_count} consensus features against {lib_count} library entries",
        )

    # Process each consensus feature
    for cons_row in consensus_to_process.iter_rows(named=True):
        cons_uid = cons_row.get("consensus_uid")
        cons_mz = cons_row.get("mz")
        cons_rt = cons_row.get("rt")

        if cons_mz is None:
            if logger:
                logger.debug(f"Skipping consensus feature {cons_uid} - no m/z value")
            results.append({"consensus_uid": cons_uid, "matches": []})
            continue

        # Find matches using vectorized filtering
        matches = _find_matches_vectorized(
            lib_df, cons_mz, cons_rt, effective_mz_tol, effective_rt_tol, logger, cons_uid
        )

        # Convert matches to result format
        match_results = []
        if not matches.is_empty():
            for match_row in matches.iter_rows(named=True):
                mz_delta = abs(cons_mz - match_row.get("mz")) if match_row.get("mz") is not None else None
                lib_rt = match_row.get("rt")
                rt_delta = abs(cons_rt - lib_rt) if (cons_rt is not None and lib_rt is not None) else None

                # Get library probability as base score, then multiply by adduct probability
                lib_probability = match_row.get("probability", 1.0) if match_row.get("probability") is not None else 1.0
                adduct = match_row.get("adduct")
                adduct_probability = adduct_prob_map.get(adduct, 1.0) if adduct else 1.0
                score = lib_probability * adduct_probability
                # Scale to 0-100 and round to 1 decimal place
                score = round(score * 100.0, 1)

                match_results.append({
                    "lib_uid": match_row.get("lib_uid"),
                    "mz_delta": mz_delta,
                    "rt_delta": rt_delta,
                    "matcher": "ms1",
                    "score": score,
                })

        results.append({"consensus_uid": cons_uid, "matches": match_results})

    return results


def _find_matches_vectorized(lib_df, cons_mz, cons_rt, mz_tol, rt_tol, logger, cons_uid):
    """
    Find library matches using optimized vectorized operations.

    FIXED VERSION: Prevents incorrect matching of same compound to different m/z values.
    """
    # Filter by m/z tolerance using vectorized operations
    matches = lib_df.filter((pl.col("mz") >= cons_mz - mz_tol) & (pl.col("mz") <= cons_mz + mz_tol))

    initial_match_count = len(matches)

    # Apply RT filter if available - STRICT VERSION (no fallback)
    if rt_tol is not None and cons_rt is not None and not matches.is_empty():
        # First, check if any m/z matches have RT data
        rt_candidates = matches.filter(pl.col("rt").is_not_null())

        if not rt_candidates.is_empty():
            # Apply RT filtering to candidates with RT data
            rt_matches = rt_candidates.filter((pl.col("rt") >= cons_rt - rt_tol) & (pl.col("rt") <= cons_rt + rt_tol))

            if not rt_matches.is_empty():
                matches = rt_matches
                if logger:
                    logger.debug(
                        f"Consensus {cons_uid}: {initial_match_count} m/z matches, {len(rt_candidates)} with RT, {len(matches)} after RT filter"
                    )
            else:
                # NO FALLBACK - if RT filtering finds no matches, return empty
                matches = rt_matches  # This is empty
                if logger:
                    logger.debug(
                        f"Consensus {cons_uid}: RT filtering eliminated all {len(rt_candidates)} candidates (rt_tol={rt_tol}s) - no matches returned"
                    )
        else:
            # No RT data in library matches - return empty if strict RT filtering requested
            if logger:
                logger.debug(
                    f"Consensus {cons_uid}: {initial_match_count} m/z matches but none have library RT data - no matches returned due to RT filtering"
                )
            matches = pl.DataFrame()  # Return empty DataFrame

    # FIX 1: Add stricter m/z validation - prioritize more accurate matches
    if not matches.is_empty():
        strict_mz_tol = mz_tol * 0.5  # Use 50% of tolerance as strict threshold
        strict_matches = matches.filter(
            (pl.col("mz") >= cons_mz - strict_mz_tol) & (pl.col("mz") <= cons_mz + strict_mz_tol)
        )

        if not strict_matches.is_empty():
            # Use strict matches if available
            matches = strict_matches
            if logger:
                logger.debug(
                    f"Consensus {cons_uid}: Using {len(matches)} strict m/z matches (within {strict_mz_tol:.6f} Da)"
                )
        else:
            if logger:
                logger.debug(f"Consensus {cons_uid}: No strict matches, using {len(matches)} loose matches")

    # FIX 2: Improved deduplication - prioritize by m/z accuracy
    if not matches.is_empty() and len(matches) > 1:
        if "formula" in matches.columns and "adduct" in matches.columns:
            pre_dedup_count = len(matches)

            # Calculate m/z error for sorting
            matches = matches.with_columns([(pl.col("mz") - cons_mz).abs().alias("mz_error_abs")])

            # Group by formula and adduct, but keep the most accurate m/z match
            matches = (
                matches.sort(["mz_error_abs", "lib_uid"])  # Sort by m/z accuracy first, then lib_uid for consistency
                .group_by(["formula", "adduct"], maintain_order=True)
                .first()
                .drop("mz_error_abs")  # Remove the temporary column
            )

            post_dedup_count = len(matches)
            if logger and post_dedup_count < pre_dedup_count:
                logger.debug(
                    f"Consensus {cons_uid}: deduplicated {pre_dedup_count} to {post_dedup_count} matches (m/z accuracy prioritized)"
                )

    return matches


def _update_identification_results(study, results, logger):
    """Update study.id_df with new identification results."""
    # Flatten results into records
    records = []
    for result in results:
        consensus_uid = result["consensus_uid"]
        for match in result["matches"]:
            records.append({
                "consensus_uid": consensus_uid,
                "lib_uid": match["lib_uid"],
                "mz_delta": match["mz_delta"],
                "rt_delta": match["rt_delta"],
                "matcher": match["matcher"],
                "score": match["score"],
                "iso": 0,  # Default to zero
            })

    # Convert to DataFrame and append to existing results
    new_results_df = pl.DataFrame(records) if records else pl.DataFrame()

    if not new_results_df.is_empty():
        if hasattr(study, "id_df") and study.id_df is not None and not study.id_df.is_empty():
            # Check if existing id_df has the iso column
            if "iso" not in study.id_df.columns:
                # Add iso column to existing id_df with default value 0
                study.id_df = study.id_df.with_columns(pl.lit(0).alias("iso"))
                if logger:
                    logger.debug("Added 'iso' column to existing id_df for schema compatibility")

            study.id_df = pl.concat([study.id_df, new_results_df])
        else:
            study.id_df = new_results_df

        if logger:
            logger.debug(f"Added {len(records)} identification results to study.id_df")
    elif not hasattr(study, "id_df"):
        study.id_df = pl.DataFrame()


def _finalize_identification_results(study, params, logger):
    """Apply final scoring adjustments and update consensus columns."""
    # Apply scoring adjustments based on compound and formula counts
    _apply_scoring_adjustments(study, params)

    # Update consensus_df with top-scoring identification results
    _update_consensus_id_columns(study, logger)


def _store_identification_history(study, effective_mz_tol, effective_rt_tol, target_uids, params, kwargs):
    """Store identification operation in study history."""
    if hasattr(study, "store_history"):
        history_params = {"mz_tol": effective_mz_tol, "rt_tol": effective_rt_tol}
        if target_uids is not None:
            history_params["features"] = target_uids
        if params is not None and hasattr(params, "to_dict"):
            history_params["params"] = params.to_dict()
        if kwargs:
            history_params["kwargs"] = kwargs
        study.update_history(["identify"], history_params)


def _validate_identify_inputs(study, logger=None):
    """Validate inputs for identification process."""
    if getattr(study, "consensus_df", None) is None or study.consensus_df.is_empty():
        if logger:
            logger.warning("No consensus features found for identification")
        return False

    if getattr(study, "lib_df", None) is None or study.lib_df.is_empty():
        if logger:
            logger.error("Library (study.lib_df) is empty; call lib_load() first")
        raise ValueError("Library (study.lib_df) is empty; call lib_load() first")

    return True


def _prepare_consensus_features(study, features, logger=None):
    """Prepare consensus features for identification."""
    target_uids = None
    if features is not None:
        if hasattr(features, "columns"):  # DataFrame-like
            if "consensus_uid" in features.columns:
                target_uids = features["consensus_uid"].unique().to_list()
            else:
                raise ValueError(
                    "features DataFrame must contain 'consensus_uid' column",
                )
        elif hasattr(features, "__iter__") and not isinstance(
            features,
            str,
        ):  # List-like
            target_uids = list(features)
        else:
            raise ValueError(
                "features must be a DataFrame with 'consensus_uid' column or a list of UIDs",
            )

        if logger:
            logger.debug(f"Identifying {len(target_uids)} specified features")

    # Filter consensus features if target_uids specified
    consensus_to_process = study.consensus_df
    if target_uids is not None:
        consensus_to_process = study.consensus_df.filter(
            pl.col("consensus_uid").is_in(target_uids),
        )
        if consensus_to_process.is_empty():
            if logger:
                logger.warning(
                    "No consensus features found matching specified features",
                )
            return None, target_uids

    return consensus_to_process, target_uids


def _get_adduct_probabilities(study):
    """Get adduct probabilities from _get_adducts() results."""
    adducts_df = _get_adducts(study)
    adduct_prob_map = {}
    if not adducts_df.is_empty():
        for row in adducts_df.iter_rows(named=True):
            adduct_prob_map[row.get("name")] = row.get("probability", 1.0)
    return adduct_prob_map


def _create_identification_results(
    consensus_to_process, study, effective_mz_tol, effective_rt_tol, adduct_prob_map, logger=None
):
    """Create identification results by matching consensus features against library (DEPRECATED - use optimized version)."""
    # This function is now deprecated in favor of _perform_identification_matching
    # Keep for backward compatibility but redirect to optimized version
    results = _perform_identification_matching(
        consensus_to_process, study, effective_mz_tol, effective_rt_tol, adduct_prob_map, logger
    )

    # Convert to legacy format for compatibility
    legacy_results = []
    features_with_matches = 0
    total_matches = 0

    for result in results:
        if result["matches"]:
            features_with_matches += 1
            total_matches += len(result["matches"])

            for match in result["matches"]:
                legacy_results.append({
                    "consensus_uid": result["consensus_uid"],
                    "lib_uid": match["lib_uid"],
                    "mz_delta": match["mz_delta"],
                    "rt_delta": match["rt_delta"],
                    "matcher": match["matcher"],
                    "score": match["score"],
                })

    return legacy_results, features_with_matches, total_matches


def _apply_scoring_adjustments(study, params):
    """Apply scoring adjustments based on compound and formula counts using optimized operations."""
    if not study.id_df.is_empty() and hasattr(study, "lib_df") and not study.lib_df.is_empty():
        # Get penalty parameters
        heteroatoms = getattr(params, "heteroatoms", ["Cl", "Br", "F", "I"])
        heteroatom_penalty = getattr(params, "heteroatom_penalty", 0.7)
        formulas_penalty = getattr(params, "multiple_formulas_penalty", 0.8)
        compounds_penalty = getattr(params, "multiple_compounds_penalty", 0.8)

        # Single join to get all needed library information
        lib_columns = ["lib_uid", "cmpd_uid", "formula"]
        id_with_lib = study.id_df.join(
            study.lib_df.select(lib_columns),
            on="lib_uid",
            how="left",
        )

        # Calculate all statistics in one group_by operation
        stats = id_with_lib.group_by("consensus_uid").agg([
            pl.col("cmpd_uid").n_unique().alias("num_cmpds"),
            pl.col("formula").filter(pl.col("formula").is_not_null()).n_unique().alias("num_formulas"),
        ])

        # Join stats back and apply all penalties in one with_columns operation
        heteroatom_conditions = [pl.col("formula").str.contains(atom) for atom in heteroatoms]
        has_heteroatoms = (
            pl.fold(acc=pl.lit(False), function=lambda acc, x: acc | x, exprs=heteroatom_conditions)
            if heteroatom_conditions
            else pl.lit(False)
        )

        study.id_df = (
            id_with_lib.join(stats, on="consensus_uid", how="left")
            .with_columns([
                # Apply all penalties in sequence using case-when chains
                pl.when(pl.col("formula").is_not_null() & has_heteroatoms)
                .then(pl.col("score") * heteroatom_penalty)
                .otherwise(pl.col("score"))
                .alias("score_temp1")
            ])
            .with_columns([
                pl.when(pl.col("num_formulas") > 1)
                .then(pl.col("score_temp1") * formulas_penalty)
                .otherwise(pl.col("score_temp1"))
                .alias("score_temp2")
            ])
            .with_columns([
                pl.when(pl.col("num_cmpds") > 1)
                .then(pl.col("score_temp2") * compounds_penalty)
                .otherwise(pl.col("score_temp2"))
                .round(4)
                .alias("score")
            ])
            .select([
                "consensus_uid",
                "lib_uid",
                "mz_delta",
                "rt_delta",
                "matcher",
                "score",
            ])
        )


def _update_consensus_id_columns(study, logger=None):
    """
    Update consensus_df with top-scoring identification results using safe in-place updates.

    FIXED VERSION: Prevents same compound from being assigned to vastly different m/z values.
    """
    try:
        if not hasattr(study, "id_df") or study.id_df is None or study.id_df.is_empty():
            if logger:
                logger.debug("No identification results to process")
            return

        if not hasattr(study, "lib_df") or study.lib_df is None or study.lib_df.is_empty():
            if logger:
                logger.debug("No library data available")
            return

        if not hasattr(study, "consensus_df") or study.consensus_df is None or study.consensus_df.is_empty():
            if logger:
                logger.debug("No consensus data available")
            return

        # Get library columns we need (include mz for validation)
        lib_columns = ["lib_uid", "name", "adduct", "mz"]
        if "class" in study.lib_df.columns:
            lib_columns.append("class")

        # FIX 1: Join identification results with consensus m/z for validation
        id_with_consensus = study.id_df.join(
            study.consensus_df.select(["consensus_uid", "mz"]), on="consensus_uid", how="left", suffix="_consensus"
        )

        # FIX 2: Validate m/z accuracy - filter out poor matches
        id_with_lib = id_with_consensus.join(
            study.lib_df.select(["lib_uid", "mz"]), on="lib_uid", how="left", suffix="_lib"
        )

        # Calculate actual m/z error and filter out excessive errors
        id_validated = id_with_lib.with_columns([(pl.col("mz") - pl.col("mz_lib")).abs().alias("actual_mz_error")])

        # Filter out matches with excessive m/z error
        max_reasonable_error = 0.02  # 20 millidalton maximum error
        id_validated = id_validated.filter(
            (pl.col("actual_mz_error") <= max_reasonable_error) | pl.col("actual_mz_error").is_null()
        )

        if logger:
            original_count = len(id_with_consensus)
            validated_count = len(id_validated)
            if validated_count < original_count:
                logger.warning(
                    f"Filtered out {original_count - validated_count} identifications with excessive m/z error (>{max_reasonable_error:.3f} Da)"
                )

        # Get top-scoring identification for each consensus feature (from validated results)
        top_ids = (
            id_validated.sort(["consensus_uid", "score"], descending=[False, True])
            .group_by("consensus_uid", maintain_order=True)
            .first()
            .join(study.lib_df.select(lib_columns), on="lib_uid", how="left")
            .select([
                "consensus_uid",
                "name",
                pl.col("class").alias("id_top_class")
                if "class" in lib_columns
                else pl.lit(None, dtype=pl.String).alias("id_top_class"),
                pl.col("adduct").alias("id_top_adduct"),
                pl.col("score").alias("id_top_score"),
            ])
            .rename({"name": "id_top_name"})
        )

        # FIX 3: Check for conflicts where same compound+adduct assigned to very different m/z
        if not top_ids.is_empty():
            compound_groups = (
                top_ids.join(study.consensus_df.select(["consensus_uid", "mz"]), on="consensus_uid", how="left")
                .group_by(["id_top_name", "id_top_adduct"])
                .agg([
                    pl.col("consensus_uid").count().alias("count"),
                    pl.col("mz").min().alias("mz_min"),
                    pl.col("mz").max().alias("mz_max"),
                ])
                .with_columns([(pl.col("mz_max") - pl.col("mz_min")).alias("mz_range")])
            )

            # Find problematic assignments (same compound+adduct with >0.1 Da m/z range)
            problematic = compound_groups.filter((pl.col("count") > 1) & (pl.col("mz_range") > 0.1))

            if not problematic.is_empty() and logger:
                for row in problematic.iter_rows(named=True):
                    name = row["id_top_name"]
                    adduct = row["id_top_adduct"]
                    count = row["count"]
                    mz_range = row["mz_range"]
                    logger.warning(
                        f"Identification conflict detected: '{name}' ({adduct}) assigned to {count} features with {mz_range:.4f} Da m/z range"
                    )

        # Ensure we have the id_top columns in consensus_df
        for col_name, dtype in [
            ("id_top_name", pl.String),
            ("id_top_class", pl.String),
            ("id_top_adduct", pl.String),
            ("id_top_score", pl.Float64),
            ("id_source", pl.String),
        ]:
            if col_name not in study.consensus_df.columns:
                study.consensus_df = study.consensus_df.with_columns(pl.lit(None, dtype=dtype).alias(col_name))

        # Create a mapping dictionary for efficient updates
        id_mapping = {}
        for row in top_ids.iter_rows(named=True):
            consensus_uid = row["consensus_uid"]
            id_mapping[consensus_uid] = {
                "id_top_name": row["id_top_name"],
                "id_top_class": row["id_top_class"],
                "id_top_adduct": row["id_top_adduct"],
                "id_top_score": row["id_top_score"],
            }

        # Update consensus_df using map_elements (safer than join for avoiding duplicates)
        if id_mapping:
            study.consensus_df = study.consensus_df.with_columns([
                pl.col("consensus_uid")
                .map_elements(lambda uid: id_mapping.get(uid, {}).get("id_top_name"), return_dtype=pl.String)
                .alias("id_top_name"),
                pl.col("consensus_uid")
                .map_elements(lambda uid: id_mapping.get(uid, {}).get("id_top_class"), return_dtype=pl.String)
                .alias("id_top_class"),
                pl.col("consensus_uid")
                .map_elements(lambda uid: id_mapping.get(uid, {}).get("id_top_adduct"), return_dtype=pl.String)
                .alias("id_top_adduct"),
                pl.col("consensus_uid")
                .map_elements(lambda uid: id_mapping.get(uid, {}).get("id_top_score"), return_dtype=pl.Float64)
                .alias("id_top_score"),
            ])

        if logger:
            num_updated = len(id_mapping)
            logger.debug(f"Updated consensus_df with top identifications for {num_updated} features")

    except Exception as e:
        if logger:
            logger.error(f"Error updating consensus_df with identification results: {e}")
        # Don't re-raise to avoid breaking the identification process


def identify(study, features=None, params=None, **kwargs):
    """Identify consensus features against the loaded library.

    Matches consensus_df.mz against lib_df.mz within mz_tolerance. If rt_tolerance
    is provided and both consensus and library entries have rt values, RT is
    used as an additional filter.

    Args:
        study: Study instance
        features: Optional DataFrame or list of consensus_uids to identify.
                 If None, identifies all consensus features.
        params: Optional identify_defaults instance with matching tolerances and scoring parameters.
                If None, uses default parameters.
        **kwargs: Individual parameter overrides (mz_tol, rt_tol, heteroatom_penalty,
                 multiple_formulas_penalty, multiple_compounds_penalty, heteroatoms)

    The resulting DataFrame is stored as study.id_df. Columns:
        - consensus_uid
        - lib_uid
        - mz_delta
        - rt_delta (nullable)
        - score (adduct probability from _get_adducts with penalties applied)
    """
    # Get logger from study if available
    logger = getattr(study, "logger", None)

    # Setup parameters early
    params = _setup_identify_parameters(params, kwargs)
    effective_mz_tol = getattr(params, "mz_tol", 0.01)
    effective_rt_tol = getattr(params, "rt_tol", 2.0)

    if logger:
        logger.debug(
            f"Starting identification with mz_tolerance={effective_mz_tol}, rt_tolerance={effective_rt_tol}",
        )

    # Validate inputs early
    if not _validate_identify_inputs(study, logger):
        return

    # Prepare consensus features and determine target UIDs early
    consensus_to_process, target_uids = _prepare_consensus_features(study, features, logger)
    if consensus_to_process is None:
        return

    # Smart reset of id_df: only clear results for features being re-identified
    _smart_reset_id_results(study, target_uids, logger)

    # Cache adduct probabilities (expensive operation)
    adduct_prob_map = _get_cached_adduct_probabilities(study, logger)

    # Perform identification with optimized matching
    results = _perform_identification_matching(
        consensus_to_process, study, effective_mz_tol, effective_rt_tol, adduct_prob_map, logger
    )

    # Update or append results to study.id_df
    _update_identification_results(study, results, logger)

    # Apply scoring adjustments and update consensus columns
    _finalize_identification_results(study, params, logger)

    # Store operation in history
    _store_identification_history(study, effective_mz_tol, effective_rt_tol, target_uids, params, kwargs)

    # Log final statistics
    consensus_count = len(consensus_to_process)
    if logger:
        features_with_matches = len([r for r in results if len(r["matches"]) > 0])
        total_matches = sum(len(r["matches"]) for r in results)
        logger.success(
            f"Identification completed: {features_with_matches}/{consensus_count} features matched, {total_matches} total identifications",
        )


def get_id(study, features=None) -> pl.DataFrame:
    """Get identification results with comprehensive annotation data.

    Combines identification results (study.id_df) with library information to provide
    comprehensive identification data including names, adducts, formulas, etc.

    Args:
        study: Study instance with id_df and lib_df populated
        features: Optional DataFrame or list of consensus_uids to filter results.
                 If None, returns all identification results.

    Returns:
        Polars DataFrame with columns:
        - consensus_uid
        - lib_uid
        - mz (consensus feature m/z)
        - rt (consensus feature RT)
        - name (compound name from library)
        - shortname (short name from library, if available)
        - class (compound class from library, if available)
        - formula (molecular formula from library)
        - adduct (adduct type from library)
        - smiles (SMILES notation from library)
        - mz_delta (absolute m/z difference)
        - rt_delta (absolute RT difference, nullable)
        - Additional library columns if available (inchi, inchikey, etc.)

    Raises:
        ValueError: If study.id_df or study.lib_df are empty
    """
    # Validate inputs
    if getattr(study, "id_df", None) is None or study.id_df.is_empty():
        raise ValueError(
            "Identification results (study.id_df) are empty; call identify() first",
        )

    if getattr(study, "lib_df", None) is None or study.lib_df.is_empty():
        raise ValueError("Library (study.lib_df) is empty; call lib_load() first")

    if getattr(study, "consensus_df", None) is None or study.consensus_df.is_empty():
        raise ValueError("Consensus features (study.consensus_df) are empty")

    # Start with identification results
    result_df = study.id_df.clone()

    # Filter by features if provided
    if features is not None:
        if hasattr(features, "columns"):  # DataFrame-like
            if "consensus_uid" in features.columns:
                uids = features["consensus_uid"].unique().to_list()
            else:
                raise ValueError(
                    "features DataFrame must contain 'consensus_uid' column",
                )
        elif hasattr(features, "__iter__") and not isinstance(
            features,
            str,
        ):  # List-like
            uids = list(features)
        else:
            raise ValueError(
                "features must be a DataFrame with 'consensus_uid' column or a list of UIDs",
            )

        result_df = result_df.filter(pl.col("consensus_uid").is_in(uids))

        if result_df.is_empty():
            return pl.DataFrame()

    # Join with consensus_df to get consensus feature m/z and RT
    consensus_cols = ["consensus_uid", "mz", "rt"]
    # Only select columns that exist in consensus_df
    available_consensus_cols = [col for col in consensus_cols if col in study.consensus_df.columns]

    result_df = result_df.join(
        study.consensus_df.select(available_consensus_cols),
        on="consensus_uid",
        how="left",
        suffix="_consensus",
    )

    # Join with lib_df to get library information
    lib_cols = [
        "lib_uid",
        "name",
        "shortname",
        "class",
        "formula",
        "adduct",
        "smiles",
        "cmpd_uid",
        "inchikey",
    ]
    # Add optional columns if they exist
    optional_lib_cols = ["inchi", "db_id", "db"]
    for col in optional_lib_cols:
        if col in study.lib_df.columns:
            lib_cols.append(col)

    # Only select columns that exist in lib_df
    available_lib_cols = [col for col in lib_cols if col in study.lib_df.columns]

    result_df = result_df.join(
        study.lib_df.select(available_lib_cols),
        on="lib_uid",
        how="left",
        suffix="_lib",
    )

    # Reorder columns for better readability
    column_order = [
        "consensus_uid",
        "cmpd_uid" if "cmpd_uid" in result_df.columns else None,
        "lib_uid",
        "name" if "name" in result_df.columns else None,
        "shortname" if "shortname" in result_df.columns else None,
        "class" if "class" in result_df.columns else None,
        "formula" if "formula" in result_df.columns else None,
        "adduct" if "adduct" in result_df.columns else None,
        "mz" if "mz" in result_df.columns else None,
        "mz_delta",
        "rt" if "rt" in result_df.columns else None,
        "rt_delta",
        "matcher" if "matcher" in result_df.columns else None,
        "score" if "score" in result_df.columns else None,
        "smiles" if "smiles" in result_df.columns else None,
        "inchikey" if "inchikey" in result_df.columns else None,
    ]

    # Add any remaining columns
    remaining_cols = [col for col in result_df.columns if col not in column_order]
    column_order.extend(remaining_cols)

    # Filter out None values and select existing columns
    final_column_order = [col for col in column_order if col is not None and col in result_df.columns]

    result_df = result_df.select(final_column_order)

    # Add compound and formula count columns
    if "consensus_uid" in result_df.columns:
        # Calculate counts per consensus_uid
        count_stats = result_df.group_by("consensus_uid").agg(
            [
                pl.col("cmpd_uid").n_unique().alias("num_cmpds")
                if "cmpd_uid" in result_df.columns
                else pl.lit(None).alias("num_cmpds"),
                pl.col("formula").filter(pl.col("formula").is_not_null()).n_unique().alias("num_formulas")
                if "formula" in result_df.columns
                else pl.lit(None).alias("num_formulas"),
            ],
        )

        # Join the counts back to the main dataframe
        result_df = result_df.join(count_stats, on="consensus_uid", how="left")

        # Reorder columns to put count columns in the right position
        final_columns = []
        for col in result_df.columns:
            if col in [
                "consensus_uid",
                "cmpd_uid",
                "lib_uid",
                "name",
                "shortname",
                "class",
                "formula",
                "adduct",
                "mz",
                "mz_delta",
                "rt",
                "rt_delta",
                "matcher",
                "score",
            ]:
                final_columns.append(col)
        # Add count columns
        if "num_cmpds" in result_df.columns:
            final_columns.append("num_cmpds")
        if "num_formulas" in result_df.columns:
            final_columns.append("num_formulas")
        # Add remaining columns
        for col in result_df.columns:
            if col not in final_columns:
                final_columns.append(col)

        result_df = result_df.select(final_columns)

        # Apply filtering logic (scores are already final from identify())
        if "consensus_uid" in result_df.columns and len(result_df) > 0:
            # (v) Rank by score, assume that highest score has the correct rt
            # (vi) Remove all lower-scoring ids with a different rt (group by cmpd_uid)
            # (vii) Remove multiply charged ids if not in line with [M+H]+ or [M-H]- (group by cmpd_uid)

            # Group by cmpd_uid and apply filtering logic
            if "cmpd_uid" in result_df.columns:
                filtered_dfs = []
                for cmpd_uid, group_df in result_df.group_by("cmpd_uid"):
                    # Sort by score descending to get highest score first
                    group_df = group_df.sort("score", descending=True)

                    if len(group_df) == 0:
                        continue

                    # Get the highest scoring entry's RT as reference
                    reference_rt = (
                        group_df["rt"][0] if "rt" in group_df.columns and group_df["rt"][0] is not None else None
                    )

                    # Filter entries: keep those with same RT as highest scoring entry
                    if reference_rt is not None and "rt" in group_df.columns:
                        # Keep entries with the same RT or null RT
                        rt_filtered = group_df.filter(
                            (pl.col("rt") == reference_rt) | pl.col("rt").is_null(),
                        )
                    else:
                        # No reference RT, keep all
                        rt_filtered = group_df

                    # Check multiply charged constraint
                    if "z" in rt_filtered.columns and "adduct" in rt_filtered.columns and len(rt_filtered) > 0:
                        # Check if there are multiply charged adducts
                        multiply_charged = rt_filtered.filter(
                            (pl.col("z") > 1) | (pl.col("z") < -1),
                        )
                        singly_charged = rt_filtered.filter(
                            (pl.col("z") == 1) | (pl.col("z") == -1),
                        )

                        if not multiply_charged.is_empty():
                            # Check if [M+H]+ or [M-H]- are present
                            reference_adducts = ["[M+H]+", "[M-H]-"]
                            has_reference = any(
                                singly_charged.filter(
                                    pl.col("adduct").is_in(reference_adducts),
                                ).height
                                > 0,
                            )

                            if not has_reference:
                                # Remove multiply charged adducts
                                rt_filtered = singly_charged

                    if len(rt_filtered) > 0:
                        filtered_dfs.append(rt_filtered)

                if filtered_dfs:
                    result_df = pl.concat(filtered_dfs)
                else:
                    result_df = pl.DataFrame()

    # Sort by cmpd_uid if available
    if "cmpd_uid" in result_df.columns:
        result_df = result_df.sort("cmpd_uid")

    return result_df


def id_reset(study):
    """Reset identification data and remove from history.

    Removes:
    - study.id_df (identification results DataFrame)
    - 'identify' from study.history
    - Resets id_top_* columns in consensus_df to null

    Args:
        study: Study instance to reset
    """
    # Get logger from study if available
    logger = getattr(study, "logger", None)

    # Remove id_df
    if hasattr(study, "id_df"):
        if logger:
            logger.debug("Removing id_df")
        delattr(study, "id_df")

    # Reset id_top_* columns in consensus_df
    if hasattr(study, "consensus_df") and not study.consensus_df.is_empty():
        if logger:
            logger.debug("Resetting id_top_* columns in consensus_df")

        # Check which columns exist before trying to update them
        id_columns_to_reset = []
        for col in ["id_top_name", "id_top_class", "id_top_adduct", "id_top_score", "id_source"]:
            if col in study.consensus_df.columns:
                if col == "id_top_score":
                    id_columns_to_reset.append(pl.lit(None, dtype=pl.Float64).alias(col))
                else:
                    id_columns_to_reset.append(pl.lit(None, dtype=pl.String).alias(col))

        if id_columns_to_reset:
            study.consensus_df = study.consensus_df.with_columns(id_columns_to_reset)

    # Remove identify from history
    if hasattr(study, "history") and "identify" in study.history:
        if logger:
            logger.debug("Removing 'identify' from history")
        del study.history["identify"]

    if logger:
        logger.info("Identification data reset completed")


def lib_reset(study):
    """Reset library and identification data and remove from history.

    Removes:
    - study.id_df (identification results DataFrame)
    - study.lib_df (library DataFrame)
    - study._lib (library object reference)
    - Consensus features created by lib_to_consensus() (number_samples = -1 or 0)
    - 'identify' from study.history
    - 'lib_load' from study.history (if exists)
    - 'lib_to_consensus' from study.history (if exists)
    - Resets id_top_* columns in consensus_df to null

    Args:
        study: Study instance to reset
    """
    # Get logger from study if available
    logger = getattr(study, "logger", None)

    # Remove consensus features created by lib_to_consensus()
    # These are identified by number_samples = -1 or 0
    if hasattr(study, "consensus_df") and not study.consensus_df.is_empty():
        if logger:
            logger.debug("Checking for consensus features created by lib_to_consensus()")

        try:
            # Filter for features created by lib_to_consensus()
            # These can be identified by:
            # 1. number_samples < 1 (set to 0.0 by lib_to_consensus)
            # 2. AND have corresponding entries in consensus_mapping_df with sample_uid = 0 (virtual sample)

            # First check if we have any features with number_samples < 1
            potential_lib_features = study.consensus_df.filter(pl.col("number_samples") < 1)

            if potential_lib_features is not None and not potential_lib_features.is_empty():
                # Further filter by checking if they have sample_uid = 0 in consensus_mapping_df
                # This ensures we only remove library-derived features, not legitimate features with 0 samples
                if hasattr(study, "consensus_mapping_df") and not study.consensus_mapping_df.is_empty():
                    lib_consensus_uids = (
                        study.consensus_mapping_df.filter(pl.col("sample_uid") == 0)["consensus_uid"].unique().to_list()
                    )

                    if lib_consensus_uids:
                        lib_consensus_features = potential_lib_features.filter(
                            pl.col("consensus_uid").is_in(lib_consensus_uids)
                        )
                    else:
                        lib_consensus_features = pl.DataFrame()  # No library features found
                else:
                    # If no consensus_mapping_df, fall back to number_samples < 1 only
                    lib_consensus_features = potential_lib_features
            else:
                lib_consensus_features = pl.DataFrame()  # No features with number_samples < 1

            if lib_consensus_features is not None and not lib_consensus_features.is_empty():
                num_lib_features = len(lib_consensus_features)
                if logger:
                    logger.info(f"Removing {num_lib_features} consensus features created by lib_to_consensus()")

                # Use consensus_delete to remove these features and all dependent data
                study.consensus_delete(lib_consensus_features)

                if logger:
                    logger.debug("Successfully removed library-derived consensus features")
            else:
                if logger:
                    logger.debug("No library-derived consensus features found to remove")
        except Exception as e:
            if logger:
                logger.warning(f"Error removing library-derived consensus features: {e}")

    # Remove id_df
    if hasattr(study, "id_df"):
        if logger:
            logger.debug("Removing id_df")
        delattr(study, "id_df")

    # Remove lib_df
    if hasattr(study, "lib_df"):
        if logger:
            logger.debug("Removing lib_df")
        delattr(study, "lib_df")

    # Remove lib object reference
    if hasattr(study, "_lib"):
        if logger:
            logger.debug("Removing _lib reference")
        delattr(study, "_lib")

    # Reset id_top_* columns in consensus_df
    if hasattr(study, "consensus_df") and not study.consensus_df.is_empty():
        if logger:
            logger.debug("Resetting id_top_* columns in consensus_df")

        # Check which columns exist before trying to update them
        id_columns_to_reset = []
        for col in ["id_top_name", "id_top_class", "id_top_adduct", "id_top_score", "id_source"]:
            if col in study.consensus_df.columns:
                if col == "id_top_score":
                    id_columns_to_reset.append(pl.lit(None, dtype=pl.Float64).alias(col))
                else:
                    id_columns_to_reset.append(pl.lit(None, dtype=pl.String).alias(col))

        if id_columns_to_reset:
            study.consensus_df = study.consensus_df.with_columns(id_columns_to_reset)

    # Remove from history
    if hasattr(study, "history"):
        if "identify" in study.history:
            if logger:
                logger.debug("Removing 'identify' from history")
            del study.history["identify"]

        if "lib_load" in study.history:
            if logger:
                logger.debug("Removing 'lib_load' from history")
            del study.history["lib_load"]

        if "lib_to_consensus" in study.history:
            if logger:
                logger.debug("Removing 'lib_to_consensus' from history")
            del study.history["lib_to_consensus"]

    if logger:
        logger.info("Library and identification data reset completed")


def _get_adducts(study, adducts_list: list | None = None, **kwargs):
    """
    Generate comprehensive adduct specifications for study-level adduct filtering.

    This method creates a DataFrame of adduct combinations that will be used to filter
    and score adducts at the study level. Similar to sample._get_adducts() but uses
    study-level parameters and constraints.

    Parameters
    ----------
    adducts_list : List[str], optional
        List of base adduct specifications in format "+H:1:0.6" or "-H:-1:0.8"
        If None, uses self.parameters.adducts
    **kwargs : dict
        Override parameters, including:
        - charge_min: Minimum charge to consider (default 1)
        - charge_max: Maximum charge to consider (default 3)
        - max_combinations: Maximum number of adduct components to combine (default 3)
        - min_probability: Minimum probability threshold (default from study parameters)

    Returns
    -------
    pl.DataFrame
        DataFrame with columns:
        - name: Formatted adduct name like "[M+H]1+" or "[M+2H]2+"
        - charge: Total charge of the adduct
        - mass_shift: Total mass shift in Da
        - probability: Combined probability score
        - complexity: Number of adduct components (1-3)
    """
    # Import required modules

    # Use provided adducts list or get from study parameters
    adducts_list_to_use = adducts_list
    if adducts_list_to_use is None:
        adducts_list_to_use = (
            study.parameters.adducts if hasattr(study.parameters, "adducts") and study.parameters.adducts else []
        )

    # Get parameters with study-specific defaults
    charge_min = kwargs.get("charge_min", -3)  # Allow negative charges
    charge_max = kwargs.get("charge_max", 3)  # Study uses up to charge ±3
    max_combinations = kwargs.get("max_combinations", 3)  # Up to 3 combinations
    min_probability = kwargs.get(
        "min_probability",
        getattr(study.parameters, "adduct_min_probability", 0.04),
    )

    # Parse base adduct specifications
    base_specs = []

    for adduct_str in adducts_list_to_use:
        if not isinstance(adduct_str, str) or ":" not in adduct_str:
            continue

        try:
            parts = adduct_str.split(":")
            if len(parts) != 3:
                continue

            formula_part = parts[0]
            charge = int(parts[1])
            probability = float(parts[2])

            # Calculate mass shift from formula
            mass_shift = _calculate_formula_mass_shift(study, formula_part)

            base_specs.append(
                {
                    "formula": formula_part,
                    "charge": charge,
                    "mass_shift": mass_shift,
                    "probability": probability,
                    "raw_string": adduct_str,
                },
            )

        except (ValueError, IndexError):
            continue

    if not base_specs:
        # Return empty DataFrame with correct schema
        return pl.DataFrame(
            {
                "name": [],
                "charge": [],
                "mass_shift": [],
                "probability": [],
                "complexity": [],
            },
        )

    # Generate all valid combinations
    combinations_list = []

    # Separate specs by charge type
    positive_specs = [spec for spec in base_specs if spec["charge"] > 0]
    negative_specs = [spec for spec in base_specs if spec["charge"] < 0]
    neutral_specs = [spec for spec in base_specs if spec["charge"] == 0]

    # 1. Single adducts (filter out neutral adducts with charge == 0)
    for spec in base_specs:
        # Study-level filtering: exclude neutral adducts (charge=0) but use abs() for charged adducts
        if spec["charge"] != 0 and charge_min <= abs(spec["charge"]) <= charge_max:
            formatted_name = _format_adduct_name([spec])
            combinations_list.append(
                {
                    "components": [spec],
                    "formatted_name": formatted_name,
                    "total_mass_shift": spec["mass_shift"],
                    "total_charge": spec["charge"],
                    "combined_probability": spec["probability"],
                    "complexity": 1,
                },
            )

    # 2. Generate multiply charged versions (2H+, 3H+, etc.) - already excludes charge==0
    for spec in positive_specs + negative_specs:
        base_charge = spec["charge"]
        for multiplier in range(2, min(max_combinations + 1, 4)):  # Up to 3x multiplier
            total_charge = base_charge * multiplier
            if charge_min <= abs(total_charge) <= charge_max and total_charge != 0:
                components = [spec] * multiplier
                formatted_name = _format_adduct_name(components)
                probability_multiplied = float(spec["probability"]) ** multiplier

                combinations_list.append(
                    {
                        "components": components,
                        "formatted_name": formatted_name,
                        "total_mass_shift": float(spec["mass_shift"]) * multiplier,
                        "total_charge": total_charge,
                        "combined_probability": probability_multiplied,
                        "complexity": multiplier,
                    },
                )

    # 3. Mixed combinations (2-component) - limited for study level, filter out charge==0
    if max_combinations >= 2:
        # Positive + Neutral (1 neutral loss only) - but exclude if total charge == 0
        for pos_spec in positive_specs[:2]:  # Limit to first 2 positive specs
            for neut_spec in neutral_specs[:1]:  # Only 1 neutral loss
                total_charge = pos_spec["charge"] + neut_spec["charge"]
                if charge_min <= abs(total_charge) <= charge_max and total_charge != 0:
                    components = [pos_spec, neut_spec]
                    formatted_name = _format_adduct_name(components)
                    combinations_list.append(
                        {
                            "components": components,
                            "formatted_name": formatted_name,
                            "total_mass_shift": float(pos_spec["mass_shift"]) + float(neut_spec["mass_shift"]),
                            "total_charge": total_charge,
                            "combined_probability": float(pos_spec["probability"]) * float(neut_spec["probability"]),
                            "complexity": 2,
                        },
                    )

    # Convert to polars DataFrame
    if combinations_list:
        combinations_list.sort(
            key=lambda x: (-x["combined_probability"], x["complexity"]),
        )

        adducts_df = pl.DataFrame(
            [
                {
                    "name": combo["formatted_name"],
                    "charge": combo["total_charge"],
                    "mass_shift": combo["total_mass_shift"],
                    "probability": combo["combined_probability"],
                    "complexity": combo["complexity"],
                }
                for combo in combinations_list
            ],
        )

        # Filter by minimum probability threshold
        if min_probability > 0.0:
            adducts_before_filter = len(adducts_df)
            adducts_df = adducts_df.filter(pl.col("probability") >= min_probability)
            adducts_after_filter = len(adducts_df)

            logger = getattr(study, "logger", None)
            if logger:
                logger.trace(
                    f"Study adducts: generated {adducts_before_filter}, filtered to {adducts_after_filter} (min_prob={min_probability})",
                )

    else:
        # Return empty DataFrame with correct schema
        adducts_df = pl.DataFrame(
            {
                "name": [],
                "charge": [],
                "mass_shift": [],
                "probability": [],
                "complexity": [],
            },
        )

    return adducts_df


def _calculate_formula_mass_shift(study, formula: str) -> float:
    """Calculate mass shift from formula string like "+H", "-H2O", "+Na-H", etc."""
    # Standard atomic masses
    atomic_masses = {
        "H": 1.007825,
        "C": 12.0,
        "N": 14.003074,
        "O": 15.994915,
        "Na": 22.989769,
        "K": 38.963707,
        "Li": 7.016003,
        "Ca": 39.962591,
        "Mg": 23.985042,
        "Fe": 55.934938,
        "Cl": 34.968853,
        "Br": 78.918336,
        "I": 126.904473,
        "P": 30.973762,
        "S": 31.972071,
    }

    total_mass = 0.0

    # Parse formula by splitting on + and - while preserving the operators
    parts = []
    current_part = ""
    current_sign = 1

    for char in formula:
        if char == "+":
            if current_part:
                parts.append((current_sign, current_part))
            current_part = ""
            current_sign = 1
        elif char == "-":
            if current_part:
                parts.append((current_sign, current_part))
            current_part = ""
            current_sign = -1
        else:
            current_part += char

    if current_part:
        parts.append((current_sign, current_part))

    # Process each part
    for sign, part in parts:
        if not part:
            continue

        # Parse element and count (e.g., "H2O" -> H:2, O:1)
        elements = _parse_element_counts(part)

        for element, count in elements.items():
            if element in atomic_masses:
                total_mass += sign * atomic_masses[element] * count

    return total_mass


def _parse_element_counts(formula_part: str) -> dict[str, int]:
    """Parse element counts from a formula part like 'H2O' -> {'H': 2, 'O': 1}"""
    elements: dict[str, int] = {}
    i = 0

    while i < len(formula_part):
        # Get element (uppercase letter, possibly followed by lowercase)
        element = formula_part[i]
        i += 1

        while i < len(formula_part) and formula_part[i].islower():
            element += formula_part[i]
            i += 1

        # Get count (digits following element)
        count_str = ""
        while i < len(formula_part) and formula_part[i].isdigit():
            count_str += formula_part[i]
            i += 1

        count = int(count_str) if count_str else 1
        elements[element] = elements.get(element, 0) + count

    return elements


def _format_adduct_name(components: list[dict]) -> str:
    """Format adduct name from components like [M+H]1+ or [M+2H]2+"""
    if not components:
        return "[M]"

    # Count occurrences of each formula
    from collections import Counter

    formula_counts = Counter(comp["formula"] for comp in components)
    total_charge = sum(comp["charge"] for comp in components)

    # Build formula part with proper multipliers
    formula_parts = []
    for formula, count in sorted(
        formula_counts.items(),
    ):  # Sort for consistent ordering
        if count == 1:
            formula_parts.append(formula)
        else:
            # For multiple occurrences, use count prefix (e.g., 2H, 3Na)
            # Handle special case where formula might already start with + or -
            if formula.startswith(("+", "-")):
                sign = formula[0]
                base_formula = formula[1:]
                formula_parts.append(f"{sign}{count}{base_formula}")
            else:
                formula_parts.append(f"{count}{formula}")

    # Combine formula parts
    formula = "".join(formula_parts)

    # Format charge
    if total_charge == 0:
        charge_str = ""
    elif abs(total_charge) == 1:
        charge_str = "1+" if total_charge > 0 else "1-"
    else:
        charge_str = f"{abs(total_charge)}+" if total_charge > 0 else f"{abs(total_charge)}-"

    return f"[M{formula}]{charge_str}"


def _generate_13c_isotopes(lib_df):
    """
    Generate 13C isotope variants for library entries.

    For each compound with n carbon atoms, creates n+1 entries:
    - iso=0: original compound (no 13C)
    - iso=1: one 13C isotope (+1.00335 Da)
    - iso=2: two 13C isotopes (+2.00670 Da)
    - ...
    - iso=n: n 13C isotopes (+n*1.00335 Da)

    All isotopomers share the same quant_group.

    Args:
        lib_df: Polars DataFrame with library entries

    Returns:
        Polars DataFrame with additional 13C isotope entries
    """
    if lib_df.is_empty():
        return lib_df

    # First, ensure all original entries have iso=0
    original_df = lib_df.with_columns(pl.lit(0).alias("iso"))

    isotope_entries = []
    next_lib_uid = lib_df["lib_uid"].max() + 1 if len(lib_df) > 0 else 1

    # Mass difference for one 13C isotope
    c13_mass_shift = 1.00335  # Mass difference between 13C and 12C

    for row in original_df.iter_rows(named=True):
        formula = row.get("formula", "")
        if not formula:
            continue

        # Count carbon atoms in the formula
        carbon_count = _count_carbon_atoms(formula)
        if carbon_count == 0:
            continue

        # Get the original quant_group to keep it consistent across isotopes
        # All isotopomers of the same compound should have the same quant_group
        quant_group = row.get("quant_group", row.get("cmpd_uid", row.get("lib_uid", 1)))

        # Generate isotope variants (1 to n 13C atoms)
        for iso_num in range(1, carbon_count + 1):
            # Calculate mass shift for this number of 13C isotopes
            mass_shift = iso_num * c13_mass_shift

            # Create new entry
            isotope_entry = dict(row)  # Copy all fields
            isotope_entry["lib_uid"] = next_lib_uid
            isotope_entry["iso"] = iso_num
            isotope_entry["m"] = row["m"] + mass_shift
            isotope_entry["mz"] = (row["m"] + mass_shift) / abs(row["z"]) if row["z"] != 0 else row["m"] + mass_shift
            isotope_entry["quant_group"] = quant_group  # Keep same quant_group

            isotope_entries.append(isotope_entry)
            next_lib_uid += 1

    # Combine original entries (now with iso=0) with isotope entries
    if isotope_entries:
        isotope_df = pl.DataFrame(isotope_entries)
        # Ensure schema compatibility by aligning data types
        try:
            return pl.concat([original_df, isotope_df])
        except Exception as e:
            # If concat fails due to schema mismatch, convert to compatible types
            # Get common schema
            original_schema = original_df.schema
            isotope_schema = isotope_df.schema

            # Cast isotope_df columns to match original_df schema where possible
            cast_exprs = []
            for col_name in isotope_df.columns:
                if col_name in original_schema:
                    target_dtype = original_schema[col_name]
                    cast_exprs.append(pl.col(col_name).cast(target_dtype, strict=False))
                else:
                    cast_exprs.append(pl.col(col_name))

            isotope_df_cast = isotope_df.select(cast_exprs)
            return pl.concat([original_df, isotope_df_cast])
    else:
        return original_df


def _count_carbon_atoms(formula: str) -> int:
    """
    Count the number of carbon atoms in a molecular formula.

    Args:
        formula: Molecular formula string like "C6H12O6"

    Returns:
        Number of carbon atoms
    """
    import re

    if not formula or not isinstance(formula, str):
        return 0

    # Look for carbon followed by optional number
    # C followed by digits, or just C (which means 1)
    carbon_matches = re.findall(r"C(\d*)", formula)

    total_carbons = 0
    for match in carbon_matches:
        if match == "":
            # Just 'C' without number means 1 carbon
            total_carbons += 1
        else:
            # 'C' followed by number
            total_carbons += int(match)

    return total_carbons


def lib_to_consensus(study, chrom_fhwm: float = 5.0, mz_tol: float = 0.01, rt_tol: float = 2.0):
    """Create consensus features from library entries instead of features_df.

    This method takes all rows from lib_df and creates corresponding entries in
    consensus_df with the same columns as merge(). Instead of relying on
    features_df, it populates consensus features directly from library data.

    Before creating new features, it checks for pre-existing consensus features:
    - If rt in lib_df is null: picks consensus feature with matching mz and largest inty_mean
    - If rt is not null: picks consensus feature with matching mz and rt within tolerance
    - If a match is found, skips to the next library entry

    Args:
        study: Study instance with lib_df populated
        chrom_fhwm: Chromatographic full width at half maximum in seconds
                   to infer rt_start_mean and rt_end_mean (default: 5.0)
        mz_tol: m/z tolerance for matching existing consensus features (default: 0.01)
        rt_tol: RT tolerance for matching existing consensus features (default: 2.0)

    Side effects:
        Adds rows to study.consensus_df and study.consensus_mapping_df
        Calls study.find_ms2() at the end
    """
    # Get logger from study if available
    logger = getattr(study, "logger", None)

    # Validate inputs
    if getattr(study, "lib_df", None) is None or study.lib_df.is_empty():
        if logger:
            logger.error("Library (study.lib_df) is empty; call lib_load() first")
        raise ValueError("Library (study.lib_df) is empty; call lib_load() first")

    if logger:
        logger.info(f"Creating consensus features from {len(study.lib_df)} library entries")

    # Initialize consensus DataFrames if they don't exist
    if not hasattr(study, "consensus_df") or study.consensus_df is None:
        study.consensus_df = pl.DataFrame()
    if not hasattr(study, "consensus_mapping_df") or study.consensus_mapping_df is None:
        study.consensus_mapping_df = pl.DataFrame()

    # Get cached adducts for consistent adduct handling
    cached_adducts_df = None
    cached_valid_adducts = None
    try:
        cached_adducts_df = _get_adducts(study)
        if not cached_adducts_df.is_empty():
            cached_valid_adducts = set(cached_adducts_df["name"].to_list())
        else:
            cached_valid_adducts = set()
    except Exception as e:
        if logger:
            logger.warning(f"Could not retrieve study adducts: {e}")
        cached_valid_adducts = set()

    # Always allow '?' adducts
    cached_valid_adducts.add("?")

    # Get starting consensus_uid counter
    if not study.consensus_df.is_empty():
        max_existing_uid = study.consensus_df["consensus_uid"].max()
        consensus_uid_counter = int(max_existing_uid) + 1 if max_existing_uid is not None else 0
    else:
        consensus_uid_counter = 0

    # Track [M+H] iso=0 and [M-H] iso=0 entries for adduct grouping
    base_adduct_groups = {}  # key: (mz, adduct_base), value: adduct_group

    # Process each library entry
    consensus_metadata = []
    consensus_mapping_list = []
    matched_count = 0
    skipped_count = 0

    for lib_row in study.lib_df.iter_rows(named=True):
        # Extract basic library data
        lib_uid = lib_row.get("lib_uid")
        mz = lib_row.get("mz")
        rt = lib_row.get("rt")
        iso = lib_row.get("iso", 0)
        adduct = lib_row.get("adduct")
        z = lib_row.get("z", 1)  # charge

        # Skip entries without essential data
        if mz is None:
            if logger:
                logger.warning(f"Skipping library entry {lib_uid} - no m/z value")
            continue

        # Check for pre-existing consensus features
        existing_match = None
        if not study.consensus_df.is_empty():
            # Filter by m/z tolerance first
            mz_matches = study.consensus_df.filter((pl.col("mz") >= mz - mz_tol) & (pl.col("mz") <= mz + mz_tol))

            if not mz_matches.is_empty():
                if rt is None:
                    # If rt is null, pick the consensus feature with largest inty_mean
                    existing_match = mz_matches.sort("inty_mean", descending=True).head(1)
                else:
                    # If rt is not null, filter by RT tolerance and pick largest inty_mean
                    rt_tolerance = chrom_fhwm  # Use chrom_fhwm as RT tolerance range
                    rt_matches = mz_matches.filter(
                        (pl.col("rt") >= rt - rt_tolerance) & (pl.col("rt") <= rt + rt_tolerance)
                    )
                    if not rt_matches.is_empty():
                        existing_match = rt_matches.sort("inty_mean", descending=True).head(1)

        if existing_match is not None and len(existing_match) > 0:
            # Found a matching consensus feature, skip this library entry
            matched_count += 1
            if logger and matched_count <= 5:  # Log first few matches
                match_uid = existing_match["consensus_uid"][0]
                match_mz = existing_match["mz"][0]
                match_rt = existing_match["rt"][0]
                logger.debug(
                    f"Library entry {lib_uid} (mz={mz:.4f}, rt={rt}) matched existing consensus {match_uid} (mz={match_mz:.4f}, rt={match_rt})"
                )
            continue

        # No match found, create new consensus feature
        # Handle missing RT - use 0 as placeholder
        if rt is None:
            rt = 0.0
            if logger and skipped_count < 5:  # Log first few
                logger.debug(f"Library entry {lib_uid} has no RT, using 0.0")

        # Calculate RT range based on chrom_fhwm
        half_width = chrom_fhwm / 2.0
        rt_start = rt - half_width
        rt_end = rt + half_width

        # Get adduct information
        adduct_top = adduct if adduct else "?"
        adduct_charge_top = None
        adduct_mass_shift_top = None
        adduct_mass_neutral_top = None

        # Parse adduct to get charge and mass shift
        if adduct_top and cached_adducts_df is not None and not cached_adducts_df.is_empty():
            # Look for exact match in study adducts
            matching_adduct = cached_adducts_df.filter(pl.col("name") == adduct_top)
            if not matching_adduct.is_empty():
                adduct_row = matching_adduct.row(0, named=True)
                adduct_charge_top = adduct_row["charge"]
                adduct_mass_shift_top = adduct_row["mass_shift"]

        # Fallback to default values if not found
        if adduct_charge_top is None:
            adduct_charge_top = int(z) if z else 1
            # Default based on study polarity
            study_polarity = getattr(study, "polarity", "positive")
            if study_polarity in ["negative", "neg"]:
                if adduct_charge_top > 0:
                    adduct_charge_top = -adduct_charge_top
                adduct_mass_shift_top = -1.007825
                if adduct_top == "?":
                    adduct_top = "[M-?]1-"
            else:
                if adduct_charge_top < 0:
                    adduct_charge_top = -adduct_charge_top
                adduct_mass_shift_top = 1.007825
                if adduct_top == "?":
                    adduct_top = "[M+?]1+"

        # Calculate neutral mass
        if adduct_charge_top and adduct_mass_shift_top is not None:
            adduct_mass_neutral_top = mz * abs(adduct_charge_top) - adduct_mass_shift_top

        # Determine adduct group for isotopologues and related adducts
        adduct_group = consensus_uid_counter  # Default: each entry gets its own group
        adduct_of = 0  # Default: this is the base adduct

        # Track base adducts ([M+H] iso=0 or [M-H] iso=0) for grouping
        base_adduct_key = None
        if iso == 0 and adduct_top in ["[M+H]+", "[M+H]1+", "[M-H]-", "[M-H]1-"]:
            # This is a base adduct with iso=0
            base_adduct_key = (round(mz, 4), adduct_top)
            base_adduct_groups[base_adduct_key] = consensus_uid_counter
        elif iso > 0:
            # This is an isotopologue, try to find the base adduct
            # Calculate the base m/z (subtract isotope mass shifts)
            c13_mass_shift = 1.00335
            base_mz = mz - (iso * c13_mass_shift / abs(adduct_charge_top))

            # Look for matching base adduct
            for (stored_mz, stored_adduct), stored_group in base_adduct_groups.items():
                if abs(stored_mz - base_mz) < mz_tol and stored_adduct == adduct_top:
                    adduct_group = stored_group
                    adduct_of = stored_group
                    break

        # Create adduct values list with proper structure (format: structured data with fields: adduct, count, percentage, mass)
        adduct_values = [{"adduct": adduct_top, "count": 1, "percentage": 100.0, "mass": 0.0}]

        # Generate unique consensus_id string
        import uuid

        consensus_id_str = str(uuid.uuid4()).replace("-", "")[:16]

        # Build consensus metadata with requested modifications for new entries
        metadata = {
            "consensus_uid": consensus_uid_counter,
            "consensus_id": consensus_id_str,
            "quality": 1.0,
            "number_samples": 0.0,  # Set to 0.0 for library entries
            "rt": float(rt),
            "mz": float(mz),
            "rt_min": float(rt),  # Set to rt as requested
            "rt_max": float(rt),  # Set to rt as requested
            "rt_mean": float(rt),  # Set to rt as requested
            "rt_start_mean": float(rt_start),
            "rt_end_mean": float(rt_end),
            "rt_delta_mean": 0.0,  # Set to 0.0 as requested
            "mz_min": float(mz),  # Set to mz as requested
            "mz_max": float(mz),  # Set to mz as requested
            "mz_mean": float(mz),  # Set to mz as requested
            "mz_start_mean": float(mz),  # Set to mz as requested
            "mz_end_mean": float(mz),  # Set to mz as requested
            "inty_mean": -1.0,  # Set to -1.0 as requested
            "bl": -1.0,
            "chrom_coherence_mean": -1.0,  # Set to -1.0 as requested
            "chrom_prominence_mean": -1.0,  # Set to -1.0 as requested
            "chrom_prominence_scaled_mean": -1.0,  # Set to -1.0 as requested
            "chrom_height_scaled_mean": -1.0,  # Set to -1.0 as requested
            "iso": iso,  # Set to iso from lib_df as requested
            "iso_mean": float(iso),  # Set to iso from lib_df as requested
            "charge_mean": float(abs(z)) if z else 1.0,  # Set to z as requested
            "number_ms2": 0,  # Will be updated by find_ms2
            "adducts": adduct_values,
            "adduct_charge_top": adduct_charge_top,
            "adduct_group": adduct_group,  # Use calculated adduct group
            "adduct_mass_neutral_top": round(adduct_mass_neutral_top, 6)
            if adduct_mass_neutral_top is not None
            else None,
            "adduct_mass_shift_top": round(adduct_mass_shift_top, 6) if adduct_mass_shift_top is not None else None,
            "adduct_of": adduct_of,  # Use calculated adduct_of
            "adduct_top": adduct_top,
            "id_top_name": None,  # Set to null as requested
            "id_top_class": None,  # Set to null as requested
            "id_top_adduct": None,  # Set to null as requested
            "id_top_score": None,  # Set to null as requested
        }

        consensus_metadata.append(metadata)

        # Create mapping entry (maps to library entry as "virtual" feature)
        # Use lib_uid as the feature_uid and a virtual sample_uid of 0
        # Match existing consensus_mapping_df column order: consensus_uid, feature_uid, sample_uid
        consensus_mapping_list.append({
            "consensus_uid": consensus_uid_counter,
            "feature_uid": lib_uid,  # Use lib_uid as feature reference
            "sample_uid": 0,  # Virtual sample for library entries
        })

        consensus_uid_counter += 1

    # Log matching statistics
    if logger:
        total_processed = matched_count + len(consensus_metadata)
        logger.info(
            f"Processed {total_processed} library entries: {matched_count} matched existing consensus features, {len(consensus_metadata)} created new features"
        )

    # Convert to DataFrames with proper schema alignment
    if consensus_metadata:
        new_consensus_df = pl.DataFrame(consensus_metadata, strict=False)

        # Ensure schema compatibility with existing consensus_df
        if not study.consensus_df.is_empty():
            # Cast columns to match existing schema
            existing_schema = study.consensus_df.schema
            cast_exprs = []
            for col_name in new_consensus_df.columns:
                if col_name in existing_schema:
                    target_dtype = existing_schema[col_name]
                    if target_dtype == pl.Null:
                        # For Null columns, use lit(None) to maintain Null type
                        cast_exprs.append(pl.lit(None).alias(col_name))
                    else:
                        cast_exprs.append(pl.col(col_name).cast(target_dtype, strict=False))
                else:
                    cast_exprs.append(pl.col(col_name))

            new_consensus_df = new_consensus_df.select(cast_exprs)

        new_consensus_mapping_df = pl.DataFrame(consensus_mapping_list, strict=False)

        # Append to existing DataFrames
        if not study.consensus_df.is_empty():
            study.consensus_df = pl.concat([study.consensus_df, new_consensus_df])
        else:
            study.consensus_df = new_consensus_df

        if not study.consensus_mapping_df.is_empty():
            study.consensus_mapping_df = pl.concat([study.consensus_mapping_df, new_consensus_mapping_df])
        else:
            study.consensus_mapping_df = new_consensus_mapping_df

        if logger:
            logger.info(f"Added {len(consensus_metadata)} consensus features from library")
    else:
        if logger:
            logger.warning("No valid consensus features created from library")
        return

    # Store operation in history
    if hasattr(study, "update_history"):
        study.update_history(
            ["lib_to_consensus"],
            {"chrom_fhwm": chrom_fhwm, "lib_entries": len(study.lib_df)},
        )

    # Perform find_ms2 at the end
    try:
        if hasattr(study, "find_ms2"):
            if logger:
                logger.info("Running find_ms2 to link MS2 spectra to library-derived consensus features")
            study.find_ms2()
        else:
            if logger:
                logger.warning("find_ms2 method not available on study object")
    except Exception as e:
        if logger:
            logger.warning(f"find_ms2 failed: {e}")

    if logger:
        logger.success(f"lib_to_consensus completed: {len(consensus_metadata)} features added")
