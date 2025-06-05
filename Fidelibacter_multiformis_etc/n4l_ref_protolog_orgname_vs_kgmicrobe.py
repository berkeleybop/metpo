#!/usr/bin/env python3
"""
N4L SPARQL Query Processor
Executes SPARQL queries against N4L and KG-Microbe endpoints,
joins the results, and performs post-processing:
- Integer conversion for specific numeric fields.
- Data joined on ncbiTaxonIRI.
- Deduplication and aggregation handled by SPARQL and join.
"""
import math

import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import numpy as np
from typing import Dict, List, Any, Union
import sys
import click


class N4LSparqlProcessor:
    def __init__(self, endpoint_url: str):
        """Initialize with the primary SPARQL endpoint URL."""
        self.endpoint = SPARQLWrapper(endpoint_url)
        self.endpoint.setReturnFormat(JSON)
        self.kg_microbe_endpoint = None  # To be set if KG-Microbe data is included

    def get_n4l_query_by_taxon_iri(self) -> str:
        """Return the SPARQL query for N4L data, aggregated by NCBI Taxon IRI."""
        return """
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX n4l: <http://example.com/n4l/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT distinct
?ref ?year ?pubmedid ?doi
?prot ?protStatementCount
?org ?orgName ?rank ?ncbiTaxonIRI
WHERE {
    # Get the aboutness chain
    GRAPH n4l:protolog_aboutness {
        ?ref n4l:is_about ?prot .
        ?prot n4l:is_about ?org .
    }
    # Verify types
    GRAPH n4l:type_assertions {
        ?ref a n4l:Reference .
        ?prot a n4l:Protolog .
        ?org a n4l:OrganismNames .
    }
    ?org n4l:ncbi_tax_id ?ncbiTaxId .
    BIND(IRI(CONCAT("http://purl.obolibrary.org/obo/NCBITaxon_", REPLACE(STR(?ncbiTaxId), "\\\\.0$", ""))) AS ?ncbiTaxonIRI)
    OPTIONAL {
        GRAPH <http://example.com/n4l/N4L_ID_to_NCBI_mappings.xlsx/N4L_REF.ID_to_DOCID> {
            ?ref n4l:year ?year_raw .
            bind(REPLACE(STR(?year_raw), "\\\\.0$", "") AS ?year)
        }
    }
    OPTIONAL {
        GRAPH <http://example.com/n4l/N4L_ID_to_NCBI_mappings.xlsx/N4L_REF.ID_to_DOCID> {
            ?ref n4l:pubmedid ?pubmedid
        }
    }
    OPTIONAL {
        GRAPH <http://example.com/n4l/N4L_ID_to_NCBI_mappings.xlsx/N4L_REF.ID_to_DOCID> {
            ?ref n4l:doi ?doi
        }
    }
    OPTIONAL {
        ?org n4l:name ?orgName 
    }
    OPTIONAL {
        ?org n4l:rank ?rank 
    }
    # Count statements about each protolog individually
    OPTIONAL {
        SELECT ?prot (COUNT(distinct ?p) as ?protStatementCount)
        WHERE {
            VALUES ?protologGraph {
                <http://example.com/n4l/protolog_normalization_categories_with_1000_DB.xlsx/1000_proto_proj>
                <http://example.com/n4l/protolog_normalization_categories_with_1000_DB.xlsx/Sheet2>
                <http://example.com/n4l/protolog_normalization_categories_with_1000_DB.xlsx/Sheet3>
                <http://example.com/n4l/protolog_normalization_categories_with_1000_KMP.xlsx/1000_proto_proj>
                <http://example.com/n4l/protolog_normalization_categories_with_1000_KMP.xlsx/All%28Sheet1%2C2%2C3%29>
                <http://example.com/n4l/protolog_normalization_categories_with_1000_KMP.xlsx/EffectRIDProtos%28rid.2300_up%29>
                <http://example.com/n4l/protolog_normalization_categories_with_1000_KMP.xlsx/Sheet2>
            }
            GRAPH ?protologGraph {
                ?prot ?p ?o
            }
        }
        group by ?prot
    }
}
"""

    def get_kg_microbe_query(self) -> str:
        """Return the SPARQL query for KG-Microbe assertion counts."""
        return """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?ncbiTaxonIRI (COUNT(?p) as ?kgMicrobeAssertionCount)
WHERE {
    ?a a <https://w3id.org/biolink/vocab/Association> ;
       rdf:subject ?ncbiTaxonIRI ;
       rdf:predicate ?p .
    ?ncbiTaxonIRI <https://w3id.org/biolink/vocab/category> <https://w3id.org/biolink/vocab/OrganismTaxon> .
    MINUS {
        ?a rdf:predicate <https://w3id.org/biolink/vocab/subclass_of>
    }
    MINUS {
        ?a rdf:predicate <https://w3id.org/biolink/vocab/location_of>
    }
}
GROUP BY ?ncbiTaxonIRI
"""

    def execute_query(self, query_string: str, endpoint_url_override: str = None, timeout: int = None) -> List[
        Dict[str, Any]]:
        """Execute the SPARQL query and return results."""
        target_endpoint = self.endpoint
        current_timeout = self.endpoint.timeout if hasattr(self.endpoint, 'timeout') else None

        if endpoint_url_override:
            target_endpoint = SPARQLWrapper(endpoint_url_override)
            target_endpoint.setReturnFormat(JSON)
            if timeout is not None:
                target_endpoint.setTimeout(timeout)
            elif current_timeout is not None:  # Fallback to main endpoint's timeout if specific one not passed
                target_endpoint.setTimeout(current_timeout)
        elif timeout is not None and target_endpoint.timeout != timeout:  # Ensure main endpoint uses passed timeout if different
            target_endpoint.setTimeout(timeout)

        target_endpoint.setQuery(query_string)
        try:
            results = target_endpoint.query().convert()
            return results["results"]["bindings"]
        except Exception as e:
            click.echo(f"Error executing query on {target_endpoint.endpoint}: {e}", err=True)
            # For debugging, you might want to print the query:
            # click.echo(f"Query: {query_string}", err=True)
            raise

    def extract_value(self, binding: Union[Dict, None]) -> Union[str, None]:
        """Extract value from SPARQL binding."""
        if binding is None or 'value' not in binding:
            return None
        return binding['value']

    def convert_to_integer(self, value: Union[str, float, None]) -> Union[int, None]:
        """Convert value to integer, handling various formats."""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                value = value.strip()
                if not value:  # Handle empty string after strip
                    return None
            return int(float(value))  # Convert to float first to handle "xxxx.0"
        except (ValueError, TypeError):
            return None

    def process_query_results(self, results: List[Dict[str, Any]], int_columns: List[str]) -> pd.DataFrame:
        """Process generic SPARQL results into a DataFrame and convert specified columns to integers."""
        rows = []
        if not results and not rows:  # if results is empty
            # If int_columns are known, can create an empty df with those columns + ncbiTaxonIRI
            # For now, let pd.DataFrame handle empty list, which is fine for merge
            pass

        for result_row in results:
            row_dict = {}
            for key, binding in result_row.items():
                row_dict[key] = self.extract_value(binding)
            rows.append(row_dict)

        df = pd.DataFrame(rows)

        for col in int_columns:
            if col in df.columns:
                df[col] = df[col].apply(self.convert_to_integer)
            else:
                # If an expected int_column is missing (e.g. empty result set), add it as float for NAs
                # This helps ensure consistency for merge and later operations like fillna(0)
                df[col] = pd.Series(dtype='float64')

        # Ensure ncbiTaxonIRI column exists, even if results were empty (for merge robustness)
        if 'ncbiTaxonIRI' not in df.columns:
            df['ncbiTaxonIRI'] = pd.Series(dtype='object')

        return df

    def run(self, output_file: str = 'n4l_processed_results.csv', include_kg_microbe: bool = False):
        """Execute the complete pipeline."""
        query_timeout = self.endpoint.timeout if hasattr(self.endpoint, 'timeout') else 300  # Default if not set

        # --- N4L Query ---
        click.echo("Executing N4L SPARQL query...")
        n4l_query_str = self.get_n4l_query_by_taxon_iri()
        n4l_raw_results = self.execute_query(n4l_query_str, timeout=query_timeout)
        click.echo(f"Retrieved {len(n4l_raw_results)} rows from N4L.")

        click.echo("Processing N4L results...")
        df_n4l = self.process_query_results(
            n4l_raw_results,
            int_columns=['protStatementCount']  # 'ncbiTaxId',
        )
        click.echo(f"Processed N4L data into {len(df_n4l)} rows (unique by ncbiTaxonIRI).")

        final_df = df_n4l

        if include_kg_microbe:
            if not self.kg_microbe_endpoint:
                click.echo("KG-Microbe endpoint not set. Skipping KG-Microbe query.", err=True)
            else:
                # --- KG-Microbe Query ---
                click.echo("Executing KG-Microbe SPARQL query...")
                kg_microbe_query_str = self.get_kg_microbe_query()
                kg_microbe_raw_results = self.execute_query(
                    kg_microbe_query_str,
                    endpoint_url_override=self.kg_microbe_endpoint,
                    timeout=query_timeout
                )
                click.echo(f"Retrieved {len(kg_microbe_raw_results)} rows from KG-Microbe.")

                click.echo("Processing KG-Microbe results...")
                df_kg_microbe = self.process_query_results(
                    kg_microbe_raw_results,
                    int_columns=['kgMicrobeAssertionCount']
                )
                click.echo(f"Processed KG-Microbe data into {len(df_kg_microbe)} rows.")

                # --- Join DataFrames ---
                click.echo("Joining N4L and KG-Microbe data...")
                final_df = pd.merge(df_n4l, df_kg_microbe, on='ncbiTaxonIRI', how='outer')
                click.echo(f"Joined dataset has {len(final_df)} rows.")

        if final_df.empty:
            click.echo("No data retrieved or processed. Output file will be empty or not created.")
            # Create an empty file with headers if desired, or just skip saving
            # For now, if empty, to_csv will create a file with headers if columns are defined, or an empty file.
        else:
            # Sort by year (descending), then by org name (first orgName if multiple)
            final_df['sort_year_val'] = final_df['year'].apply(
                lambda x: int(float(x.split('|')[0])) if pd.notna(x) and x and x.split('|')[0] else 0
            )
            # Use first orgName for sorting if it's a concatenated string
            final_df['sort_orgName'] = final_df['orgName'].apply(
                lambda x: x.split('|')[0] if pd.notna(x) and x else ""
            )
            final_df = final_df.sort_values(['sort_year_val', 'sort_orgName'], ascending=[False, True])
            final_df = final_df.drop(columns=['sort_year_val', 'sort_orgName'], errors='ignore')

        # Save to CSV
        final_df.to_csv(output_file, index=False)
        click.echo(f"Results saved to {output_file}")

        # Print summary statistics
        if not final_df.empty:
            click.echo("\n--- Summary Statistics ---")
            # N4L specific columns that are now multi-valued strings (originally single values)
            # For 'nunique', it refers to unique ncbiTaxonIRI entries.
            # We can count unique items within the concatenated strings if needed, but that's more complex.
            if 'refs' in final_df.columns: click.echo(
                f"Unique ncbiTaxonIRI with references: {final_df['ref'].notna().sum()}")
            if 'prots' in final_df.columns: click.echo(
                f"Unique ncbiTaxonIRI with protologs: {final_df['prot'].notna().sum()}")
            if 'orgs' in final_df.columns: click.echo(
                f"Unique ncbiTaxonIRI with organisms: {final_df['org'].notna().sum()}")

            summary_cols = ['year', 'pubmedid', 'doi', 'orgName', 'ncbiTaxonIRI', 'rank',
                            'protStatementCount']
            if include_kg_microbe and 'kgMicrobeAssertionCount' not in summary_cols:
                summary_cols.append('kgMicrobeAssertionCount')

            for col in summary_cols:
                if col in final_df.columns:
                    non_null = final_df[col].notna().sum()
                    pct = (non_null / len(final_df)) * 100 if len(final_df) > 0 else 0
                    click.echo(f"Rows with {col}: {non_null} ({pct:.1f}%)")
                else:
                    click.echo(f"Column {col} not found in final_df for summary.")

            if include_kg_microbe and 'protStatementCount' in final_df.columns and 'kgMicrobeAssertionCount' in final_df.columns:
                click.echo("\n--- Top 10 Organisms by Combined Assertion Count (if applicable) ---")
                # Ensure counts are numeric, fill NaN with 0 for sum
                final_df['numeric_protolog_count'] = pd.to_numeric(final_df['protStatementCount'],
                                                                   errors='coerce').fillna(0)
                final_df['numeric_kg_microbe_count'] = pd.to_numeric(final_df['kgMicrobeAssertionCount'],
                                                                     errors='coerce').fillna(0)

                final_df['combined_score'] = np.sqrt(
                    final_df['numeric_protolog_count'] * final_df['numeric_kg_microbe_count'])

                top_orgs_df = final_df.nlargest(10, 'combined_score')

                for idx, row in top_orgs_df.iterrows():
                    org_name_display = row['orgName'].split('|')[0] if pd.notna(row['orgName']) and row[
                        'orgName'] else "N/A"
                    year_display = row['year'].split('|')[0] if pd.notna(row['year']) and row['year'] else "N/A"
                    click.echo(
                        f"{org_name_display}: {row['combined_score']} total "
                        f"(N4L: {row['numeric_protolog_count']}, KG-Microbe: {row['numeric_kg_microbe_count']}, Year: {year_display})"
                    )
                final_df = final_df.drop(
                    columns=['numeric_protolog_count', 'numeric_kg_microbe_count', 'combined_score'], errors='ignore')

        return final_df


