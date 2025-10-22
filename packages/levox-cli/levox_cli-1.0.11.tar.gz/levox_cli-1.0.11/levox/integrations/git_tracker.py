"""
Git integration for tracking commits, PRs, and remediation evidence.
Supports GitHub, GitLab, and local git repositories.
"""

import os
import re
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

try:
    import git
    GIT_PYTHON_AVAILABLE = True
except ImportError:
    GIT_PYTHON_AVAILABLE = False

try:
    from github import Github
    GITHUB_API_AVAILABLE = True
except ImportError:
    GITHUB_API_AVAILABLE = False

try:
    import gitlab
    GITLAB_API_AVAILABLE = True
except ImportError:
    GITLAB_API_AVAILABLE = False


@dataclass
class CommitInfo:
    """Information about a git commit."""
    hash: str
    author: str
    author_email: str
    date: datetime
    message: str
    branch: str
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    pr_title: Optional[str] = None
    pr_state: Optional[str] = None


@dataclass
class FileHistory:
    """History of changes to a specific file."""
    file_path: str
    commits: List[CommitInfo]
    blame_info: List[Tuple[int, str, str, str]]  # line, author, date, commit


@dataclass
class RemediationCommit:
    """Commit that fixed a violation."""
    violation_id: str
    commit_hash: str
    commit_info: CommitInfo
    confidence: float
    evidence: str  # Description of how the commit fixed the violation


