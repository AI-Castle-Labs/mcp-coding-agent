import requests
from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Try to load from mcp-coding-agent/.env
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

from velocity_agent import VelocityComplexityAgent, print_velocity_complexity_score
from discord_pr_bot import run_discord_analyzer


class githubanalyzer:

    def __init__(self):
        # Use environment variable for security (never hardcode tokens in source code)
        self.token = os.environ.get("GITHUB_TOKEN", "")
        
        self.base_url = "https://api.github.com"
        self.owner = "AgenticAI-UIUC"
        self.days = 7
        self.reponame = ["agentic-ai-music-recommendation-system","agentic-ai-sports-analyst","agentic-ai-equity-analyst","agentic-ai-healthcare-search","agentic-ai-portfolio-manager"]

        self.developer_names = {"cyn-clical":"william yuan"}
        
        # GitHub API now prefers "Bearer" over "token" for authentication
        auth_header = ""
        if self.token:
            # Check if token starts with ghp_ (personal access token), ghs_ (fine-grained token), or github_pat_ (fine-grained PAT)
            if self.token.startswith(("ghp_", "ghs_", "github_pat_")):
                auth_header = f"Bearer {self.token}"
            else:
                # Legacy format for older tokens
                auth_header = f"token {self.token}"
        
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": auth_header
        }
        self.now = datetime.utcnow()
        self.threshold_date = self.now - timedelta(days=self.days)
        self.threshold_str = self.threshold_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        self.date_format = "%Y-%m-%dT%H:%M:%SZ"



    def get_commits(self):
        
        params = {
            "since": self.threshold_str,
            "per_page": 100
        }
        page = 1

        all_commits = []
        author_commits = {}
        
        for repo in self.reponame:
            page = 1
            while True:
                params['page'] = page
                url = f"{self.base_url}/repos/{self.owner}/{repo}/commits"
                
                try:
                    response = requests.get(url, headers=self.headers, params=params)
                    response.raise_for_status()
                    
                    commits = response.json()
                    
                    if not commits:
                        break
                    
                    for commit in commits:
                        author = commit['commit']['author']['name']
                        if author not in author_commits:
                            author_commits[author] = 0
                        author_commits[author] += 1
                    
                    all_commits.extend(commits)
                    
                    # Check if we've reached the last page by checking the Link header
                    if 'Link' in response.headers and 'rel="next"' not in response.headers['Link']:
                        break
                    
                    page += 1
                    
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching commits from {repo}: {e}")
                    break

        top_5_authors = sorted(author_commits.items(), key=lambda x: x[1], reverse=True)[:5]

        return top_5_authors
    
    def get_pull_requests(self):
        """
        Retrieve pull requests from the repository that were created or updated 
        within the specified number of days.
        
        Returns:
            list: A list of pull request objects containing PR details
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.reponame}/pulls"
        params = {
            "state": "all",  # Get all PRs: open, closed, and merged
            "sort": "updated",  # Sort by last updated
            "direction": "desc",  # Most recent first
            "per_page": 100
        }
        page = 1
        all_prs = []
        
        while True:
            params['page'] = page
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                prs = response.json()
                
                if not prs:
                    break
                
                # Filter PRs by date - keep only those updated after our threshold date
                recent_prs = []
                for pr in prs:
                    updated_at = datetime.strptime(pr['updated_at'], self.date_format)
                    if updated_at >= self.threshold_date:
                        recent_prs.append(pr)
                    else:
                        # Since PRs are sorted by updated date, once we find an old one,
                        # we can stop checking the rest
                        break
                
                if not recent_prs:
                    break
                    
                all_prs.extend(recent_prs)
                
                # Check if we've reached the last page by checking the Link header
                if 'Link' in response.headers and 'rel="next"' not in response.headers['Link']:
                    break
                    
                page += 1
            except requests.exceptions.RequestException as e:
                print(f"Error fetching pull requests: {e}")
                break
        
        return all_prs
    
    def get_pr_details(self, pr_number):
        """
        Get detailed information about a specific pull request including reviews and commits
        
        Args:
            pr_number (int): Pull request number
            
        Returns:
            dict: Dictionary containing PR details, commits, and reviews
        """
        pr_url = f"{self.base_url}/repos/{self.owner}/{self.reponame}/pulls/{pr_number}"
        commits_url = f"{self.base_url}/repos/{self.owner}/{self.reponame}/pulls/{pr_number}/commits"
        reviews_url = f"{self.base_url}/repos/{self.owner}/{self.reponame}/pulls/{pr_number}/reviews"
        comments_url = f"{self.base_url}/repos/{self.owner}/{self.reponame}/pulls/{pr_number}/comments"
        
        try:
            # Get PR details
            pr_response = requests.get(pr_url, headers=self.headers)
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            
            # Get commits in this PR
            commits_response = requests.get(commits_url, headers=self.headers)
            commits_response.raise_for_status()
            commits_data = commits_response.json()
            
            # Get reviews for this PR
            reviews_response = requests.get(reviews_url, headers=self.headers)
            reviews_response.raise_for_status()
            reviews_data = reviews_response.json()
            
            # Get review comments for this PR
            comments_response = requests.get(comments_url, headers=self.headers)
            comments_response.raise_for_status()
            comments_data = comments_response.json()
            
            return {
                "pull_request": pr_data,
                "commits": commits_data,
                "reviews": reviews_data,
                "comments": comments_data
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PR details for PR #{pr_number}: {e}")
            return None
    
    def get_weekly_pr_numbers(self, detailed=False):
        """
        Extract PR numbers for PRs updated in the specified time period
        
        Args:
            detailed (bool): If True, return detailed information about each PR
                            If False, return just the PR numbers
        
        Returns:
            If detailed=False: list of PR numbers
            If detailed=True: list of dicts with PR number, title, state, author, dates
        """
        prs = self.get_pull_requests()
        
        if not detailed:
            return [pr['number'] for pr in prs]
        
        result = []
        for pr in prs:
            try:
                created_date = datetime.strptime(pr['created_at'], self.date_format)
                updated_date = datetime.strptime(pr['updated_at'], self.date_format)
                
                # Determine if PR is merged
                merged_status = "merged" if pr.get('merged_at') else pr['state']
                
                pr_info = {
                    "number": pr['number'],
                    "title": pr['title'],
                    "state": merged_status,
                    "author": pr['user']['login'],
                    "created_at": created_date,
                    "updated_at": updated_date,
                    "created_at_str": created_date.strftime('%Y-%m-%d'),
                    "updated_at_str": updated_date.strftime('%Y-%m-%d')
                }
                
                result.append(pr_info)
            except (KeyError, ValueError) as e:
                print(f"Error processing PR: {e}")
                
        return result
    
    def get_pr_numbers_by_date_range(self, start_date=None, end_date=None):
        """
        Extract PR numbers for a custom date range
        
        Args:
            start_date (str): Start date in 'YYYY-MM-DD' format (inclusive)
                             If None, no lower bound is applied
            end_date (str): End date in 'YYYY-MM-DD' format (inclusive)
                           If None, no upper bound is applied
        
        Returns:
            list: List of PR numbers that were updated in the date range
        """
        # Save current threshold date
        original_threshold = self.threshold_date
        original_threshold_str = self.threshold_str
        
        try:
            # Set custom date range if provided
            if start_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                self.threshold_date = start_date_obj
                self.threshold_str = start_date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Get PRs for this time period
            prs = self.get_pull_requests()
            
            # Filter by end date if provided
            if end_date:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
                prs = [pr for pr in prs if datetime.strptime(pr['updated_at'], self.date_format) <= end_date_obj]
            
            return [pr['number'] for pr in prs]
            
        finally:
            # Restore original threshold
            self.threshold_date = original_threshold
            self.threshold_str = original_threshold_str
        
    def get_pr_code_changes(self, pr_number):
        """
        Get the actual code changes (diff) for a specific pull request
        
        Args:
            pr_number (int): Pull request number
            
        Returns:
            dict: Dictionary containing file changes, with changed files and their diffs
        """
        # URL for the pull request files endpoint
        files_url = f"{self.base_url}/repos/{self.owner}/{self.reponame}/pulls/{pr_number}/files"
        
        try:
            # Special header to get the diff content
            headers = self.headers.copy()
            headers["Accept"] = "application/vnd.github.v3.diff"
            
            # First, get the list of files changed in the PR
            response = requests.get(files_url, headers=self.headers)
            response.raise_for_status()
            files_data = response.json()
            
            # Get the raw diff for each file
            result = {
                "total_files_changed": len(files_data),
                "total_additions": sum(f.get('additions', 0) for f in files_data),
                "total_deletions": sum(f.get('deletions', 0) for f in files_data),
                "files": []
            }
            
            # Process each file
            for file_info in files_data:
                file_data = {
                    "filename": file_info.get('filename'),
                    "status": file_info.get('status'),  # added, modified, removed
                    "additions": file_info.get('additions', 0),
                    "deletions": file_info.get('deletions', 0),
                    "changes": file_info.get('changes', 0)
                }
                
                # Get the patch/diff if available
                if 'patch' in file_info:
                    file_data['diff'] = file_info['patch']
                else:
                    file_data['diff'] = "(Binary file or diff too large)"
                    
                result["files"].append(file_data)
                
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching code changes for PR #{pr_number}: {e}")
            return None

    def get_file_content(self, repo_name: str, file_path: str, branch: str = "main") -> Optional[str]:
        """
        Get the content of a file from a GitHub repository.
        
        Args:
            repo_name: Name of the repository
            file_path: Path to the file in the repository (e.g., "src/main.py")
            branch: Branch name (default: "main")
            
        Returns:
            File content as string, or None if error
        """
        # #region agent log
        import json
        with open('/Users/ash/Desktop/RAGUIUC/internal-dev-tasks/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A,B,C,D,E","location":"devanalyzer.py:337","message":"get_file_content entry","data":{"repo_name":repo_name,"file_path":file_path,"branch":branch},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        
        url = f"{self.base_url}/repos/{self.owner}/{repo_name}/contents/{file_path}"
        params = {"ref": branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            # #region agent log
            with open('/Users/ash/Desktop/RAGUIUC/internal-dev-tasks/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"devanalyzer.py:343","message":"HTTP response status","data":{"status_code":response.status_code,"headers":dict(response.headers)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            # #endregion
            
            # Check for authentication errors
            if response.status_code == 401:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("message", "Unauthorized")
                print(f"\n❌ Authentication Error (401) when fetching {file_path}: {error_msg}")
                print("Please verify your GITHUB_TOKEN is valid and has the required permissions.")
                return None
            
            response.raise_for_status()
            file_data = response.json()
            
            # #region agent log
            with open('/Users/ash/Desktop/RAGUIUC/internal-dev-tasks/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A,B,C","location":"devanalyzer.py:348","message":"file_data parsed","data":{"type":file_data.get("type"),"encoding":file_data.get("encoding"),"size":file_data.get("size"),"has_content":("content" in file_data),"content_length":len(str(file_data.get("content",""))[:100]) if file_data.get("content") else 0},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            # #endregion
            
            # GitHub API returns base64 encoded content
            if file_data.get("encoding") == "base64":
                import base64
                
                # #region agent log
                with open('/Users/ash/Desktop/RAGUIUC/internal-dev-tasks/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"devanalyzer.py:353","message":"before base64 decode","data":{"content_exists":("content" in file_data),"content_type":type(file_data.get("content")).__name__},"timestamp":int(__import__('time').time()*1000)}) + '\n')
                # #endregion
                
                content = base64.b64decode(file_data["content"]).decode("utf-8")
                
                # #region agent log
                with open('/Users/ash/Desktop/RAGUIUC/internal-dev-tasks/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A,E","location":"devanalyzer.py:358","message":"after decode success","data":{"decoded_length":len(content)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
                # #endregion
                
                return content
            else:
                # #region agent log
                with open('/Users/ash/Desktop/RAGUIUC/internal-dev-tasks/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"devanalyzer.py:363","message":"non-base64 encoding path","data":{"encoding":file_data.get("encoding"),"returning_content":bool(file_data.get("content"))},"timestamp":int(__import__('time').time()*1000)}) + '\n')
                # #endregion
                
                return file_data.get("content", "")
        except requests.exceptions.RequestException as e:
            # #region agent log
            with open('/Users/ash/Desktop/RAGUIUC/internal-dev-tasks/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B,D","location":"devanalyzer.py:370","message":"RequestException caught","data":{"error_type":type(e).__name__,"error_msg":str(e)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            # #endregion
            
            print(f"Error fetching file {file_path} from {repo_name}: {e}")
            return None
        except (KeyError, TypeError, UnicodeDecodeError, Exception) as e:
            # #region agent log
            with open('/Users/ash/Desktop/RAGUIUC/internal-dev-tasks/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C,E","location":"devanalyzer.py:377","message":"unexpected exception","data":{"error_type":type(e).__name__,"error_msg":str(e)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            # #endregion
            
            print(f"Unexpected error processing file {file_path} from {repo_name}: {e}")
            return None
    
    def get_repo_files(self, repo_name: str, path: str = "", branch: str = "main", file_extension: str = ".py") -> List[Dict[str, Any]]:
        """
        Get list of files from a GitHub repository, optionally filtered by extension.
        
        Args:
            repo_name: Name of the repository
            path: Directory path in repo (empty for root)
            branch: Branch name (default: "main")
            file_extension: Filter by file extension (e.g., ".py")
            
        Returns:
            List of file info dicts with 'path', 'name', 'type', etc.
        """
        url = f"{self.base_url}/repos/{self.owner}/{repo_name}/contents/{path}"
        params = {"ref": branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            # Check for authentication errors
            if response.status_code == 401:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("message", "Unauthorized")
                print(f"\n❌ Authentication Error (401) when fetching files from {repo_name}/{path}: {error_msg}")
                print("\nPossible causes:")
                print("1. GITHUB_TOKEN is not set or is invalid")
                print("2. Token has expired")
                print("3. Token doesn't have required permissions (needs 'repo' scope)")
                print("4. Repository is private and token doesn't have access")
                print("\nTo fix:")
                print("- Verify your GITHUB_TOKEN is set: echo $GITHUB_TOKEN")
                print("- Generate a new token at: https://github.com/settings/tokens")
                print("- Ensure token has 'repo' scope for private repos or 'public_repo' for public repos")
                return []
            
            response.raise_for_status()
            items = response.json()
            
            files = []
            for item in items:
                if item.get("type") == "file" and item.get("name", "").endswith(file_extension):
                    files.append({
                        "path": item.get("path"),
                        "name": item.get("name"),
                        "size": item.get("size"),
                        "url": item.get("download_url"),
                    })
                elif item.get("type") == "dir":
                    # Recursively get files from subdirectories
                    sub_files = self.get_repo_files(repo_name, item.get("path"), branch, file_extension)
                    files.extend(sub_files)
            
            return files
        except requests.exceptions.RequestException as e:
            print(f"Error fetching files from {repo_name}/{path}: {e}")
            return []

    def get_author_pr_activity(self, author_login, days=30):
        """
        Fetch PRs created or updated by a specific author within a time window.

        Args:
            author_login (str): GitHub login for the author.
            days (int): Lookback window in days.

        Returns:
            list: PR objects created by the author in the window.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        author_prs = []

        for repo in self.reponame:
            page = 1
            while True:
                params = {
                    "state": "all",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": 100,
                    "page": page,
                }
                url = f"{self.base_url}/repos/{self.owner}/{repo}/pulls"
                try:
                    response = requests.get(url, headers=self.headers, params=params)
                    response.raise_for_status()
                    prs = response.json()

                    if not prs:
                        break

                    for pr in prs:
                        updated_at = datetime.strptime(pr["updated_at"], self.date_format)
                        if updated_at < cutoff:
                            # PR list is sorted by updated date; safe to break early.
                            prs = []
                            break
                        if pr.get("user", {}).get("login") == author_login:
                            author_prs.append(pr)

                    if not prs:
                        break

                    link_header = response.headers.get("Link", "")
                    if 'rel="next"' not in link_header:
                        break
                    page += 1
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching PR activity for {author_login} in {repo}: {e}")
                    break

        return author_prs
    
    def analyze_pull_requests(self, pull_requests):
        """
        Analyze pull requests and provide statistics
        
        Args:
            pull_requests (list): List of pull request objects
            
        Returns:
            dict: Dictionary containing PR statistics
        """
        total_prs = len(pull_requests)
        if total_prs == 0:
            return {
                "total": 0,
                "merged": 0,
                "open": 0,
                "closed_without_merge": 0,
                "avg_time_to_merge": None,
                "avg_comments": 0,
                "avg_commits": 0
            }
        
        merged_prs = []
        open_prs = []
        closed_without_merge = []
        
        for pr in pull_requests:
            if pr.get('merged_at'):
                merged_prs.append(pr)
            elif pr['state'] == 'open':
                open_prs.append(pr)
            else:
                closed_without_merge.append(pr)
        
        # Calculate average time to merge
        merge_times = []
        for pr in merged_prs:
            created_at = datetime.strptime(pr['created_at'], self.date_format)
            merged_at = datetime.strptime(pr['merged_at'], self.date_format)
            merge_time = merged_at - created_at
            merge_times.append(merge_time.total_seconds())
        
        avg_merge_time = sum(merge_times) / len(merge_times) if merge_times else None
        
        # Get more detailed information for each PR
        commits_counts = []
        comments_counts = []
        
        for pr in pull_requests:
            # We'll get details for a few PRs to avoid making too many API requests
            if len(commits_counts) < 5:  # Limit to avoid too many API calls
                pr_details = self.get_pr_details(pr['number'])
                if pr_details:
                    commits_counts.append(len(pr_details['commits']))
                    comments_counts.append(len(pr_details['comments']) + len(pr_details['reviews']))
        
        avg_commits = sum(commits_counts) / len(commits_counts) if commits_counts else 0
        avg_comments = sum(comments_counts) / len(comments_counts) if comments_counts else 0
        
        return {
            "total": total_prs,
            "merged": len(merged_prs),
            "open": len(open_prs),
            "closed_without_merge": len(closed_without_merge),
            "avg_time_to_merge_seconds": avg_merge_time,
            "avg_time_to_merge_hours": avg_merge_time / 3600 if avg_merge_time else None,
            "avg_commits": avg_commits,
            "avg_comments": avg_comments,
        }

    def get_contribution_summary(self):
        """
        Get a summary of contributions per person from commits and PRs

        Returns:
            dict: Dictionary with contribution statistics per person
        """
        # Get commits and PRs
        commits = self.get_commits()
        prs = self.get_pull_requests()

        # Initialize contribution tracking
        contributions = {}

        # Process commits
        for commit in commits:
            author = commit['commit']['author']['name']
            if author not in contributions:
                contributions[author] = {
                    'commits': 0,
                    'prs_created': 0,
                    'prs_reviewed': 0,
                    'lines_added': 0,
                    'lines_deleted': 0,
                    'files_changed': set()
                }
            contributions[author]['commits'] += 1

            # Try to get commit stats if available
            try:
                commit_url = commit['url']
                response = requests.get(commit_url, headers=self.headers)
                if response.status_code == 200:
                    commit_data = response.json()
                    stats = commit_data.get('stats', {})
                    contributions[author]['lines_added'] += stats.get('additions', 0)
                    contributions[author]['lines_deleted'] += stats.get('deletions', 0)

                    # Track files changed
                    files = commit_data.get('files', [])
                    for file in files:
                        contributions[author]['files_changed'].add(file['filename'])
            except:
                pass  # Skip if we can't get detailed stats

        # Process PRs
        for pr in prs:
            author = pr['user']['login']
            if author not in contributions:
                contributions[author] = {
                    'commits': 0,
                    'prs_created': 0,
                    'prs_reviewed': 0,
                    'lines_added': 0,
                    'lines_deleted': 0,
                    'files_changed': set()
                }
            contributions[author]['prs_created'] += 1

            # Get PR details to count reviews and more stats
            pr_details = self.get_pr_details(pr['number'])
            if pr_details:
                # Count reviews by this author on other PRs
                for review in pr_details.get('reviews', []):
                    reviewer = review['user']['login']
                    if reviewer in contributions:
                        contributions[reviewer]['prs_reviewed'] += 1
                    elif reviewer:
                        contributions[reviewer] = {
                            'commits': 0,
                            'prs_created': 0,
                            'prs_reviewed': 1,
                            'lines_added': 0,
                            'lines_deleted': 0,
                            'files_changed': set()
                        }

                # Add PR code changes to author's stats
                pr_changes = self.get_pr_code_changes(pr['number'])
                if pr_changes:
                    for file in pr_changes.get('files', []):
                        contributions[author]['lines_added'] += file.get('additions', 0)
                        contributions[author]['lines_deleted'] += file.get('deletions', 0)
                        contributions[author]['files_changed'].add(file.get('filename'))

        # Convert sets to counts and calculate totals
        summary = {}
        for person, stats in contributions.items():
            summary[person] = {
                'commits': stats['commits'],
                'prs_created': stats['prs_created'],
                'prs_reviewed': stats['prs_reviewed'],
                'lines_added': stats['lines_added'],
                'lines_deleted': stats['lines_deleted'],
                'files_changed_count': len(stats['files_changed']),
                'total_contributions': stats['commits'] + stats['prs_created'] + stats['prs_reviewed']
            }

        return summary

    def analyze_pr_value(self, pr_number):
        """Analyze a PR to determine if it adds value to the codebase."""
        # Simple implementation - returns basic analysis
        pr_details = self.get_pr_details(pr_number)
        if not pr_details:
            return {"error": "Could not fetch PR details"}

        pr_changes = self.get_pr_code_changes(pr_number)
        if not pr_changes:
            return {"error": "Could not fetch PR changes"}

        # Calculate a simple score based on basic metrics
        score = 50  # Base score
        if pr_changes['total_additions'] > 0:
            score += 10  # Adding code is generally good
        if any('test' in f['filename'].lower() for f in pr_changes['files']):
            score += 20  # Tests are valuable
        if pr_changes['total_files_changed'] > 10:
            score -= 10  # Too many files might be concerning

        return {
            'pr_number': pr_number,
            'score': min(score, 100),
            'summary': f"PR #{pr_number} has a value score of {score}/100 based on code changes and test coverage."
        }


