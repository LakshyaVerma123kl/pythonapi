"""
API User Fetcher
This script fetches user data from JSONPlaceholder API and displays it in a formatted way.
Author: Lakshya Verma
Version: 2.0
"""

import requests
import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional


class UserFetcher:
    """Class to handle fetching and displaying user data from API"""
    
    BASE_URL = "https://jsonplaceholder.typicode.com/users"
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the UserFetcher.
        
        Args:
            timeout (int): Request timeout in seconds
        """
        self.timeout = timeout
        self.users = None
    
    def fetch_users(self) -> Optional[List[Dict]]:
        """
        Fetch users from the JSONPlaceholder API.
        
        Returns:
            List[Dict]: List of user dictionaries if successful, None otherwise
        """
        try:
            print("🔄 Fetching data from API...")
            response = requests.get(self.BASE_URL, timeout=self.timeout)
            
            # Check if the request was successful
            response.raise_for_status()
            
            users = response.json()
            
            # Check if the list is empty
            if not users:
                print("⚠️  Warning: API returned an empty list of users.")
                return None
            
            self.users = users
            print(f"✅ Successfully fetched {len(users)} users.\n")
            return users
            
        except requests.exceptions.Timeout:
            print("❌ Error: Request timed out. Please check your internet connection.")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Error: Failed to connect to the API. Please check your internet connection.")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error: HTTP error occurred: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: An error occurred while fetching data: {e}")
            return None
        except ValueError:
            print("❌ Error: Failed to parse JSON response.")
            return None
    
    def display_users(self, users: List[Dict], filter_by_s: bool = False, 
                     format_type: str = 'pretty', limit: Optional[int] = None) -> None:
        """
        Display user information in various formats.
        
        Args:
            users (List[Dict]): List of user dictionaries
            filter_by_s (bool): If True, only display users whose city starts with 'S'
            format_type (str): Output format - 'pretty', 'json', 'csv', or 'minimal'
            limit (int): Maximum number of users to display
        """
        if not users:
            print("⚠️  No users to display.")
            return
        
        # Filter users if needed
        filtered_users = []
        for user in users:
            city = user.get('address', {}).get('city', 'N/A')
            if not filter_by_s or city.startswith('S'):
                filtered_users.append(user)
        
        # Apply limit if specified
        if limit:
            filtered_users = filtered_users[:limit]
        
        if not filtered_users:
            print("ℹ️  No users found matching the criteria.")
            return
        
        # Display based on format type
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
                
                print(f"👤 User {idx}:")
                print(f"   Name:     {name}")
                print(f"   Username: {username}")
                print(f"   Email:    {email}")
                print(f"   City:     {city}")
                print(f"   Phone:    {phone}")
                print(f"   Company:  {company}")
                print("─" * 50)
                
            except (KeyError, TypeError) as e:
                print(f"⚠️  Warning: Could not parse user {idx} data: {e}")
                continue
    
    def _display_minimal(self, users: List[Dict]) -> None:
        """Display users in minimal style (original format)"""
        for idx, user in enumerate(users, start=1):
            try:
                name = user.get('name', 'N/A')
                username = user.get('username', 'N/A')
                email = user.get('email', 'N/A')
                city = user.get('address', {}).get('city', 'N/A')
                
                print(f"User {idx}:")
                print(f"Name: {name}")
                print(f"Username: {username}")
                print(f"Email: {email}")
                print(f"City: {city}")
                print("-" * 24)
                
            except (KeyError, TypeError) as e:
                print(f"⚠️  Warning: Could not parse user {idx} data: {e}")
                continue
    
    def _display_json(self, users: List[Dict]) -> None:
        """Display users in JSON format"""
        output = []
        for user in users:
            output.append({
                'name': user.get('name', 'N/A'),
                'username': user.get('username', 'N/A'),
                'email': user.get('email', 'N/A'),
                'city': user.get('address', {}).get('city', 'N/A')
            })
        print(json.dumps(output, indent=2))
    
    def _display_csv(self, users: List[Dict]) -> None:
        """Display users in CSV format"""
        print("Name,Username,Email,City")
        for user in users:
            name = user.get('name', 'N/A')
            username = user.get('username', 'N/A')
            email = user.get('email', 'N/A')
            city = user.get('address', {}).get('city', 'N/A')
            print(f'"{name}","{username}","{email}","{city}"')
    
    def get_statistics(self) -> None:
        """Display statistics about the fetched users"""
        if not self.users:
            print("⚠️  No users data available.")
            return
        
        print("\n📊 Statistics:")
        print(f"   Total Users: {len(self.users)}")
        
        # Count users by city
        cities = {}
        for user in self.users:
            city = user.get('address', {}).get('city', 'Unknown')
            cities[city] = cities.get(city, 0) + 1
        
        print(f"   Unique Cities: {len(cities)}")
        
        # Cities starting with S
        s_cities = [city for city in cities.keys() if city.startswith('S')]
        print(f"   Cities starting with 'S': {len(s_cities)}")
        
        # Most common city
        if cities:
            most_common = max(cities.items(), key=lambda x: x[1])
            print(f"   Most common city: {most_common[0]} ({most_common[1]} users)")
    
    def search_users(self, query: str, field: str = 'name') -> List[Dict]:
        """
        Search users by a specific field.
        
        Args:
            query (str): Search query
            field (str): Field to search in ('name', 'username', 'email', 'city')
        
        Returns:
            List[Dict]: List of matching users
        """
        if not self.users:
            return []
        
        results = []
        for user in self.users:
            if field == 'city':
                value = user.get('address', {}).get('city', '').lower()
            else:
                value = user.get(field, '').lower()
            
            if query.lower() in value:
                results.append(user)
        
        return results
    
    def save_to_file(self, filename: str, format_type: str = 'json') -> None:
        """
        Save users data to a file.
        
        Args:
            filename (str): Output filename
            format_type (str): File format ('json' or 'csv')
        """
        if not self.users:
            print("⚠️  No users data to save.")
            return
        
        try:
            if format_type == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.users, f, indent=2, ensure_ascii=False)
            elif format_type == 'csv':
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("Name,Username,Email,City,Phone,Company\n")
                    for user in self.users:
                        name = user.get('name', 'N/A')
                        username = user.get('username', 'N/A')
                        email = user.get('email', 'N/A')
                        city = user.get('address', {}).get('city', 'N/A')
                        phone = user.get('phone', 'N/A')
                        company = user.get('company', {}).get('name', 'N/A')
                        f.write(f'"{name}","{username}","{email}","{city}","{phone}","{company}"\n')
            
            print(f"✅ Data saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")


def print_header():
    """Print application header"""
    print("\n" + "=" * 60)
    print("        📋 USER DATA FETCHER v2.0")
    print("=" * 60)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"⏰ Execution Time: {timestamp}")
    print("=" * 60 + "\n")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Fetch and display user data from JSONPlaceholder API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_users.py                          # Display all users (pretty format)
  python fetch_users.py --filter-s               # Show only users from cities starting with 'S'
  python fetch_users.py --format json            # Output in JSON format
  python fetch_users.py --limit 5                # Show only first 5 users
  python fetch_users.py --stats                  # Show statistics
  python fetch_users.py --search "New York"      # Search users by city
  python fetch_users.py --save output.json       # Save data to file
        """
    )
    
    parser.add_argument('--filter-s', action='store_true',
                       help='Filter users whose city starts with "S"')
    parser.add_argument('--format', choices=['pretty', 'json', 'csv', 'minimal'],
                       default='pretty', help='Output format (default: pretty)')
    parser.add_argument('--limit', type=int, help='Limit number of users to display')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--search', type=str, help='Search users by name, username, or email')
    parser.add_argument('--search-field', choices=['name', 'username', 'email', 'city'],
                       default='name', help='Field to search in (default: name)')
    parser.add_argument('--save', type=str, help='Save data to file (JSON or CSV)')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Request timeout in seconds (default: 10)')
    
    return parser.parse_args()


