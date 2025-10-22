"""Basic usage examples for privacy-preserving similarity search."""

import pandas as pd
import numpy as np
from privacy_similarity import PrivacyPreservingSimilaritySearch


def example_customer_deduplication():
    """Example: Find duplicate customer records."""
    print("=" * 60)
    print("Example 1: Customer Deduplication")
    print("=" * 60)

    # Create sample customer data with duplicates
    customers = pd.DataFrame({
        'customer_id': [1, 2, 3, 4, 5, 6, 7, 8],
        'name': [
            'John Smith',
            'Jon Smith',  # Duplicate of 1
            'Jane Doe',
            'John A. Smith',  # Duplicate of 1
            'Alice Johnson',
            'Jane M. Doe',  # Duplicate of 3
            'Bob Williams',
            'Robert Williams'  # Duplicate of 7
        ],
        'email': [
            'john@example.com',
            'jon@example.com',
            'jane@example.com',
            'jsmith@example.com',
            'alice@example.com',
            'jane.doe@example.com',
            'bob@example.com',
            'robert.w@example.com'
        ],
        'address': [
            '123 Main St',
            '123 Main Street',
            '456 Oak Ave',
            '123 Main St.',
            '789 Pine Rd',
            '456 Oak Avenue',
            '321 Elm St',
            '321 Elm Street'
        ]
    })

    print(f"\nOriginal dataset: {len(customers)} customers")
    print(customers)

    # Initialize with differential privacy
    searcher = PrivacyPreservingSimilaritySearch(
        privacy_mode='differential_privacy',
        epsilon=1.0,
        index_type='HNSW'
    )

    # Fit on customer data
    searcher.fit(
        customers,
        sensitive_columns=['name', 'email', 'address'],
        id_column='customer_id'
    )

    # Find duplicates
    duplicates = searcher.find_duplicates(threshold=0.85)

    print(f"\n✓ Found {len(duplicates)} duplicate groups:")
    for i, group in enumerate(duplicates, 1):
        print(f"\nGroup {i} (similarity: {group['similarity']:.3f}):")
        for customer_id in group['ids']:
            customer = customers[customers['customer_id'] == customer_id].iloc[0]
            print(f"  - ID {customer_id}: {customer['name']} ({customer['email']})")

    # Get statistics
    stats = searcher.get_statistics()
    print(f"\nSystem Statistics:")
    print(f"  - Privacy mode: {stats['privacy_mode']}")
    print(f"  - Index type: {stats['index_type']}")
    print(f"  - Number of records: {stats['num_records']}")
    print(f"  - Embedding dimension: {stats['embedding_dimension']}")


def example_similar_customers():
    """Example: Find customers with similar interests."""
    print("\n" + "=" * 60)
    print("Example 2: Similar Customer Discovery")
    print("=" * 60)

    # Create customer data with interests
    customers = pd.DataFrame({
        'customer_id': range(1, 11),
        'name': [
            'Alice', 'Bob', 'Charlie', 'David', 'Emma',
            'Frank', 'Grace', 'Henry', 'Iris', 'Jack'
        ],
        'interests': [
            'sports, technology, travel',
            'technology, gaming, programming',
            'cooking, travel, photography',
            'sports, fitness, health',
            'technology, AI, machine learning',
            'cooking, baking, food',
            'travel, adventure, hiking',
            'gaming, technology, esports',
            'photography, art, design',
            'sports, soccer, basketball'
        ],
        'purchase_history': [
            'laptop, running shoes, camera',
            'gaming pc, keyboard, mouse',
            'cookbook, camera lens, luggage',
            'gym membership, protein powder',
            'python book, gpu, courses',
            'mixer, cookware, apron',
            'backpack, tent, hiking boots',
            'gaming chair, headset, monitor',
            'camera, tripod, editing software',
            'soccer ball, jersey, cleats'
        ]
    })

    print(f"\nDataset: {len(customers)} customers")

    # Initialize searcher
    searcher = PrivacyPreservingSimilaritySearch(
        privacy_mode='differential_privacy',
        epsilon=2.0,  # Less privacy, more accuracy for recommendations
        embedding_model='sentence-transformers/all-MiniLM-L6-v2',
        index_type='HNSW'
    )

    # Fit on interests and purchase history
    searcher.fit(
        customers,
        embedding_columns=['interests', 'purchase_history'],
        id_column='customer_id'
    )

    # Find similar customers for a query
    query = pd.DataFrame({
        'interests': ['technology, programming, computers'],
        'purchase_history': ['laptop, books, online courses']
    })

    print("\nQuery customer interests: technology, programming, computers")
    print("Query purchase history: laptop, books, online courses")

    results = searcher.search(query, k=5, return_distances=True)

    print("\nTop 5 similar customers:")
    for i, customer_id in enumerate(results[0]['ids'], 1):
        customer = customers[customers['customer_id'] == customer_id].iloc[0]
        distance = results[0]['distances'][i-1]
        similarity = 1 / (1 + distance) if distance > 0 else 1.0

        print(f"{i}. {customer['name']} (similarity: {similarity:.3f})")
        print(f"   Interests: {customer['interests']}")
        print(f"   Purchases: {customer['purchase_history']}")


