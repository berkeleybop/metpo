import pandas as pd
import click
from typing import Dict, List, Set, Tuple
import os

from oaklib import get_adapter
from oaklib.datamodels.vocabulary import IS_A, PART_OF
import re


class ExternalOntologyHelper:
    """Helper class to retrieve sibling information from external ontologies."""

    # Mapping of IRI patterns to CURIE prefixes
    IRI_TO_CURIE_PATTERNS = {
        'http://purl.obolibrary.org/obo/': '',  # Removes prefix, keeps GO_0008152
        'https://w3id.org/biolink/vocab/': 'biolink:',
    }

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.adapter_cache = {}

    def _iri_to_curie(self, iri: str) -> str:
        """Convert IRI to CURIE format expected by OAKLib."""
        # Try each pattern
        for iri_prefix, curie_prefix in self.IRI_TO_CURIE_PATTERNS.items():
            if iri.startswith(iri_prefix):
                # Remove IRI prefix and convert _ to :
                remainder = iri[len(iri_prefix):]
                # For OBO ontologies: GO_0008152 -> GO:0008152, WBPhenotype_0001084 -> WBPhenotype:0001084
                remainder = re.sub(r'([A-Za-z]+)_(\d+)', r'\1:\2', remainder)
                curie = curie_prefix + remainder
                if self.debug:
                    print(f"    Converted IRI to CURIE: {iri} -> {curie}")
                return curie
        # If no pattern matches, return as-is
        return iri

    def _curie_to_iri(self, curie: str) -> str:
        """Convert CURIE back to IRI format for comparison."""
        # Handle OBO CURIEs: GO:0008152 -> http://purl.obolibrary.org/obo/GO_0008152
        # Also handles mixed-case: WBPhenotype:0001084 -> http://purl.obolibrary.org/obo/WBPhenotype_0001084
        if re.match(r'[A-Za-z]+:\d+', curie):
            prefix, local_id = curie.split(':', 1)
            return f"http://purl.obolibrary.org/obo/{prefix}_{local_id}"
        # Handle biolink CURIEs
        if curie.startswith('biolink:'):
            remainder = curie[8:]  # Remove 'biolink:'
            return f"https://w3id.org/biolink/vocab/{remainder}"
        # If no pattern matches, return as-is
        return curie

    def _extract_ontology_prefix(self, iri: str) -> str:
        """Extract ontology prefix from IRI."""
        # Match patterns like GO_0008152, PATO_0000001, WBPhenotype_0001084, FBcv_0000703, etc.
        # Also handles fragment identifiers like pato#cell_quality, omp#cell_quality
        match = re.search(r'/([A-Za-z]+)[_#]', iri)
        if match:
            prefix = match.group(1)
            if self.debug:
                print(f"    Extracted prefix: {prefix} from {iri}")
            return prefix
        # Match biolink patterns
        if 'biolink' in iri:
            return 'biolink'
        return None

    def _get_adapter(self, iri: str):
        """Get an OAKLib adapter for the external ontology.

        Tries multiple strategies in order:
        1. sqlite:obo: - semantic SQL (best performance, cached locally)
        2. ubergraph: - SPARQL endpoint (many ontologies, requires network)
        3. ols: - OLS4 API (web-based, widely available)
        """
        ontology_prefix = self._extract_ontology_prefix(iri)

        if not ontology_prefix:
            return None

        if ontology_prefix not in self.adapter_cache:
            adapter = None
            strategies = [
                ('sqlite:obo:', 'semantic SQL'),
                ('ubergraph:', 'Ubergraph SPARQL'),
                ('ols:', 'OLS4 API')
            ]

            for strategy_prefix, strategy_name in strategies:
                try:
                    if self.debug:
                        print(f"    Trying {strategy_name} for {ontology_prefix}...")
                    adapter = get_adapter(f"{strategy_prefix}{ontology_prefix.lower()}")
                    if self.debug:
                        print(f"    ✓ Connected via {strategy_name}")
                    break
                except Exception as e:
                    if self.debug:
                        print(f"    ✗ {strategy_name} failed: {type(e).__name__}")
                    continue

            self.adapter_cache[ontology_prefix] = adapter

        return self.adapter_cache.get(ontology_prefix)

    def get_siblings(self, iri: str) -> Set[str]:
        """Get siblings of a term from its external ontology."""
        adapter = self._get_adapter(iri)

        if not adapter:
            if self.debug:
                print(f"    No adapter available for {iri}")
            return set()

        try:
            # Convert IRI to CURIE for querying
            curie = self._iri_to_curie(iri)

            # First check if the term exists
            try:
                label = adapter.label(curie)
                if self.debug:
                    print(f"    Term found: '{label}'")
            except:
                if self.debug:
                    print(f"    Warning: Term not found or label unavailable")

            # Get parents using hierarchical_parents
            parents = list(adapter.hierarchical_parents(curie, isa_only=True))
            if self.debug:
                print(f"    Parents: {len(parents)}")

            # Get siblings through parents
            siblings = set()
            for parent in parents:
                # Get direct children using incoming_relationships
                # This returns (predicate, subject) tuples where subject -> parent
                incoming = list(adapter.incoming_relationships(parent))
                # Filter for subClassOf relationships to get direct children
                children = [subj for pred, subj in incoming if 'subClassOf' in pred]
                if self.debug:
                    print(f"      Parent has {len(children)} children")
                siblings.update(children)

            # Remove self
            siblings.discard(curie)
            siblings.discard(iri)

            # Convert all siblings back to IRI format for comparison with CSV data
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
    default='../metpo_relevant_matches.csv',
    help="Path to the input CSV file containing METPO term matches."
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
    default='sibling_coherence_results.csv',
    help="Path to save coherence results CSV."
)
def main(input_csv: str, metpo_owl: str, good_match_threshold: float, debug: bool, output_csv: str):
    """
    Analyzes sibling coherence for METPO term matches.
    """
    print(f"Loading matches from: {input_csv}")
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at {input_csv}")
        return
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    print(f"Loaded {len(df)} match records.")
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
    for index, row in best_matches_df.iterrows():
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

        external_siblings = external_helper.get_siblings(match_iri)

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