def main():
    """Main function to run the script"""
    args = parse_arguments()
    
    print_header()
    
    # Initialize fetcher
    fetcher = UserFetcher(timeout=args.timeout)
    
    # Fetch users
    users = fetcher.fetch_users()
    
    if users is None:
        sys.exit(1)
    
    # Handle search
    if args.search:
        print(f"\n🔍 Searching for '{args.search}' in {args.search_field}...\n")
        users = fetcher.search_users(args.search, args.search_field)
        if not users:
            print(f"❌ No users found matching '{args.search}'")
            sys.exit(0)
        print(f"✅ Found {len(users)} matching user(s)\n")
    
    # Display users
    print("=" * 60)
    if args.filter_s:
        print("🏙️  USERS FROM CITIES STARTING WITH 'S'")
    else:
        print("👥 ALL USERS")
    print("=" * 60 + "\n")
    
    fetcher.display_users(users, filter_by_s=args.filter_s, 
                         format_type=args.format, limit=args.limit)
    
    # Show statistics if requested
    if args.stats:
        fetcher.get_statistics()
    
    # Save to file if requested
    if args.save:
        file_format = 'json' if args.save.endswith('.json') else 'csv'
        fetcher.save_to_file(args.save, file_format)
    
    print("\n" + "=" * 60)
    print("✅ Script execution completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()