def example_privacy_modes():
    """Example: Compare different privacy modes."""
    print("\n" + "=" * 60)
    print("Example 3: Privacy Modes Comparison")
    print("=" * 60)

    # Sample data
    data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice Smith', 'Bob Jones', 'Charlie Brown', 'David Lee', 'Emma Davis'],
        'email': ['alice@ex.com', 'bob@ex.com', 'charlie@ex.com', 'david@ex.com', 'emma@ex.com']
    })

    privacy_modes = [
        ('none', {}),
        ('secure_hashing', {}),
        ('differential_privacy', {'epsilon': 10.0}),  # Low privacy
        ('differential_privacy', {'epsilon': 1.0}),   # Medium privacy
        ('differential_privacy', {'epsilon': 0.1}),   # High privacy
    ]

    print("\nComparing privacy modes on same dataset:")

    for mode, params in privacy_modes:
        searcher = PrivacyPreservingSimilaritySearch(
            privacy_mode=mode,
            index_type='Flat',  # Exact search
            **params
        )

        searcher.fit(data, sensitive_columns=['name', 'email'], id_column='id')

        stats = searcher.get_statistics()

        privacy_desc = mode
        if mode == 'differential_privacy':
            privacy_desc += f" (ε={params.get('epsilon', 1.0)})"

        print(f"\n{privacy_desc}:")
        print(f"  - Embedding dimension: {stats['embedding_dimension']}")

        # Test search on first record
        query = data.iloc[[0]]
        results = searcher.search(query, k=3)

        print(f"  - Top match for 'Alice Smith': ID {results[0]['ids'][0]}")


def example_incremental_updates():
    """Example: Add records incrementally."""
    print("\n" + "=" * 60)
    print("Example 4: Incremental Updates")
    print("=" * 60)

    # Initial dataset
    initial_data = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'description': ['Data scientist', 'Software engineer', 'Product manager']
    })

    print(f"Initial dataset: {len(initial_data)} records")

    # Fit initial model
    searcher = PrivacyPreservingSimilaritySearch(
        privacy_mode='differential_privacy',
        epsilon=1.0,
        index_type='HNSW'
    )

    searcher.fit(
        initial_data,
        embedding_columns=['description'],
        id_column='id'
    )

    print(f"✓ Initial index built")

    # Add new records
    new_data = pd.DataFrame({
        'id': [4, 5],
        'name': ['David', 'Emma'],
        'description': ['Machine learning engineer', 'UX designer']
    })

    print(f"\nAdding {len(new_data)} new records...")
    searcher.add_records(new_data)

    # Verify
    stats = searcher.get_statistics()
    print(f"✓ Total records now: {stats['num_records']}")

    # Search across all records
    query = pd.DataFrame({
        'description': ['AI researcher']
    })

    results = searcher.search(query, k=3)
    print(f"\nTop matches for 'AI researcher':")
    all_data = pd.concat([initial_data, new_data])
    for customer_id in results[0]['ids']:
        person = all_data[all_data['id'] == customer_id].iloc[0]
        print(f"  - {person['name']}: {person['description']}")


def main():
    """Run all examples."""
    print("Privacy-Preserving Similarity Search - Examples")
    print("=" * 60)

    try:
        example_customer_deduplication()
        example_similar_customers()
        example_privacy_modes()
        example_incremental_updates()

        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