class GitTracker:
    """Tracks git commits, PRs, and remediation evidence."""
    
    def __init__(self, repo_path: Optional[str] = None, 
                 github_token: Optional[str] = None,
                 gitlab_token: Optional[str] = None):
        """Initialize git tracker."""
        self.logger = logging.getLogger(__name__)
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.github_token = github_token
        self.gitlab_token = gitlab_token
        
        # Initialize git repository
        self.repo = None
        if GIT_PYTHON_AVAILABLE:
            try:
                self.repo = git.Repo(self.repo_path)
            except Exception as e:
                self.logger.warning(f"Failed to initialize git repository: {e}")
        
        # Initialize API clients
        self.github_client = None
        self.gitlab_client = None
        
        if github_token and GITHUB_API_AVAILABLE:
            self.github_client = Github(github_token)
        
        if gitlab_token and GITLAB_API_AVAILABLE:
            self.gitlab_client = gitlab.Gitlab(token=gitlab_token)
    
    def get_current_commit(self) -> Optional[CommitInfo]:
        """Get current HEAD commit information."""
        try:
            if not self.repo:
                return None
            
            head_commit = self.repo.head.commit
            return self._commit_to_info(head_commit)
            
        except Exception as e:
            self.logger.error(f"Failed to get current commit: {e}")
            return None
    
    def get_commit_info(self, commit_hash: str) -> Optional[CommitInfo]:
        """Get detailed information about a specific commit."""
        try:
            if not self.repo:
                return None
            
            commit = self.repo.commit(commit_hash)
            return self._commit_to_info(commit)
            
        except Exception as e:
            self.logger.error(f"Failed to get commit info for {commit_hash}: {e}")
            return None
    
    def _commit_to_info(self, commit) -> CommitInfo:
        """Convert git commit object to CommitInfo."""
        try:
            # Get branch information
            branch = "unknown"
            try:
                branch = self.repo.active_branch.name
            except:
                # Try to get branch from commit
                for ref in self.repo.refs:
                    if ref.commit == commit:
                        branch = ref.name
                        break
            
            # Get PR information if available
            pr_number, pr_url, pr_title, pr_state = self._get_pr_info(commit)
            
            return CommitInfo(
                hash=commit.hexsha,
                author=commit.author.name,
                author_email=commit.author.email,
                date=datetime.fromtimestamp(commit.committed_date),
                message=commit.message.strip(),
                branch=branch,
                pr_number=pr_number,
                pr_url=pr_url,
                pr_title=pr_title,
                pr_state=pr_state
            )
            
        except Exception as e:
            self.logger.error(f"Failed to convert commit to info: {e}")
            return None
    
    def _get_pr_info(self, commit) -> Tuple[Optional[int], Optional[str], Optional[str], Optional[str]]:
        """Get PR information for a commit."""
        try:
            # Try to extract PR number from commit message
            pr_number = self._extract_pr_number(commit.message)
            if not pr_number:
                return None, None, None, None
            
            # Get PR details from API
            if self.github_client:
                return self._get_github_pr_info(pr_number)
            elif self.gitlab_client:
                return self._get_gitlab_pr_info(pr_number)
            else:
                return pr_number, None, None, None
                
        except Exception as e:
            self.logger.error(f"Failed to get PR info: {e}")
            return None, None, None, None
    
    def _extract_pr_number(self, message: str) -> Optional[int]:
        """Extract PR number from commit message."""
        # Common patterns for PR references
        patterns = [
            r'#(\d+)',  # #123
            r'PR #(\d+)',  # PR #123
            r'Merge pull request #(\d+)',  # GitHub merge
            r'Merge request !(\d+)',  # GitLab merge request
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _get_github_pr_info(self, pr_number: int) -> Tuple[int, Optional[str], Optional[str], Optional[str]]:
        """Get GitHub PR information."""
        try:
            # This would need the repository name - simplified for now
            # In a real implementation, you'd get the repo name from git remote
            return pr_number, None, None, None
        except Exception as e:
            self.logger.error(f"Failed to get GitHub PR info: {e}")
            return pr_number, None, None, None
    
    def _get_gitlab_pr_info(self, mr_number: int) -> Tuple[int, Optional[str], Optional[str], Optional[str]]:
        """Get GitLab merge request information."""
        try:
            # Similar to GitHub - would need repository information
            return mr_number, None, None, None
        except Exception as e:
            self.logger.error(f"Failed to get GitLab MR info: {e}")
            return mr_number, None, None, None
    
    def get_file_history(self, file_path: str, limit: int = 50) -> Optional[FileHistory]:
        """Get commit history for a specific file."""
        try:
            if not self.repo:
                return None
            
            # Get commit history for the file
            commits = []
            try:
                for commit in self.repo.iter_commits(paths=file_path, max_count=limit):
                    commit_info = self._commit_to_info(commit)
                    if commit_info:
                        commits.append(commit_info)
            except Exception as e:
                self.logger.warning(f"Failed to get file history for {file_path}: {e}")
                return None
            
            # Get blame information
            blame_info = self.get_blame_info(file_path)
            
            return FileHistory(
                file_path=file_path,
                commits=commits,
                blame_info=blame_info
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get file history: {e}")
            return None
    
    def get_blame_info(self, file_path: str) -> List[Tuple[int, str, str, str]]:
        """Get blame information for a file (who wrote each line)."""
        try:
            if not self.repo:
                return []
            
            # Use git blame command
            result = subprocess.run(
                ['git', 'blame', '--line-porcelain', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.warning(f"Git blame failed for {file_path}")
                return []
            
            blame_info = []
            lines = result.stdout.split('\n')
            current_line = 0
            
            for line in lines:
                if line.startswith('author '):
                    author = line[7:]
                elif line.startswith('author-time '):
                    timestamp = int(line[12:])
                    date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                elif line.startswith('committer '):
                    committer = line[10:]
                elif line.startswith('summary '):
                    summary = line[8:]
                elif line.startswith('\t'):
                    # This is the actual line content
                    current_line += 1
                    blame_info.append((current_line, author, date, summary))
            
            return blame_info
            
        except Exception as e:
            self.logger.error(f"Failed to get blame info: {e}")
            return []
    
    def detect_remediation_commits(self, violation: Dict[str, Any]) -> List[RemediationCommit]:
        """Detect commits that likely fixed a violation."""
        try:
            file_path = violation.get('file_path')
            line_number = violation.get('line_number')
            violation_type = violation.get('violation_type')
            
            if not file_path:
                return []
            
            # Get file history
            file_history = self.get_file_history(file_path)
            if not file_history:
                return []
            
            remediation_commits = []
            
            # Look for commits that might have fixed the violation
            for commit in file_history.commits:
                confidence = self._calculate_remediation_confidence(
                    commit, violation, file_path, line_number
                )
                
                if confidence > 0.3:  # Threshold for considering it a remediation
                    remediation_commits.append(RemediationCommit(
                        violation_id=violation.get('id', ''),
                        commit_hash=commit.hash,
                        commit_info=commit,
                        confidence=confidence,
                        evidence=self._generate_remediation_evidence(commit, violation)
                    ))
            
            # Sort by confidence
            remediation_commits.sort(key=lambda x: x.confidence, reverse=True)
            
            return remediation_commits[:5]  # Return top 5 most likely
            
        except Exception as e:
            self.logger.error(f"Failed to detect remediation commits: {e}")
            return []
    
    def _calculate_remediation_confidence(self, commit: CommitInfo, 
                                        violation: Dict[str, Any], 
                                        file_path: str, 
                                        line_number: int) -> float:
        """Calculate confidence that a commit fixed a violation."""
        confidence = 0.0
        
        # Check commit message for relevant keywords
        message_lower = commit.message.lower()
        violation_type = violation.get('violation_type', '').lower()
        
        # Keywords that suggest fixing the violation type
        keywords_map = {
            'pii_in_logs': ['log', 'pii', 'privacy', 'data', 'remove', 'fix'],
            'hardcoded_credentials': ['credential', 'password', 'secret', 'key', 'auth'],
            'unencrypted_pii': ['encrypt', 'security', 'pii', 'data'],
            'unnecessary_pii': ['remove', 'delete', 'pii', 'data', 'minimize'],
            'missing_consent': ['consent', 'privacy', 'gdpr', 'compliance'],
            'no_deletion_mechanism': ['delete', 'remove', 'cleanup', 'purge']
        }
        
        relevant_keywords = keywords_map.get(violation_type, [])
        for keyword in relevant_keywords:
            if keyword in message_lower:
                confidence += 0.2
        
        # Check for common fix patterns
        fix_patterns = [
            r'fix.*' + re.escape(violation_type),
            r'remove.*' + re.escape(violation_type),
            r'resolve.*' + re.escape(violation_type),
            r'address.*' + re.escape(violation_type)
        ]
        
        for pattern in fix_patterns:
            if re.search(pattern, message_lower):
                confidence += 0.3
        
        # Check if commit modified the specific file and line
        # This would require more complex git analysis
        if file_path in commit.message:
            confidence += 0.1
        
        # Check for security-related keywords
        security_keywords = ['security', 'privacy', 'gdpr', 'compliance', 'audit']
        for keyword in security_keywords:
            if keyword in message_lower:
                confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_remediation_evidence(self, commit: CommitInfo, 
                                     violation: Dict[str, Any]) -> str:
        """Generate evidence description for how commit fixed violation."""
        evidence_parts = []
        
        # Add commit message
        evidence_parts.append(f"Commit message: {commit.message}")
        
        # Add author and date
        evidence_parts.append(f"Fixed by: {commit.author} on {commit.date.strftime('%Y-%m-%d')}")
        
        # Add PR information if available
        if commit.pr_url:
            evidence_parts.append(f"PR: {commit.pr_url}")
        
        # Add file information
        file_path = violation.get('file_path', '')
        if file_path:
            evidence_parts.append(f"File: {file_path}")
        
        return " | ".join(evidence_parts)
    
    def get_deployment_status(self, commit_hash: str) -> Dict[str, Any]:
        """Get deployment status for a commit."""
        try:
            # This would integrate with CI/CD systems
            # For now, return basic information
            return {
                'deployed': False,
                'environment': 'unknown',
                'deployment_date': None,
                'deployment_url': None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get deployment status: {e}")
            return {
                'deployed': False,
                'environment': 'unknown',
                'deployment_date': None,
                'deployment_url': None
            }
    
    def get_environment(self, commit_hash: str) -> str:
        """Get environment information for a commit."""
        try:
            # This would check branch names, tags, or CI/CD configuration
            if not self.repo:
                return 'unknown'
            
            # Check branch name
            try:
                branch = self.repo.active_branch.name
                if 'main' in branch or 'master' in branch:
                    return 'production'
                elif 'develop' in branch or 'dev' in branch:
                    return 'development'
                elif 'staging' in branch or 'stage' in branch:
                    return 'staging'
            except:
                pass
            
            # Check tags
            try:
                tags = self.repo.tags
                for tag in tags:
                    if tag.commit.hexsha == commit_hash:
                        return 'production'  # Tagged commits are usually production
            except:
                pass
            
            return 'unknown'
            
        except Exception as e:
            self.logger.error(f"Failed to get environment: {e}")
            return 'unknown'
    
    def is_git_repository(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            return self.repo is not None and not self.repo.bare
        except:
            return False
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get repository information."""
        try:
            if not self.repo:
                return {}
            
            info = {
                'is_git_repo': True,
                'repository_path': str(self.repo_path),
                'current_branch': None,
                'remote_urls': [],
                'last_commit': None
            }
            
            # Get current branch
            try:
                info['current_branch'] = self.repo.active_branch.name
            except:
                pass
            
            # Get remote URLs
            try:
                for remote in self.repo.remotes:
                    info['remote_urls'].append({
                        'name': remote.name,
                        'url': remote.url
                    })
            except:
                pass
            
            # Get last commit
            try:
                last_commit = self.repo.head.commit
                info['last_commit'] = {
                    'hash': last_commit.hexsha,
                    'author': last_commit.author.name,
                    'date': last_commit.committed_datetime.isoformat(),
                    'message': last_commit.message.strip()
                }
            except:
                pass
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get repository info: {e}")
            return {'is_git_repo': False}
