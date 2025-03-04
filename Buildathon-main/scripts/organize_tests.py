#!/usr/bin/env python
"""
Script to organize test files by moving them to the tests directory.
"""

import os
import shutil
import sys

def organize_tests():
    """
    Move test files to the tests directory, except for test_app.py
    which is already in that directory.
    """
    # Check if tests directory exists
    if not os.path.exists('tests'):
        print("Creating tests directory...")
        os.makedirs('tests')

    # List of test files to move
    test_files = [
        'test_gatsby_search.py',
        'test_google_api.py',
        'test_movies.py',
        'test_place_details.py',
        'test_showtimes.py',
        'test_specific_show.py',
        'test_timezone.py',
        'test_timezone_events.py',
        'test_timezone_simple.py',
        'run_test.py'
    ]

    # Move each test file
    for filename in test_files:
        if os.path.exists(filename):
            dest_path = os.path.join('tests', filename)
            
            # Check if destination already exists
            if os.path.exists(dest_path):
                print(f"Warning: {dest_path} already exists, skipping {filename}")
                continue
                
            print(f"Moving {filename} to tests directory...")
            try:
                shutil.move(filename, dest_path)
                print(f"Successfully moved {filename}")
            except Exception as e:
                print(f"Error moving {filename}: {str(e)}")
        else:
            print(f"Warning: {filename} not found, skipping")

    print("Test organization complete!")

if __name__ == "__main__":
    organize_tests() 