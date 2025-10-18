"""
Generic DynamoDB Repository Package

This package provides both synchronous and asynchronous repository classes
for DynamoDB operations with a consistent interface, plus filtering utilities.

Classes:
    GenericRepository: Synchronous DynamoDB repository
    AsyncGenericRepository: Asynchronous DynamoDB repository
    FilterHelper: Utility class for building DynamoDB filter expressions
    Attr: DynamoDB condition expression builder (from boto3)

Example:
    from generic_repo import GenericRepository, AsyncGenericRepository, Attr

    # Sync usage with filtering
    repo = GenericRepository(table_name='my-table', primary_key_name='id')
    for item in repo.load_all(filters={'status': 'active', 'age': {'gt': 18}}):
        print(item)

    # Conditional updates
    result = repo.update(
        primary_key_value='item-123',
        update_data={'status': 'active'},
        condition_expression=Attr('approved').eq(True),
        rejection_message="Item must be approved first"
    )
    if result.get('success') == False:
        print(f"Update rejected: {result['message']}")

    # Async usage with filtering
    async with AsyncGenericRepository(table_name='my-table', primary_key_name='id') as repo:
        async for item in repo.load_all(filters={'status': 'active'}):
            print(item)
"""

from .async_repo import AsyncGenericRepository
from .filter_helper import FilterHelper
from .sync_repo import GenericRepository

__all__ = ['GenericRepository', 'AsyncGenericRepository', 'FilterHelper']

__version__ = '2.0.3'
__author__ = 'Subrat'
__email__ = 'subratamal@gmail.com'
__description__ = 'Generic DynamoDB Repository with sync and async support'
