"""
API User Fetcher v3.0 - Production Ready
Complete with logging, caching, and rate limiting
"""

import requests
import sys
import json
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import time


# Configure logging
def setup_logging(log_file: str = 'user_fetcher.log', verbose: bool = False):
    """Setup logging configuration"""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


class CacheManager:
    """Simple cache manager for API responses"""
    
    def __init__(self, cache_duration: int = 300):
        """
        Initialize cache manager.
        
        Args:
            cache_duration (int): Cache duration in seconds (default: 5 minutes)
        """
        self.cache_duration = cache_duration
        self.cache_file = Path('cache') / 'api_cache.json'
        self.cache_file.parent.mkdir(exist_ok=True)
    
    def get(self) -> Optional[Dict]:
        """Get cached data if valid"""
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                cached_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cache_time < timedelta(seconds=self.cache_duration):
                return cached_data['data']
        except Exception as e:
            logging.warning(f"Cache read error: {e}")
        
        return None
    
    def set(self, data: List[Dict]) -> None:
        """Save data to cache"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            logging.warning(f"Cache write error: {e}")
    
    def clear(self) -> None:
        """Clear cache"""
        if self.cache_file.exists():
            self.cache_file.unlink()


class UserFetcher:
    """Enhanced class to handle fetching and displaying user data from API"""
    
    BASE_URL = "https://jsonplaceholder.typicode.com/users"
    
    def __init__(self, timeout: int = 10, use_cache: bool = True, logger=None):
        """
        Initialize the UserFetcher.
        
        Args:
            timeout (int): Request timeout in seconds
            use_cache (bool): Whether to use caching
            logger: Logger instance
        """
        self.timeout = timeout
        self.users = None
        self.use_cache = use_cache
        self.cache = CacheManager() if use_cache else None
        self.logger = logger or logging.getLogger(__name__)
        self.last_request_time = None
    
    def _rate_limit(self, min_interval: float = 1.0):
        """Simple rate limiting"""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    def fetch_users(self, force_refresh: bool = False) -> Optional[List[Dict]]:
        """
        Fetch users from the JSONPlaceholder API with caching support.
        
        Args:
            force_refresh (bool): Force refresh even if cache exists
        
        Returns:
            List[Dict]: List of user dictionaries if successful, None otherwise
        """
        # Check cache first
        if self.use_cache and not force_refresh:
            cached_data = self.cache.get()
            if cached_data:
                self.logger.info("📦 Using cached data")
                print("📦 Using cached data (use --no-cache to refresh)")
                self.users = cached_data
                return cached_data
        
        try:
            self.logger.info(f"Fetching data from {self.BASE_URL}")
            print("🔄 Fetching data from API...")
            
            # Apply rate limiting
            self._rate_limit()
            
            response = requests.get(self.BASE_URL, timeout=self.timeout)
            response.raise_for_status()
            
            users = response.json()
            
            if not users:
                self.logger.warning("API returned empty list")
                print("⚠️  Warning: API returned an empty list of users.")
                return None
            
            self.users = users
            
            # Cache the data
            if self.use_cache:
                self.cache.set(users)
                self.logger.info("Data cached successfully")
            
            self.logger.info(f"Successfully fetched {len(users)} users")
            print(f"✅ Successfully fetched {len(users)} users.\n")
            return users
            
        except requests.exceptions.Timeout:
            self.logger.error("Request timeout")
            print("❌ Error: Request timed out. Please check your internet connection.")
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error("Connection error")
            print("❌ Error: Failed to connect to the API. Please check your internet connection.")
            return None
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            print(f"❌ Error: HTTP error occurred: {e}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            print(f"❌ Error: An error occurred while fetching data: {e}")
            return None
        except ValueError as e:
            self.logger.error(f"JSON parse error: {e}")
            print("❌ Error: Failed to parse JSON response.")
            return None
    
    def display_users(self, users: List[Dict], filter_by_s: bool = False, 
                     format_type: str = 'pretty', limit: Optional[int] = None) -> None:
        """Display user information in various formats"""
        if not users:
            self.logger.warning("No users to display")
            print("⚠️  No users to display.")
            return
        
        # Filter users
        filtered_users = []
        for user in users:
            city = user.get('address', {}).get('city', 'N/A')
            if not filter_by_s or city.startswith('S'):
                filtered_users.append(user)
        
        if limit:
            filtered_users = filtered_users[:limit]
        
        if not filtered_users:
            self.logger.info("No users match filter criteria")
            print("ℹ️  No users found matching the criteria.")
            return
        
        self.logger.info(f"Displaying {len(filtered_users)} users in {format_type} format")
        
        # Display based on format
        if format_type == 'json':
            self._display_json(filtered_users)
        elif format_type == 'csv':
            self._display_csv(filtered_users)
        elif format_type == 'minimal':
            self._display_minimal(filtered_users)
        else:
            self._display_pretty(filtered_users)
    
    def _display_pretty(self, users: List[Dict]) -> None:
        """Display users in pretty formatted style"""
        for idx, user in enumerate(users, start=1):
            try:
                name = user.get('name', 'N/A')
                username = user.get('username', 'N/A')
                email = user.get('email', 'N/A')
                city = user.get('address', {}).get('city', 'N/A')
                phone = user.get('phone', 'N/A')
                company = user.get('company', {}).get('name', 'N/A')
                website = user.get('website', 'N/A')
                
                print(f"👤 User {idx}:")
                print(f"   Name:     {name}")
                print(f"   Username: {username}")
                print(f"   Email:    {email}")
                print(f"   City:     {city}")
                print(f"   Phone:    {phone}")
                print(f"   Company:  {company}")
                print(f"   Website:  {website}")
                print("─" * 60)
                
            except (KeyError, TypeError) as e:
                self.logger.warning(f"Error parsing user {idx}: {e}")
                print(f"⚠️  Warning: Could not parse user {idx} data: {e}")
    
    def _display_minimal(self, users: List[Dict]) -> None:
        """Display users in minimal style"""
        for idx, user in enumerate(users, start=1):
            try:
                print(f"User {idx}:")
                print(f"Name: {user.get('name', 'N/A')}")
                print(f"Username: {user.get('username', 'N/A')}")
                print(f"Email: {user.get('email', 'N/A')}")
                print(f"City: {user.get('address', {}).get('city', 'N/A')}")
                print("-" * 24)
            except (KeyError, TypeError) as e:
                self.logger.warning(f"Error parsing user {idx}: {e}")
    
    def _display_json(self, users: List[Dict]) -> None:
        """Display users in JSON format"""
        output = []
        for user in users:
            output.append({
                'name': user.get('name', 'N/A'),
                'username': user.get('username', 'N/A'),
                'email': user.get('email', 'N/A'),
                'city': user.get('address', {}).get('city', 'N/A'),
                'phone': user.get('phone', 'N/A'),
                'company': user.get('company', {}).get('name', 'N/A')
            })
        print(json.dumps(output, indent=2))
    
    def _display_csv(self, users: List[Dict]) -> None:
        """Display users in CSV format"""
        print("Name,Username,Email,City,Phone,Company")
        for user in users:
            name = user.get('name', 'N/A')
            username = user.get('username', 'N/A')
            email = user.get('email', 'N/A')
            city = user.get('address', {}).get('city', 'N/A')
            phone = user.get('phone', 'N/A')
            company = user.get('company', {}).get('name', 'N/A')
            print(f'"{name}","{username}","{email}","{city}","{phone}","{company}"')
    
    def get_statistics(self) -> None:
        """Display statistics about the fetched users"""
        if not self.users:
            print("⚠️  No users data available.")
            return
        
        self.logger.info("Generating statistics")
        print("\n📊 Statistics:")
        print(f"   Total Users: {len(self.users)}")
        
        # Count users by city
        cities = {}
        domains = {}
        
        for user in self.users:
            city = user.get('address', {}).get('city', 'Unknown')
            cities[city] = cities.get(city, 0) + 1
            
            # Email domain analysis
            email = user.get('email', '')
            if '@' in email:
                domain = email.split('@')[1]
                domains[domain] = domains.get(domain, 0) + 1
        
        print(f"   Unique Cities: {len(cities)}")
        
        # Cities starting with S
        s_cities = [city for city in cities.keys() if city.startswith('S')]
        print(f"   Cities starting with 'S': {len(s_cities)}")
        
        # Most common city
        if cities:
            most_common = max(cities.items(), key=lambda x: x[1])
            print(f"   Most common city: {most_common[0]} ({most_common[1]} users)")
        
        # Most common email domain
        if domains:
            most_common_domain = max(domains.items(), key=lambda x: x[1])
            print(f"   Most common email domain: {most_common_domain[0]} ({most_common_domain[1]} users)")
    
    def search_users(self, query: str, field: str = 'name') -> List[Dict]:
        """Search users by a specific field"""
        if not self.users:
            return []
        
        self.logger.info(f"Searching for '{query}' in field '{field}'")
        results = []
        
        for user in self.users:
            if field == 'city':
                value = user.get('address', {}).get('city', '').lower()
            else:
                value = user.get(field, '').lower()
            
            if query.lower() in value:
                results.append(user)
        
        self.logger.info(f"Found {len(results)} matching users")
        return results
    
    def save_to_file(self, filename: str, format_type: str = 'json') -> None:
        """Save users data to a file"""
        if not self.users:
            print("⚠️  No users data to save.")
            return
        
        try:
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            filepath = output_dir / filename
            
            if format_type == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.users, f, indent=2, ensure_ascii=False)
            elif format_type == 'csv':
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("Name,Username,Email,City,Phone,Company,Website\n")
                    for user in self.users:
                        name = user.get('name', 'N/A')
                        username = user.get('username', 'N/A')
                        email = user.get('email', 'N/A')
                        city = user.get('address', {}).get('city', 'N/A')
                        phone = user.get('phone', 'N/A')
                        company = user.get('company', {}).get('name', 'N/A')
                        website = user.get('website', 'N/A')
                        f.write(f'"{name}","{username}","{email}","{city}","{phone}","{company}","{website}"\n')
            
            self.logger.info(f"Data saved to {filepath}")
            print(f"✅ Data saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving file: {e}")
            print(f"❌ Error saving file: {e}")
    
    def clear_cache(self) -> None:
        """Clear the cache"""
        if self.cache:
            self.cache.clear()
            print("✅ Cache cleared successfully")
            self.logger.info("Cache cleared")


def print_header():
    """Print application header"""
    print("\n" + "=" * 70)
    print("        📋 USER DATA FETCHER v3.0 - Production Ready")
    print("=" * 70)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"⏰ Execution Time: {timestamp}")
    print("=" * 70 + "\n")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Fetch and display user data from JSONPlaceholder API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_users.py                              # Display all users
  python fetch_users.py --filter-s                   # Filter cities starting with 'S'
  python fetch_users.py --format json                # JSON output
  python fetch_users.py --limit 5 --stats            # Show 5 users + stats
  python fetch_users.py --search "New York"          # Search by city
  python fetch_users.py --save output.json           # Save to file
  python fetch_users.py --no-cache                   # Disable caching
  python fetch_users.py --clear-cache                # Clear cache
  python fetch_users.py --verbose                    # Verbose logging
        """
    )
    
    parser.add_argument('--filter-s', action='store_true',
                       help='Filter users whose city starts with "S"')
    parser.add_argument('--format', choices=['pretty', 'json', 'csv', 'minimal'],
                       default='pretty', help='Output format')
    parser.add_argument('--limit', type=int, help='Limit number of users to display')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--search', type=str, help='Search users')
    parser.add_argument('--search-field', choices=['name', 'username', 'email', 'city'],
                       default='name', help='Field to search in')
    parser.add_argument('--save', type=str, help='Save data to file')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout (seconds)')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    parser.add_argument('--clear-cache', action='store_true', help='Clear cache and exit')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    return parser.parse_args()


