#!/usr/bin/env python3
"""Fetch ontology names from OLS4 API and merge with size data."""

import requests
import csv
import time
import click


@click.command()
@click.option('--sizes-csv', default='ontology_sizes.csv', help='Input CSV with ontology sizes')
@click.option('--output-csv', default='ontology_catalog.csv', help='Output merged catalog CSV')
@click.option('--api-delay', default=0.5, type=float, help='Delay between API requests (seconds)')
def main(sizes_csv, output_csv, api_delay):
    """Fetch ontology metadata from OLS4 API and merge with size data."""
    
    # Load our ontology sizes
    sizes = {}
    with open(sizes_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sizes[row['ontologyId']] = int(row['count'])
    
    print(f"Loaded {len(sizes)} ontology sizes from local data")
    
    # Fetch ontology names from OLS4 API
    print("\nFetching ontology metadata from OLS4 API...")
    ontology_info = {}
    
    page = 0
    total_pages = None
    
    while total_pages is None or page < total_pages:
        url = f"https://www.ebi.ac.uk/ols4/api/ontologies?page={page}&size=20"
        print(f"  Fetching page {page}...", end='')
    
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
    
            if total_pages is None:
                total_pages = data['page']['totalPages']
                print(f" (total pages: {total_pages})")
            else:
                print()
    
            # Extract ontology info
            for onto in data['_embedded']['ontologies']:
                onto_id = onto['ontologyId'].lower()
                title = onto.get('config', {}).get('title', 'Unknown')
                description = onto.get('config', {}).get('description', '')
    
                ontology_info[onto_id] = {
                    'title': title,
                    'description': description[:200] if description else ''
                }
    
            page += 1
            time.sleep(api_delay)  # Be nice to the API
    
        except Exception as e:
            print(f" Error: {e}")
            break
    
    print(f"\nFetched metadata for {len(ontology_info)} ontologies from OLS4")
    
    # Merge data and write output
    print("\nCreating merged CSV...")
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'ontologyId', 'title', 'count', 'description'
        ])
        writer.writeheader()
    
        for onto_id in sorted(sizes.keys(), key=lambda x: sizes[x], reverse=True):
            info = ontology_info.get(onto_id.lower(), {})
            writer.writerow({
                'ontologyId': onto_id,
                'title': info.get('title', 'Unknown'),
                'count': sizes[onto_id],
                'description': info.get('description', '')
            })
    
    print("✓ Created ontology_catalog.csv")
    
    # Show summary
    print("\nTop 20 ontologies by size:")
    count = 0
    for onto_id in sorted(sizes.keys(), key=lambda x: sizes[x], reverse=True):
        if count >= 20:
            break
        info = ontology_info.get(onto_id.lower(), {})
        title = info.get('title', 'Unknown')
        print(f"  {onto_id:15} {sizes[onto_id]:>8,}  {title}")
        count += 1


if __name__ == '__main__':
    main()
