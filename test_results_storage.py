#!/usr/bin/env python3
"""
Test Results Storage Module

Provides persistent storage and retrieval of speed test results
with export functionality and historical analysis.
"""

import json
import sqlite3
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import statistics

from speedtest_core import SpeedTestResult


class TestResultStorage:
    """Handles storage and retrieval of speed test results with connection pooling."""

    def __init__(self, db_path: str = "speedtest_history.db"):
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None
        self.init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection with connection pooling.

        Returns:
            Active SQLite connection

        Raises:
            sqlite3.Error: If connection initialization fails
        """
        if self._conn is None:
            temp_conn = None
            try:
                # Create connection and initialize settings atomically
                temp_conn = sqlite3.connect(self.db_path)
                # Set autocommit mode for PRAGMAs to execute immediately
                temp_conn.isolation_level = None
                temp_conn.execute("PRAGMA journal_mode=WAL")
                temp_conn.execute("PRAGMA busy_timeout=5000")
                temp_conn.row_factory = sqlite3.Row
                # Only assign after ALL initialization succeeds
                self._conn = temp_conn
                temp_conn = None  # Prevent cleanup if successful
            except Exception:
                # Close partial connection and re-raise
                if temp_conn is not None:
                    try:
                        temp_conn.close()
                    except Exception:
                        pass  # Ignore errors during cleanup
                raise
        return self._conn

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass  # Ignore close errors
            finally:
                self._conn = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()
        return False
    
    def init_database(self) -> None:
        """Initialize SQLite database with results table."""
        with sqlite3.connect(self.db_path) as conn:
            # Enable WAL mode for better concurrent access
            conn.execute("PRAGMA journal_mode=WAL")
            # Set busy timeout to 5 seconds for concurrent writes
            conn.execute("PRAGMA busy_timeout=5000")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    download_mbps REAL NOT NULL,
                    upload_mbps REAL NOT NULL,
                    ping_ms REAL NOT NULL,
                    server_info TEXT NOT NULL,
                    is_valid BOOLEAN NOT NULL,
                    warnings TEXT,
                    test_date TEXT NOT NULL
                )
            """)

            # Create indexes for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON test_results(timestamp)
            """)

            # Additional index for date range queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_date
                ON test_results(test_date)
            """)
    
    def save_result(self, result: SpeedTestResult) -> int:
        """Save test result to database.
        
        Args:
            result: SpeedTestResult object to save
            
        Returns:
            ID of saved record
        """
        test_date = datetime.fromtimestamp(result.timestamp).isoformat()
        warnings_json = json.dumps(result.warnings) if result.warnings else None
        
        conn = self._get_connection()
        cursor = conn.execute(
            """
                INSERT INTO test_results 
                (timestamp, download_mbps, upload_mbps, ping_ms, server_info, 
                 is_valid, warnings, test_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.timestamp,
                result.download_mbps,
                result.upload_mbps,
                result.ping_ms,
                result.server_info,
                result.is_valid,
                warnings_json,
                test_date,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    
    def get_recent_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent test results.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of result dictionaries
        """
        conn = self._get_connection()
        cursor = conn.execute(
            """
                SELECT * FROM test_results 
                WHERE is_valid = 1
                ORDER BY timestamp DESC 
                LIMIT ?
            """,
            (limit,),
        )

        results = []
        for row in cursor:
            result_dict = dict(row)
            if result_dict['warnings']:
                result_dict['warnings'] = json.loads(result_dict['warnings'])
            results.append(result_dict)

        return results

    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all valid test results (use with caution on large databases).

        Returns:
            List of all result dictionaries
        """
        conn = self._get_connection()
        cursor = conn.execute(
            """
                SELECT * FROM test_results
                WHERE is_valid = 1
                ORDER BY timestamp DESC
            """
        )

        results = []
        for row in cursor:
            result_dict = dict(row)
            if result_dict['warnings']:
                result_dict['warnings'] = json.loads(result_dict['warnings'])
            results.append(result_dict)

        return results

    def get_results_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get results within date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of result dictionaries
        """
        start_timestamp = start_date.timestamp()
        end_timestamp = end_date.timestamp()
        
        conn = self._get_connection()
        cursor = conn.execute(
            """
                SELECT * FROM test_results 
                WHERE timestamp BETWEEN ? AND ? AND is_valid = 1
                ORDER BY timestamp DESC
            """,
            (start_timestamp, end_timestamp),
        )
        
        results = []
        for row in cursor:
            result_dict = dict(row)
            if result_dict['warnings']:
                result_dict['warnings'] = json.loads(result_dict['warnings'])
            results.append(result_dict)
        
        return results
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get statistics for recent results.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with statistics
        """
        start_date = datetime.now() - timedelta(days=days)
        results = self.get_results_by_date_range(start_date, datetime.now())
        
        if not results:
            return {
                'count': 0,
                'period_days': days,
                'download': {},
                'upload': {},
                'ping': {}
            }
        
        downloads = [r['download_mbps'] for r in results]
        uploads = [r['upload_mbps'] for r in results]
        pings = [r['ping_ms'] for r in results]
        
        def calc_stats(values):
            return {
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'count': len(values)
            }
        
        return {
            'count': len(results),
            'period_days': days,
            'first_test': results[-1]['test_date'] if results else None,
            'last_test': results[0]['test_date'] if results else None,
            'download': calc_stats(downloads),
            'upload': calc_stats(uploads),
            'ping': calc_stats(pings)
        }
    
    def export_to_csv(self, output_file: str, days: Optional[int] = None, batch_size: int = 1000) -> int:
        """Export results to CSV file using batched queries for memory efficiency.

        Args:
            output_file: Path to output CSV file
            days: Number of recent days to export (None for all)
            batch_size: Number of records per batch (default 1000)

        Returns:
            Number of exported records

        Raises:
            ValueError: If batch_size is invalid
        """
        if batch_size <= 0:
            raise ValueError(f"batch_size must be positive, got {batch_size}")

        total_exported = 0

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'test_date', 'download_mbps', 'upload_mbps', 'ping_ms',
                'server_info', 'warnings'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Stream results in batches
            offset = 0
            while True:
                batch = self._get_results_batch(days, offset, batch_size)
                if not batch:
                    break

                for result in batch:
                    writer.writerow({
                        'test_date': result['test_date'],
                        'download_mbps': result['download_mbps'],
                        'upload_mbps': result['upload_mbps'],
                        'ping_ms': result['ping_ms'],
                        'server_info': result['server_info'],
                        'warnings': '; '.join(result['warnings']) if result['warnings'] else ''
                    })
                    total_exported += 1

                offset += batch_size

        return total_exported

    def _get_results_batch(self, days: Optional[int], offset: int, limit: int) -> List[Dict[str, Any]]:
        """Get a batch of results for streaming export.

        Args:
            days: Number of recent days (None for all)
            offset: Starting offset
            limit: Number of records to fetch

        Returns:
            List of result dictionaries
        """
        conn = self._get_connection()

        if days:
            start_timestamp = (datetime.now() - timedelta(days=days)).timestamp()
            cursor = conn.execute(
                """
                    SELECT * FROM test_results
                    WHERE is_valid = 1 AND timestamp >= ?
                    ORDER BY timestamp ASC
                    LIMIT ? OFFSET ?
                """,
                (start_timestamp, limit, offset),
            )
        else:
            cursor = conn.execute(
                """
                    SELECT * FROM test_results
                    WHERE is_valid = 1
                    ORDER BY timestamp ASC
                    LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )

        results = []
        for row in cursor:
            result_dict = dict(row)
            if result_dict['warnings']:
                result_dict['warnings'] = json.loads(result_dict['warnings'])
            else:
                result_dict['warnings'] = []
            results.append(result_dict)

        return results
    
    def export_to_json(self, output_file: str, days: Optional[int] = None, batch_size: int = 1000) -> int:
        """Export results to JSON file using batched queries for memory efficiency.

        Args:
            output_file: Path to output JSON file
            days: Number of recent days to export (None for all)
            batch_size: Number of records per batch (default 1000)

        Returns:
            Number of exported records

        Raises:
            ValueError: If batch_size is invalid
        """
        if batch_size <= 0:
            raise ValueError(f"batch_size must be positive, got {batch_size}")

        all_results = []
        offset = 0

        # Stream results in batches
        while True:
            batch = self._get_results_batch(days, offset, batch_size)
            if not batch:
                break
            all_results.extend(batch)
            offset += batch_size

        export_data = {
            'export_date': datetime.now().isoformat(),
            'export_period_days': days,
            'total_results': len(all_results),
            'results': all_results  # Already ordered ASC from query
        }

        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)

        return len(all_results)
    
    def cleanup_old_results(self, keep_days: int = 365) -> int:
        """Remove old results beyond specified days.
        
        Args:
            keep_days: Number of days of history to keep
            
        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        cutoff_timestamp = cutoff_date.timestamp()
        
        conn = self._get_connection()
        cursor = conn.execute(
            """
                DELETE FROM test_results 
                WHERE timestamp < ?
            """,
            (cutoff_timestamp,),
        )
        conn.commit()
        return cursor.rowcount
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information.
        
        Returns:
            Database statistics
        """
        conn = self._get_connection()
        # Total records
        total_count = conn.execute("SELECT COUNT(*) FROM test_results").fetchone()[0]
        
        # Valid records
        valid_count = conn.execute("SELECT COUNT(*) FROM test_results WHERE is_valid = 1").fetchone()[0]
        
        # Date range
        date_range = conn.execute(
            """
                SELECT MIN(test_date), MAX(test_date) 
                FROM test_results WHERE is_valid = 1
            """
        ).fetchone()
        
        # Database file size
        db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
        
        return {
            'database_path': str(self.db_path),
            'database_size_bytes': db_size,
            'database_size_mb': round(db_size / (1024 * 1024), 2),
            'total_records': total_count,
            'valid_records': valid_count,
            'first_test': date_range[0] if date_range[0] else None,
            'last_test': date_range[1] if date_range[1] else None
        }


