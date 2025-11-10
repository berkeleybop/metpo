import pandas as pd
import click
from typing import Dict, List, Set, Tuple
import os

from oaklib import get_adapter
from oaklib.datamodels.vocabulary import IS_A, PART_OF
import re
from dotenv import load_dotenv, find_dotenv
from tqdm import tqdm


class ExternalOntologyHelper:
    """Helper class to retrieve sibling information from external ontologies."""

    # Mapping of IRI patterns to CURIE prefixes
    IRI_TO_CURIE_PATTERNS = {
        'http://purl.obolibrary.org/obo/': '',  # Removes prefix, keeps GO_0008152
        'https://w3id.org/biolink/vocab/': 'biolink:',
    }

    # Manual mapping from ontology prefix to local DB file
    LOCAL_DB_MAP = {
        'mco': 'mco.db',
        'micro': 'MicrO-2025-03-20-merged.db',
        'mpo': 'mpo_v0.74.en_only.db',
        'n4l_merged': 'n4l_merged.db',
        'omp': 'omp.db',
        'fao': 'fao.db'
    }

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.adapter_cache = {}

    def _iri_to_curie(self, iri: str) -> str:
        """Convert IRI to CURIE format expected by OAKLib."""
        for iri_prefix, curie_prefix in self.IRI_TO_CURIE_PATTERNS.items():
            if iri.startswith(iri_prefix):
                remainder = iri[len(iri_prefix):]
                remainder = re.sub(r'([A-Za-z]+)_(\d+)', r'\1:\2', remainder)
                curie = curie_prefix + remainder
                if self.debug:
                    print(f"    Converted IRI to CURIE: {iri} -> {curie}")
                return curie
        return iri

    def _curie_to_iri(self, curie: str) -> str:
        """Convert CURIE back to IRI format for comparison."""
        if re.match(r'[A-Za-z]+:\d+', curie):
            prefix, local_id = curie.split(':', 1)
            return f"http://purl.obolibrary.org/obo/{prefix}_{local_id}"
        if curie.startswith('biolink:'):
            remainder = curie[8:]
            return f"https://w3id.org/biolink/vocab/{remainder}"
        return curie

    def _extract_ontology_prefix_from_iri(self, iri: str) -> str:
        """Extract ontology prefix from IRI as a fallback."""
        match = re.search(r'/([A-Za-z]+)[_#]', iri)
        if match:
            prefix = match.group(1)
            if self.debug:
                print(f"    Extracted prefix from IRI: {prefix} from {iri}")
            return prefix
        if 'biolink' in iri:
            return 'biolink'
        return None

    def _get_adapter(self, ontology_prefix: str, iri_for_fallback: str):
        """Get an OAKLib adapter for the external ontology."""
        if not ontology_prefix:
            ontology_prefix = self._extract_ontology_prefix_from_iri(iri_for_fallback)

        if not ontology_prefix:
            return None

        if ontology_prefix not in self.adapter_cache:
            adapter = None
            prefix_lower = ontology_prefix.lower()

            # Strategy 1: Local SQLite DBs
            local_db_file = self.LOCAL_DB_MAP.get(prefix_lower)
            if local_db_file and os.path.exists(local_db_file):
                try:
                    if self.debug:
                        print(f"    Trying Local SQLite DB for {ontology_prefix}...")
                    adapter = get_adapter(f"sqlite:{local_db_file}")
                    if self.debug:
                        print(f"    ✓ Connected via Local SQLite DB: {local_db_file}")
                except Exception as e:
                    if self.debug:
                        print(f"    ✗ Local SQLite DB failed: {type(e).__name__}")
            
            # Strategy 2: Local OWL files
            if not adapter:
                # Check for case-sensitive match first, then uppercase
                for owl_filename in [f"{ontology_prefix}.owl", f"{ontology_prefix.upper()}.owl"]:
                    local_owl_path = f"../external/ontologies/bioportal/{owl_filename}"
                    if os.path.exists(local_owl_path):
                        try:
                            if self.debug:
                                print(f"    Trying Local OWL for {ontology_prefix}...")
                            adapter = get_adapter(f"pronto:{local_owl_path}")
                            if self.debug:
                                print(f"    ✓ Connected via Local OWL: {local_owl_path}")
                            break # Stop if found
                        except Exception as e:
                            if self.debug:
                                print(f"    ✗ Local OWL failed: {type(e).__name__}")

            # Strategy 3 & onwards: Web-based strategies
            if not adapter:
                web_strategies = [
                    ('bioportal', 'BioPortal API'), # Use original case for BioPortal
                    ('ubergraph', 'Ubergraph SPARQL'),
                    ('ols', 'OLS4 API')
                ]

                for strategy, name in web_strategies:
                    try:
                        # Use original case for bioportal, lowercase for others
                        prefix_to_use = ontology_prefix if strategy == 'bioportal' else prefix_lower
                        if self.debug:
                            print(f"    Trying {name} for {prefix_to_use}...")
                        adapter = get_adapter(f"{strategy}:{prefix_to_use}")
                        if self.debug:
                            print(f"    ✓ Connected via {name}")
                        break # Found a working strategy
                    except Exception as e:
                        if self.debug:
                            print(f"    ✗ {name} failed: {type(e).__name__}")
                        continue

            self.adapter_cache[ontology_prefix] = adapter

        return self.adapter_cache.get(ontology_prefix)

    def get_siblings(self, iri: str, ontology_prefix: str = None) -> Set[str]:
        """Get siblings of a term from its external ontology."""
        adapter = self._get_adapter(ontology_prefix, iri_for_fallback=iri)

        if not adapter:
            if self.debug:
                print(f"    No adapter available for {iri}")
            return set()

        try:
            curie = self._iri_to_curie(iri)
            try:
                label = adapter.label(curie)
                if self.debug:
                    print(f"    Term found: '{label}'")
            except:
                if self.debug:
                    print(f"    Warning: Term not found or label unavailable for {curie}")

            parents = list(adapter.hierarchical_parents(curie, isa_only=True))
            if self.debug:
                print(f"    Parents: {len(parents)}")

            siblings = set()
            for parent in parents:
                incoming = list(adapter.incoming_relationships(parent))
                children = [subj for pred, subj in incoming if 'subClassOf' in pred]
                if self.debug:
                    print(f"      Parent has {len(children)} children")
                siblings.update(children)

            siblings.discard(curie)
            siblings.discard(iri)

            siblings_iris = {self._curie_to_iri(s) for s in siblings}

            if self.debug:
                print(f"    Siblings found: {len(siblings_iris)}")

            return siblings_iris
        except Exception as e:
            if self.debug:
                print(f"    Error getting siblings: {type(e).__name__}: {e}")
            return set()


