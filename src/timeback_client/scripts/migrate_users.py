"""Script to migrate users from staging to production environment.

This script handles the migration of users from the staging environment to production.
It includes error handling, logging, and verification of the migration.

Example:
    >>> python -m timeback_client.scripts.migrate_users --staging-client-id xxx --staging-client-secret xxx --prod-client-id yyy --prod-client-secret yyy
"""

import argparse
import logging
import sys
from typing import Dict, List, Any, Tuple
from ..core.client import TimeBackClient
from ..models.user import User

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_all_users(client: TimeBackClient) -> List[Dict[str, Any]]:
    """Get all users from the specified environment.
    
    Args:
        client: The TimeBackClient instance to use
        
    Returns:
        List of user dictionaries
    """
    users = []
    offset = 0
    limit = 100
    
    while True:
        response = client.rostering.users.list_users(
            offset=offset,
            limit=limit
        )
        
        if not response.get('users'):
            break
            
        users.extend(response['users'])
        
        if len(response['users']) < limit:
            break
            
        offset += limit
        
    return users

def migrate_users(
    staging_client: TimeBackClient,
    prod_client: TimeBackClient,
    dry_run: bool = False
) -> Tuple[int, int, List[str]]:
    """Migrate users from staging to production.
    
    Args:
        staging_client: The staging environment client
        prod_client: The production environment client
        dry_run: If True, only print what would be done without making changes
        
    Returns:
        Tuple of (total users, successful migrations, list of failed sourcedIds)
    """
    logger.info("Starting user migration from staging to production")
    
    # Get all users from staging
    staging_users = get_all_users(staging_client)
    total_users = len(staging_users)
    logger.info(f"Found {total_users} users in staging")
    
    if dry_run:
        logger.info("DRY RUN - No changes will be made")
        return total_users, 0, []
    
    # Migrate each user
    successful = 0
    failed_ids = []
    
    for user in staging_users:
        try:
            # Create user in production
            response = prod_client.rostering.users.create_user(user)
            successful += 1
            logger.info(f"Successfully migrated user {user['sourcedId']}")
        except Exception as e:
            logger.error(f"Failed to migrate user {user['sourcedId']}: {str(e)}")
            failed_ids.append(user['sourcedId'])
            
    return total_users, successful, failed_ids

def verify_migration(
    staging_client: TimeBackClient,
    prod_client: TimeBackClient
) -> bool:
    """Verify that the migration was successful.
    
    Args:
        staging_client: The staging environment client
        prod_client: The production environment client
        
    Returns:
        True if verification passed, False otherwise
    """
    logger.info("Verifying migration...")
    
    # Get users from both environments
    staging_users = get_all_users(staging_client)
    prod_users = get_all_users(prod_client)
    
    # Create maps for easy lookup
    staging_map = {u['sourcedId']: u for u in staging_users}
    prod_map = {u['sourcedId']: u for u in prod_users}
    
    # Check that all staging users exist in production
    missing_users = set(staging_map.keys()) - set(prod_map.keys())
    if missing_users:
        logger.error(f"Found {len(missing_users)} users missing from production")
        for user_id in missing_users:
            logger.error(f"Missing user: {user_id}")
        return False
        
    logger.info("All users from staging exist in production")
    return True

def main():
    parser = argparse.ArgumentParser(description='Migrate users from staging to production')
    parser.add_argument('--staging-client-id', required=True, help='Staging environment client ID')
    parser.add_argument('--staging-client-secret', required=True, help='Staging environment client secret')
    parser.add_argument('--prod-client-id', required=True, help='Production environment client ID')
    parser.add_argument('--prod-client-secret', required=True, help='Production environment client secret')
    parser.add_argument('--dry-run', action='store_true', help='Print what would be done without making changes')
    
    args = parser.parse_args()
    
    # Initialize clients
    staging_client = TimeBackClient(
        environment="staging",
        client_id=args.staging_client_id,
        client_secret=args.staging_client_secret
    )
    
    prod_client = TimeBackClient(
        environment="production",
        client_id=args.prod_client_id,
        client_secret=args.prod_client_secret
    )
    
    try:
        # Perform migration
        total, successful, failed = migrate_users(
            staging_client,
            prod_client,
            dry_run=args.dry_run
        )
        
        if args.dry_run:
            logger.info(f"DRY RUN - Would migrate {total} users")
            return 0
            
        # Log results
        logger.info(f"Migration complete:")
        logger.info(f"Total users: {total}")
        logger.info(f"Successfully migrated: {successful}")
        logger.info(f"Failed: {len(failed)}")
        
        if failed:
            logger.error("Failed to migrate the following users:")
            for user_id in failed:
                logger.error(f"  {user_id}")
                
        # Verify migration
        if verify_migration(staging_client, prod_client):
            logger.info("Migration verification passed")
            return 0
        else:
            logger.error("Migration verification failed")
            return 1
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 