def main():
    """CLI interface for results storage."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Speed Test Results Storage Management')
    parser.add_argument('--db', default='speedtest_history.db', help='Database file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('--days', type=int, default=30, help='Days to analyze')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export results')
    export_parser.add_argument('format', choices=['csv', 'json'], help='Export format')
    export_parser.add_argument('output', help='Output file path')
    export_parser.add_argument('--days', type=int, help='Days to export (all if not specified)')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show database info')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old results')
    cleanup_parser.add_argument('--keep-days', type=int, default=365, help='Days of history to keep')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    storage = TestResultStorage(args.db)
    
    if args.command == 'stats':
        stats = storage.get_statistics(args.days)
        if stats['count'] == 0:
            print(f"No valid test results found in the last {args.days} days.")
            return 0
            
        print(f"📊 Speed Test Statistics (last {args.days} days)")
        print("=" * 50)
        print(f"Total tests: {stats['count']}")
        print(f"Period: {stats['first_test']} to {stats['last_test']}")
        print()
        
        def print_metric_stats(name, data):
            print(f"{name}:")
            print(f"  Average: {data['mean']:.2f}")
            print(f"  Median:  {data['median']:.2f}")
            print(f"  Min:     {data['min']:.2f}")
            print(f"  Max:     {data['max']:.2f}")
            print()
        
        print_metric_stats("Download (Mbps)", stats['download'])
        print_metric_stats("Upload (Mbps)", stats['upload'])
        print_metric_stats("Ping (ms)", stats['ping'])
    
    elif args.command == 'export':
        if args.format == 'csv':
            count = storage.export_to_csv(args.output, args.days)
        else:  # json
            count = storage.export_to_json(args.output, args.days)
        
        period_str = f"last {args.days} days" if args.days else "all time"
        print(f"✅ Exported {count} results ({period_str}) to {args.output}")
    
    elif args.command == 'info':
        info = storage.get_database_info()
        print("📁 Database Information")
        print("=" * 30)
        print(f"Path: {info['database_path']}")
        print(f"Size: {info['database_size_mb']} MB")
        print(f"Total records: {info['total_records']}")
        print(f"Valid records: {info['valid_records']}")
        if info['first_test'] and info['last_test']:
            print(f"Date range: {info['first_test']} to {info['last_test']}")
    
    elif args.command == 'cleanup':
        deleted_count = storage.cleanup_old_results(args.keep_days)
        print(f"🗑️  Cleaned up {deleted_count} old records (keeping last {args.keep_days} days)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())