@click.command()
@click.option('--n4l-endpoint',
              required=True,
              type=str,
              help='Main N4L SPARQL endpoint URL (e.g., http://localhost:7200/repositories/metpo_n4l_etc_automated).')
@click.option('-o', '--output',
              default='n4l_processed_results.csv',
              show_default=True,
              help='Output CSV file.')
@click.option('--timeout',
              default=300,
              show_default=True,
              type=int,
              help='Query timeout in seconds.')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Enable verbose output.')
@click.option('--include-kg-microbe', '-kgm',
              is_flag=True,
              help='Include KG-Microbe assertion counts via a separate query.')
@click.option('--kg-microbe-endpoint',
              default='http://localhost:7200/repositories/kg_microbe',  # Default, adjust if KG-Microbe is elsewhere
              show_default=True,
              help='KG-Microbe endpoint URL for its query.')
def main(n4l_endpoint: str, output: str, timeout: int, verbose: bool, include_kg_microbe: bool,
         kg_microbe_endpoint: str):
    """
    Process N4L SPARQL query results (and optionally KG-Microbe),
    joins them by ncbiTaxonIRI, and saves to CSV.

    ENDPOINT: Main N4L SPARQL endpoint URL (e.g., http://localhost:7200/repositories/n4l)
    """
    if verbose:
        click.echo(f"N4L Endpoint: {n4l_endpoint}")
        click.echo(f"Output file: {output}")
        click.echo(f"Timeout: {timeout} seconds")
        if include_kg_microbe:
            click.echo(f"Including KG-Microbe data from endpoint: {kg_microbe_endpoint}")

    try:
        processor = N4LSparqlProcessor(n4l_endpoint)
        processor.endpoint.setTimeout(timeout)  # Set timeout for the main endpoint wrapper

        if include_kg_microbe:
            processor.kg_microbe_endpoint = kg_microbe_endpoint

        processor.run(output_file=output, include_kg_microbe=include_kg_microbe)

    except Exception as e:
        click.echo(f"An critical error occurred: {e}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
