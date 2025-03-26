"""Run the migration from staging to production with provided credentials.

This script migrates specific users from staging to production based on their OneRoster IDs.
"""

from timeback_client import TimeBackClient
import logging
import json
import sys
from typing import List, Dict, Any, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API URLs
STAGING_URL = "https://staging.alpha-1edtech.com"
PRODUCTION_URL = "https://alpha-1edtech.com"

def get_user_by_id(client: TimeBackClient, sourcedId: str) -> Dict[str, Any]:
    """Get a specific user from the API.
    
    Args:
        client: The TimeBackClient instance
        sourcedId: The OneRoster ID of the user
        
    Returns:
        The user data or None if not found
    """
    try:
        response = client.rostering.users._make_request(f"/users/{sourcedId}")
        if not response or 'user' not in response:
            logger.error(f"User {sourcedId} not found")
            return None
        return response['user']
    except Exception as e:
        logger.error(f"Failed to get user {sourcedId}: {str(e)}")
        return None

def migrate_specific_users(
    staging_client: TimeBackClient,
    prod_client: TimeBackClient,
    user_ids: List[str],
    dry_run: bool = False
) -> Tuple[int, int, List[str]]:
    """Migrate specific users from staging to production.
    
    Args:
        staging_client: The staging environment client
        prod_client: The production environment client
        user_ids: List of OneRoster IDs to migrate
        dry_run: If True, only print what would be done without making changes
        
    Returns:
        Tuple of (total users, successful migrations, list of failed sourcedIds)
    """
    logger.info(f"Starting migration of {len(user_ids)} users from staging to production")
    
    if dry_run:
        logger.info("DRY RUN - No changes will be made")
        return len(user_ids), 0, []
    
    successful = 0
    failed_ids = []
    
    for user_id in user_ids:
        try:
            # Get user from staging
            user = get_user_by_id(staging_client, user_id)
            if not user:
                logger.error(f"User {user_id} not found in staging")
                failed_ids.append(user_id)
                continue
                
            # Check if user already exists in production
            existing_user = get_user_by_id(prod_client, user_id)
            if existing_user:
                logger.info(f"User {user_id} already exists in production, skipping")
                successful += 1
                continue
                
            # Create user in production
            try:
                response = prod_client.rostering.users.create_user(user)
                if not response:
                    raise Exception("No response from create_user")
                successful += 1
                logger.info(f"Successfully migrated user {user_id}")
            except Exception as e:
                logger.error(f"Failed to create user {user_id} in production: {str(e)}")
                failed_ids.append(user_id)
        except Exception as e:
            logger.error(f"Failed to migrate user {user_id}: {str(e)}")
            failed_ids.append(user_id)
            
    return len(user_ids), successful, failed_ids

def verify_specific_users(
    staging_client: TimeBackClient,
    prod_client: TimeBackClient,
    user_ids: List[str]
) -> bool:
    """Verify that specific users were migrated successfully.
    
    Args:
        staging_client: The staging environment client
        prod_client: The production environment client
        user_ids: List of OneRoster IDs to verify
        
    Returns:
        True if verification passed, False otherwise
    """
    logger.info("Verifying migration...")
    
    missing_users = []
    for user_id in user_ids:
        staging_user = get_user_by_id(staging_client, user_id)
        prod_user = get_user_by_id(prod_client, user_id)
        
        if not staging_user:
            logger.error(f"User {user_id} not found in staging")
            missing_users.append(user_id)
            continue
            
        if not prod_user:
            logger.error(f"User {user_id} not found in production")
            missing_users.append(user_id)
            continue
    
    if missing_users:
        logger.error(f"Found {len(missing_users)} users missing from production")
        for user_id in missing_users:
            logger.error(f"Missing user: {user_id}")
        return False
        
    logger.info("All specified users exist in production")
    return True

def main():
    # For testing, you can specify OneRoster IDs here
    # In production, these would come from your database
    test_user_ids = [
        "9cb17b8f-b631-4216-9241-03526b04b51c",
        "2f6e63bf-9d4a-48bb-a7a6-469cb20b1939"
    ]
    
    # Initialize clients with provided credentials
    staging_client = TimeBackClient(
        api_url=STAGING_URL,
        environment="staging",
        client_id="6lig33t22dftijdp84cha60eba",
        client_secret="1ut5ge57il9bt4jnu4680c6rlg1q0s22rvmccki84defcjfpc4u6"
    )
    
    prod_client = TimeBackClient(
        api_url=PRODUCTION_URL,
        environment="production",
        client_id="5cftjthvktn8k4au2j294gr639",
        client_secret="1dc6erific6hc64r6d0s175iqipptuu7qa6bhptd9erj1odte4ga"
    )
    
    try:
        # First do a dry run
        logger.info("Performing dry run...")
        total, successful, failed = migrate_specific_users(
            staging_client,
            prod_client,
            test_user_ids,
            dry_run=True
        )
        
        logger.info(f"Dry run complete - Would migrate {total} users")
        
        # Ask for confirmation
        response = input("\nDo you want to proceed with the actual migration? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Migration cancelled by user")
            return
        
        # Perform actual migration
        logger.info("Starting actual migration...")
        total, successful, failed = migrate_specific_users(
            staging_client,
            prod_client,
            test_user_ids,
            dry_run=False
        )
        
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
        if verify_specific_users(staging_client, prod_client, test_user_ids):
            logger.info("Migration verification passed")
        else:
            logger.error("Migration verification failed")
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 