class OaklibHierarchy:
    METPO_BASE_IRI = "https://w3id.org/metpo/"

    def __init__(self, ontology_path: str, debug: bool = False):
        self.debug = debug
        if self.debug:
            print(f"Initializing OAKLib adapter for: {ontology_path}")
        self.adapter = get_adapter(f"pronto:{ontology_path}")
        if self.debug:
            print("OAKLib adapter initialized.")

    def _curie_to_iri(self, curie: str) -> str:
        """Convert METPO CURIE to IRI."""
        if curie.startswith("METPO:"):
            return curie.replace("METPO:", self.METPO_BASE_IRI)
        return curie

    def _iri_to_curie(self, iri: str) -> str:
        """Convert METPO IRI to CURIE."""
        if iri.startswith(self.METPO_BASE_IRI):
            return iri.replace(self.METPO_BASE_IRI, "METPO:")
        return iri

    def get_parents(self, curie: str) -> Set[str]:
        """Get direct parents of a term."""
        iri = self._curie_to_iri(curie)
        parent_iris = list(self.adapter.hierarchical_parents(iri))
        parents = {self._iri_to_curie(p) for p in parent_iris}
        if self.debug:
            print(f"  Debug: Parents for {curie}: {parents}")
        return parents

    def get_children(self, curie: str) -> Set[str]:
        """Get direct children of a term."""
        iri = self._curie_to_iri(curie)
        # incoming_relationships returns (predicate, subject) tuples
        # We want subjects where predicate is rdfs:subClassOf
        relationships = list(self.adapter.incoming_relationships(iri))
        children_iris = [subj for pred, subj in relationships if pred == 'rdfs:subClassOf']
        children = {self._iri_to_curie(c) for c in children_iris}
        if self.debug:
            print(f"  Debug: Children for {curie}: {children}")
        return children

    def get_siblings(self, curie: str) -> Set[str]:
        """Get siblings of a term (terms sharing the same parent)."""
        siblings = set()
        parents = self.get_parents(curie)
        if self.debug:
            print(f"  Debug: Parents found for {curie}: {parents}")
        for parent_curie in parents:
            for child_curie in self.get_children(parent_curie):
                if child_curie != curie:
                    siblings.add(child_curie)
        if self.debug:
            print(f"  Debug: Siblings for {curie}: {siblings}")
        return siblings