def print_pr_code_changes(pr_changes):
    """Helper function to pretty print PR code changes"""
    if not pr_changes:
        print("No code changes available or error fetching changes.")
        return
        
    print(f"\n=== CODE CHANGES ({pr_changes['total_files_changed']} files) ===")
    print(f"Total: +{pr_changes['total_additions']} -{pr_changes['total_deletions']}")
    
    for file in pr_changes['files']:
        print(f"\n--- {file['filename']} ({file['status']}) ---")
        print(f"+{file['additions']} -{file['deletions']} changes")
        
        if 'diff' in file:
            # Format the diff output with proper indentation
            diff_lines = file['diff'].split('\n')
            for line in diff_lines:
                if line.startswith('+') and not line.startswith('+++'):
                    print(f"\033[92m{line}\033[0m")  # Green for additions
                elif line.startswith('-') and not line.startswith('---'):
                    print(f"\033[91m{line}\033[0m")  # Red for deletions
                else:
                    print(f"  {line}")


if __name__ == "__main__":
    analyzer = githubanalyzer()
    
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1:
        # Help menu
        if sys.argv[1] in ["--help", "-h"]:
            print("\nDevAnalyzer - GitHub Repository Analysis Tool")
            print("\nUsage:")
            print("  python devanalyzer.py                     - Show full repository analysis")
            print("  python devanalyzer.py <PR_NUMBER>         - Show details for a specific PR")
            print("  python devanalyzer.py --numbers, -n       - List PR numbers for the week")
            print("  python devanalyzer.py --numbers --detailed - List PR numbers with details")
            print("  python devanalyzer.py --numbers --export   - Export PR numbers to a file")
            print("  python devanalyzer.py --date-range <start> <end> - PR numbers for date range (YYYY-MM-DD)")
            print("  python devanalyzer.py --contributions      - Show contribution summary per person")
            print("  python devanalyzer.py --score-volume-complexity <PR_NUMBER> - Score PR velocity/complexity")
            print("  python devanalyzer.py --analyze-pr <PR_NUMBER> - Analyze PR value and get score")
            print("  python devanalyzer.py --discord-analyze <PR_NUMBER> - Analyze PR and post to Discord")
            print("  python devanalyzer.py --discord-analyze-all - Analyze all weekly PRs and post to Discord")
            sys.exit(0)
            
        # Discord PR analysis for a specific PR
        elif sys.argv[1] == "--discord-analyze" and len(sys.argv) > 2 and sys.argv[2].isdigit():
            pr_number = int(sys.argv[2])
            print(f"Analyzing PR #{pr_number} and posting to Discord...")
            asyncio.run(run_discord_analyzer(analyzer, [pr_number]))
            sys.exit(0)
            
        # Discord PR analysis for all weekly PRs
        elif sys.argv[1] == "--discord-analyze-all":
            pr_numbers = analyzer.get_weekly_pr_numbers()
            if not pr_numbers:
                print("No PRs found in the last week.")
                sys.exit(0)
            print(f"Analyzing {len(pr_numbers)} PRs and posting to Discord...")
            asyncio.run(run_discord_analyzer(analyzer, pr_numbers))
            sys.exit(0)

        # Show contribution summary per person
        elif sys.argv[1] == "--contributions":
            print(f"\n=== CONTRIBUTION SUMMARY FOR THE LAST {analyzer.days} DAYS ===")
            print(f"Repository: {analyzer.owner}/{analyzer.reponame}\n")

            contributions = analyzer.get_contribution_summary()

            if not contributions:
                print("No contributions found in the specified time period.")
                sys.exit(0)

            # Sort by total contributions (descending)
            sorted_contributions = sorted(contributions.items(),
                                        key=lambda x: x[1]['total_contributions'],
                                        reverse=True)

            print(f"{'Contributor':<20} {'Commits':<8} {'PRs':<5} {'Reviews':<8} {'Lines +':<8} {'Lines -':<8} {'Files':<6} {'Total':<6}")
            print("-" * 85)

            for person, stats in sorted_contributions:
                print(f"{person:<20} {stats['commits']:<8} {stats['prs_created']:<5} {stats['prs_reviewed']:<8} {stats['lines_added']:<8} {stats['lines_deleted']:<8} {stats['files_changed_count']:<6} {stats['total_contributions']:<6}")

            print(f"\nTotal contributors: {len(contributions)}")
            total_commits = sum(stats['commits'] for stats in contributions.values())
            total_prs = sum(stats['prs_created'] for stats in contributions.values())
            total_reviews = sum(stats['prs_reviewed'] for stats in contributions.values())
            print(f"Total commits: {total_commits}")
            print(f"Total PRs created: {total_prs}")
            print(f"Total PR reviews: {total_reviews}")

            sys.exit(0)

        # Velocity/complexity scoring
        elif sys.argv[1] == "--score-volume-complexity" and len(sys.argv) > 2 and sys.argv[2].isdigit():
            pr_number = int(sys.argv[2])
            agent = VelocityComplexityAgent(analyzer)
            result = agent.score_pr(pr_number)
            print_velocity_complexity_score(result)
            sys.exit(0)

            # Analyze PR value
        elif sys.argv[1] == "--analyze-pr" and len(sys.argv) > 2 and sys.argv[2].isdigit():
            pr_number = int(sys.argv[2])
            print(f"\n=== ANALYZING PR #{pr_number} FOR VALUE ===\n")

            analysis = analyzer.analyze_pr_value(pr_number)

            if 'error' in analysis:
                print(f"Error: {analysis['error']}")
                sys.exit(1)

            print(f"PR #{analysis['pr_number']}: {analysis.get('title', 'Unknown')}")
            print(f"Author: {analysis.get('author', 'Unknown')}")
            print(f"Score: {analysis['score']}/100")
            print(f"Summary: {analysis['summary']}")

            sys.exit(0)

        # Option to list only PR numbers for the week
        elif sys.argv[1] == "--numbers" or sys.argv[1] == "-n":
            detailed = "--detailed" in sys.argv or "-d" in sys.argv
            export = "--export" in sys.argv or "-e" in sys.argv
            
            if detailed:
                pr_data = analyzer.get_weekly_pr_numbers(detailed=True)
                print(f"\n=== DETAILED PR INFO FOR THE LAST {analyzer.days} DAYS ===")
                if pr_data:
                    # Create a nicely formatted table
                    print(f"{'Number':<7} {'State':<10} {'Created':<12} {'Updated':<12} {'Author':<15} Title")
                    print("-" * 80)
                    for pr in pr_data:
                        print(f"{pr['number']:<7} {pr['state']:<10} {pr['created_at_str']:<12} "
                              f"{pr['updated_at_str']:<12} {pr['author']:<15} {pr['title']}")
                    
                    print(f"\nTotal: {len(pr_data)} pull requests")
                    
                    # Export to file if requested
                    if export:
                        import json
                        filename = f"pr_details_{datetime.now().strftime('%Y%m%d')}.json"
                        with open(filename, "w") as f:
                            # Convert datetime objects to strings for JSON serialization
                            serializable_data = []
                            for pr in pr_data:
                                pr_copy = pr.copy()
                                # Remove the datetime objects that can't be serialized
                                del pr_copy['created_at']
                                del pr_copy['updated_at']
                                serializable_data.append(pr_copy)
                                
                            json.dump(serializable_data, f, indent=2)
                        print(f"PR details exported to {filename}")
                else:
                    print("No PRs found in the specified time period.")
            else:
                pr_numbers = analyzer.get_weekly_pr_numbers()
                print(f"\n=== PR NUMBERS UPDATED IN THE LAST {analyzer.days} DAYS ===")
                if pr_numbers:
                    print("PR Numbers:", ", ".join(map(str, pr_numbers)))
                    print(f"\nTotal: {len(pr_numbers)} pull requests")
                    
                    # Export to file if requested
                    if export:
                        filename = f"pr_numbers_{datetime.now().strftime('%Y%m%d')}.txt"
                        with open(filename, "w") as f:
                            f.write("\n".join(map(str, pr_numbers)))
                        print(f"PR numbers exported to {filename}")
                else:
                    print("No PRs found in the specified time period.")
            sys.exit(0)
            
        # Date range option
        elif sys.argv[1] == "--date-range" or sys.argv[1] == "-dr":
            start_date = None
            end_date = None
            
            if len(sys.argv) > 2:
                start_date = sys.argv[2]
            if len(sys.argv) > 3:
                end_date = sys.argv[3]
                
            try:
                pr_numbers = analyzer.get_pr_numbers_by_date_range(start_date, end_date)
                
                date_range_str = ""
                if start_date and end_date:
                    date_range_str = f"FROM {start_date} TO {end_date}"
                elif start_date:
                    date_range_str = f"FROM {start_date}"
                elif end_date:
                    date_range_str = f"UNTIL {end_date}"
                
                print(f"\n=== PR NUMBERS {date_range_str} ===")
                
                if pr_numbers:
                    print("PR Numbers:", ", ".join(map(str, pr_numbers)))
                    print(f"\nTotal: {len(pr_numbers)} pull requests")
                    
                    # Export to file if requested
                    if "--export" in sys.argv:
                        date_part = f"{start_date or 'start'}_{end_date or 'end'}"
                        filename = f"pr_numbers_{date_part}.txt"
                        with open(filename, "w") as f:
                            f.write("\n".join(map(str, pr_numbers)))
                        print(f"PR numbers exported to {filename}")
                else:
                    print("No PRs found in the specified time period.")
            except ValueError as e:
                print(f"Error: {e}")
                print("Date format should be YYYY-MM-DD")
            sys.exit(0)
        
        # Check if a specific PR number is provided as an argument
        elif sys.argv[1].isdigit():
            pr_number = int(sys.argv[1])
            print(f"\n=== VIEWING PULL REQUEST #{pr_number} ===")
        
        # Get PR details
        pr_details = analyzer.get_pr_details(pr_number)
        if pr_details and 'pull_request' in pr_details:
            pr = pr_details['pull_request']
            pr_title = pr['title']
            pr_state = pr['state']
            pr_user = pr['user']['login']
            created_date = datetime.strptime(pr['created_at'], analyzer.date_format)
            updated_date = datetime.strptime(pr['updated_at'], analyzer.date_format)
            
            # Determine if PR is merged
            merged_status = "MERGED" if pr.get('merged_at') else f"({pr_state.upper()})"
            
            print(f"PR #{pr_number}: {pr_title} {merged_status}")
            print(f"Created: {created_date.strftime('%Y-%m-%d %H:%M')} by {pr_user}")
            print(f"Updated: {updated_date.strftime('%Y-%m-%d %H:%M')}")
            
            # Show commits in this PR
            if 'commits' in pr_details:
                print(f"\n=== COMMITS ({len(pr_details['commits'])}) ===")
                for commit in pr_details['commits']:
                    author = commit['commit']['author']['name']
                    message = commit['commit']['message'].split('\n')[0]
                    sha = commit['sha'][:7]
                    print(f"{sha} - {author}: {message}")
            
            # Get and display the code changes
            pr_changes = analyzer.get_pr_code_changes(pr_number)
            print_pr_code_changes(pr_changes)
            
            # Show reviews if any
            if 'reviews' in pr_details and pr_details['reviews']:
                print(f"\n=== REVIEWS ({len(pr_details['reviews'])}) ===")
                for review in pr_details['reviews']:
                    reviewer = review['user']['login']
                    state = review['state'].upper()
                    submitted_at = datetime.strptime(review['submitted_at'], analyzer.date_format)
                    print(f"{submitted_at.strftime('%Y-%m-%d %H:%M')} - {reviewer}: {state}")
                    if review.get('body'):
                        print(f"  Comment: {review['body']}")
            
        else:
            print(f"Error: Could not find PR #{pr_number}")
        
    else:
        # Regular summary mode
        
        # Get and display commits
        print("\n=== RECENT COMMITS ===")
        commits = analyzer.get_commits()
        print(f"Found {len(commits)} commits in the last {analyzer.days} days")
        
        # Print some details about each commit
        for commit in commits:
            try:
                commit_date = datetime.strptime(commit['commit']['author']['date'], analyzer.date_format)
                author_name = commit['commit']['author']['name']
                message = commit['commit']['message'].split('\n')[0]  # Get first line of commit message
                print(f"{commit_date.strftime('%Y-%m-%d %H:%M')}: {author_name} - {message}")
            except (KeyError, ValueError) as e:
                print(f"Error processing commit: {e}")
        
        # Get and display pull requests
        print("\n=== RECENT PULL REQUESTS ===")
        pull_requests = analyzer.get_pull_requests()
        print(f"Found {len(pull_requests)} pull requests updated in the last {analyzer.days} days")
        
        # Print details about each PR
        for pr in pull_requests:
            try:
                pr_number = pr['number']
                pr_title = pr['title']
                pr_state = pr['state']
                pr_user = pr['user']['login']
                created_date = datetime.strptime(pr['created_at'], analyzer.date_format)
                updated_date = datetime.strptime(pr['updated_at'], analyzer.date_format)
                
                # Determine if PR is merged
                merged_status = "MERGED" if pr.get('merged_at') else f"({pr_state.upper()})"
                
                print(f"\nPR #{pr_number}: {pr_title} {merged_status}")
                print(f"  Created: {created_date.strftime('%Y-%m-%d %H:%M')} by {pr_user}")
                print(f"  Updated: {updated_date.strftime('%Y-%m-%d %H:%M')}")
                print(f"  To view code changes: python devanalyzer.py {pr_number}")
                
            except (KeyError, ValueError) as e:
                print(f"Error processing pull request: {e}")
        
        # Analyze pull request statistics
        if pull_requests:
            print("\n=== PULL REQUEST ANALYSIS ===")
            stats = analyzer.analyze_pull_requests(pull_requests)
            
            print(f"Total PRs: {stats['total']}")
            print(f"Merged: {stats['merged']}")
            print(f"Open: {stats['open']}")
            print(f"Closed without merge: {stats['closed_without_merge']}")
            
            if stats['avg_time_to_merge_hours'] is not None:
                print(f"Average time to merge: {stats['avg_time_to_merge_hours']:.2f} hours")
            
            print(f"Average commits per PR: {stats['avg_commits']:.1f}")
            print(f"Average comments/reviews per PR: {stats['avg_comments']:.1f}")

        # Show contribution summary
        print("\n=== CONTRIBUTION SUMMARY ===")
        contributions = analyzer.get_contribution_summary()

        if contributions:
            # Sort by total contributions (descending)
            sorted_contributions = sorted(contributions.items(),
                                        key=lambda x: x[1]['total_contributions'],
                                        reverse=True)

            print(f"{'Contributor':<20} {'Commits':<8} {'PRs':<5} {'Reviews':<8} {'Lines +':<8} {'Lines -':<8} {'Files':<6} {'Total':<6}")
            print("-" * 85)

            for person, stats in sorted_contributions[:10]:  # Show top 10 contributors
                print(f"{person:<20} {stats['commits']:<8} {stats['prs_created']:<5} {stats['prs_reviewed']:<8} {stats['lines_added']:<8} {stats['lines_deleted']:<8} {stats['files_changed_count']:<6} {stats['total_contributions']:<6}")

            if len(contributions) > 10:
                print(f"\n... and {len(contributions) - 10} more contributors")

            print(f"\nTotal contributors: {len(contributions)}")
            total_commits = sum(stats['commits'] for stats in contributions.values())
            total_prs = sum(stats['prs_created'] for stats in contributions.values())
            total_reviews = sum(stats['prs_reviewed'] for stats in contributions.values())
            print(f"Total commits: {total_commits}")
            print(f"Total PRs created: {total_prs}")
            print(f"Total PR reviews: {total_reviews}")
        else:
            print("No contributions found in the specified time period.")

        print("\nUsage options:")
        print("- For help and more options:")
        print("  python devanalyzer.py --help")
        print("- To view details and code changes for a specific PR:")
        print("  python devanalyzer.py <PR_NUMBER>")
        print("- To list only PR numbers for the week:")
        print("  python devanalyzer.py --numbers")
        print("- To list detailed PR information for the week:")
        print("  python devanalyzer.py --numbers --detailed")
        print("- To get PR numbers for a specific date range:")
        print("  python devanalyzer.py --date-range 2025-10-01 2025-10-11")
        print("- To show detailed contribution summary per person:")
        print("  python devanalyzer.py --contributions")
        print("- To analyze PR value and get a score:")
        print("  python devanalyzer.py --analyze-pr <PR_NUMBER>")
        print("- To analyze a PR with AI and post to Discord:")
        print("  python devanalyzer.py --discord-analyze <PR_NUMBER>")
        print("- To analyze all weekly PRs and post to Discord:")
        print("  python devanalyzer.py --discord-analyze-all")