def main():
    """Main function"""
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(verbose=args.verbose)
    logger.info("Starting User Fetcher application")
    
    print_header()
    
    # Initialize fetcher
    fetcher = UserFetcher(
        timeout=args.timeout, 
        use_cache=not args.no_cache,
        logger=logger
    )
    
    # Handle cache clearing
    if args.clear_cache:
        fetcher.clear_cache()
        return
    
    # Fetch users
    users = fetcher.fetch_users()
    
    if users is None:
        logger.error("Failed to fetch users")
        sys.exit(1)
    
    # Handle search
    if args.search:
        print(f"\n🔍 Searching for '{args.search}' in {args.search_field}...\n")
        users = fetcher.search_users(args.search, args.search_field)
        if not users:
            print(f"❌ No users found matching '{args.search}'")
            logger.info(f"No search results for '{args.search}'")
            sys.exit(0)
        print(f"✅ Found {len(users)} matching user(s)\n")
    
    # Display users
    print("=" * 70)
    if args.filter_s:
        print("🏙️  USERS FROM CITIES STARTING WITH 'S'")
    else:
        print("👥 ALL USERS")
    print("=" * 70 + "\n")
    
    fetcher.display_users(users, filter_by_s=args.filter_s, 
                         format_type=args.format, limit=args.limit)
    
    # Show statistics
    if args.stats:
        fetcher.get_statistics()
    
    # Save to file
    if args.save:
        file_format = 'json' if args.save.endswith('.json') else 'csv'
        fetcher.save_to_file(args.save, file_format)
    
    print("\n" + "=" * 70)
    print("✅ Script execution completed successfully!")
    print("=" * 70 + "\n")
    
    logger.info("Application finished successfully")


if __name__ == "__main__":
    main()