@click.command()
@click.option(
    '--input-csv',
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    default='../metpo_relevant_mappings.sssom.tsv',
    help="Path to the SSSOM TSV file containing METPO term mappings."
)
@click.option(
    '--metpo-owl',
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    default='../src/ontology/metpo.owl',
    help="Path to the METPO OWL file for hierarchy parsing."
)
@click.option(
    '--good-match-threshold',
    type=float,
    default=0.9,
    help="Distance threshold below which a match is considered 'good'."
)
@click.option("--debug", is_flag=True, help="Enable verbose debug output.")
@click.option(
    '--output-csv',
    type=click.Path(dir_okay=False, path_type=str),
    default='../data/coherence/sibling_coherence_analysis_output.csv',
    help="Path to save coherence results CSV."
)
def main(input_csv: str, metpo_owl: str, good_match_threshold: float, debug: bool, output_csv: str):
    """
    Analyzes sibling coherence for METPO term mappings from SSSOM TSV.
    """
    # Load environment variables from .env file, searching from the current working directory upwards
    # This allows the script to find the .env file in the parent metpo directory
    load_dotenv(find_dotenv(usecwd=True))

    print(f"Loading mappings from: {input_csv}")
    try:
        # Read SSSOM TSV (skip metadata lines starting with #)
        df = pd.read_csv(input_csv, sep='\t', comment='#')
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_csv}")
        return
    except Exception as e:
        print(f"Error loading SSSOM TSV: {e}")
        return

    # Drop rows with missing similarity_score to prevent NaN distances
    df.dropna(subset=['similarity_score'], inplace=True)

    # Map SSSOM columns to expected column names
    df['distance'] = 1.0 - df['similarity_score']
    df['metpo_id'] = df['subject_id']
    df['metpo_label'] = df['subject_label']
    df['match_document'] = df['object_label']
    df['match_ontology'] = df['object_source']
    df['match_iri'] = df['object_id']

    # Drop rows with missing subject_id to prevent key errors
    df.dropna(subset=['metpo_id'], inplace=True)

    print(f"Loaded {len(df)} mapping records.")
    print(f"Using good match threshold: {good_match_threshold}")

    # Initialize METPO hierarchy parser
    metpo_hierarchy = OaklibHierarchy(metpo_owl, debug=debug)

    # Initialize external ontology helper
    external_helper = ExternalOntologyHelper(debug=debug)

    # Filter for best matches for each METPO term
    # We only care about the single best match for sibling coherence
    best_matches_df = df.loc[df.groupby('metpo_id')['distance'].idxmin()]

    # Create lookup: metpo_id -> list of all match IRIs
    metpo_match_lookup = df.groupby('metpo_id')['match_iri'].apply(set).to_dict()

    coherence_scores = []
    for index, row in tqdm(best_matches_df.iterrows(), total=len(best_matches_df), desc="Analyzing Sibling Coherence"):
        metpo_id = row['metpo_id']
        metpo_label = row['metpo_label']
        match_iri = row['match_iri']
        match_ontology = row['match_ontology']
        match_distance = row['distance']

        if debug:
            print(f"\n--- Analyzing {metpo_label} ({metpo_id}) ---")
            print(f"  Best match: {row['match_document']} ({match_iri}) from {match_ontology}, distance: {match_distance:.3f}")

        # Get METPO siblings
        metpo_siblings = metpo_hierarchy.get_siblings(metpo_id)

        if debug:
            print(f"  METPO siblings: {len(metpo_siblings)}")

        # Get external ontology siblings
        if debug:
            print(f"  Fetching siblings from external ontology ({match_ontology})...")

        external_siblings = external_helper.get_siblings(match_iri, ontology_prefix=match_ontology)

        if debug:
            print(f"  External siblings: {len(external_siblings)}")

        # Calculate coherence: how many METPO siblings have matches to external siblings?
        coherent_siblings = 0
        if metpo_siblings and external_siblings:
            for metpo_sibling_id in metpo_siblings:
                # Get all matches for this METPO sibling
                sibling_matches = metpo_match_lookup.get(metpo_sibling_id, set())
                # Check if any match is in external siblings
                if sibling_matches & external_siblings:
                    coherent_siblings += 1
                    if debug:
                        matching_iris = sibling_matches & external_siblings
                        print(f"    {metpo_sibling_id} matches external sibling: {list(matching_iris)[0]}")

        # Calculate coherence score
        if metpo_siblings:
            coherence_score = coherent_siblings / len(metpo_siblings)
        else:
            coherence_score = None  # No siblings to compare

        if debug:
            if coherence_score is not None:
                print(f"  Coherence: {coherent_siblings}/{len(metpo_siblings)} = {coherence_score:.3f}")
            else:
                print(f"  Coherence: N/A (no siblings to compare)")

        coherence_scores.append({
            'metpo_id': metpo_id,
            'metpo_label': metpo_label,
            'match_iri': match_iri,
            'match_ontology': match_ontology,
            'match_distance': match_distance,
            'metpo_sibling_count': len(metpo_siblings),
            'external_sibling_count': len(external_siblings),
            'coherent_sibling_count': coherent_siblings,
            'coherence_score': coherence_score
        })

    print("\n=== Sibling Coherence Analysis Summary ===")
    summary_df = pd.DataFrame(coherence_scores)

    # Calculate overall statistics
    total_terms = len(summary_df)
    terms_with_siblings = len(summary_df[summary_df['metpo_sibling_count'] > 0])
    terms_with_external_siblings = len(summary_df[summary_df['external_sibling_count'] > 0])

    # Get coherence statistics (excluding None values)
    coherence_values = summary_df['coherence_score'].dropna()
    if len(coherence_values) > 0:
        mean_coherence = coherence_values.mean()
        median_coherence = coherence_values.median()
        high_coherence_count = len(coherence_values[coherence_values >= 0.5])
    else:
        mean_coherence = median_coherence = high_coherence_count = 0

    print(f"\nTotal terms analyzed: {total_terms}")
    print(f"Terms with METPO siblings: {terms_with_siblings} ({terms_with_siblings/total_terms*100:.1f}%)")
    print(f"Terms with external siblings retrieved: {terms_with_external_siblings} ({terms_with_external_siblings/total_terms*100:.1f}%)")
    print(f"Terms with coherence scores: {len(coherence_values)}")
    print(f"\nCoherence Statistics:")
    print(f"  Mean coherence: {mean_coherence:.3f}")
    print(f"  Median coherence: {median_coherence:.3f}")
    print(f"  High coherence (≥0.5): {high_coherence_count}/{len(coherence_values)} ({high_coherence_count/len(coherence_values)*100 if len(coherence_values) > 0 else 0:.1f}%)")

    # Show top coherent matches
    print(f"\n=== Top 10 Most Coherent Matches ===")
    top_coherent = summary_df.dropna(subset=['coherence_score']).nlargest(10, 'coherence_score')
    for idx, row in top_coherent.iterrows():
        print(f"{row['metpo_label']} ({row['metpo_id']})")
        print(f"  → {row['match_ontology']}: {row['match_iri']}")
        print(f"  Coherence: {row['coherence_score']:.3f} ({row['coherent_sibling_count']}/{row['metpo_sibling_count']} siblings align)")
        print()

    # Show low coherence matches for review
    print(f"\n=== Terms with Low Coherence (<0.3) ===")
    low_coherent = summary_df[summary_df['coherence_score'] < 0.3].dropna(subset=['coherence_score'])
    if len(low_coherent) > 0:
        for idx, row in low_coherent.head(10).iterrows():
            print(f"{row['metpo_label']} ({row['metpo_id']})")
            print(f"  → {row['match_ontology']}: {row['match_iri']}")
            print(f"  Coherence: {row['coherence_score']:.3f} ({row['coherent_sibling_count']}/{row['metpo_sibling_count']} siblings align)")
            print()
    else:
        print("  No terms with low coherence found!")

    # Save results to CSV
    summary_df.to_csv(output_csv, index=False)
    print(f"\n✓ Full results saved to: {output_csv}")


if __name__ == "__main__":
    main()
