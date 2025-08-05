import boto3
from typing import List, Dict
from collections import defaultdict

def get_max_folder_objects(bucket_name: str, prefix: str) -> List[str]:
    """
    Get objects from folders with maximum numeric value within each rec-load-dt.
    
    Args:
        bucket_name (str): Name of the S3 bucket
        prefix (str): Prefix path to search in
        
    Returns:
        List[str]: List of parquet file paths from the max numbered folders
    """
    s3_client = boto3.client('s3')
    
    # Get all objects with the given prefix
    paginator = s3_client.get_paginator('list_objects_v2')
    all_objects = []
    
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        if 'Contents' in page:
            all_objects.extend(page['Contents'])
    
    # Group objects by rec-load-dt
    rec_load_dt_groups = defaultdict(list)
    
    for obj in all_objects:
        key = obj['Key']
        parts = key.split('/')
        
        # Find the rec-load-dt part and the following numeric folder
        for i, part in enumerate(parts):
            if part.startswith('rec-load-dt='):
                if i + 1 < len(parts):  # Ensure there's a next part
                    rec_date = part
                    numeric_folder = parts[i + 1]
                    if numeric_folder.isdigit():  # Only process if it's a numeric folder
                        rec_load_dt_groups[rec_date].append({
                            'numeric_folder': numeric_folder,
                            'full_path': key
                        })
                break
    
    # Get parquet files from max numbered folders
    result_files = []
    
    for rec_date, folders in rec_load_dt_groups.items():
        if not folders:
            continue
            
        # Find the maximum numeric folder
        max_folder = max(folders, key=lambda x: int(x['numeric_folder']))
        max_folder_prefix = '/'.join(max_folder['full_path'].split('/')[:-1]) + '/'
        
        # Get all parquet files from the max folder
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=max_folder_prefix
        )
        
        if 'Contents' in response:
            parquet_files = [
                obj['Key'] for obj in response['Contents']
                if obj['Key'].endswith('.parquet')
            ]
            result_files.extend(parquet_files)
    
    return result_files

def main():
    # Example usage
    bucket_name = "your-bucket-name"
    prefix = "your/prefix/path/"
    
    try:
        parquet_files = get_max_folder_objects(bucket_name, prefix)
        print("Found parquet files in max folders:")
        for file in parquet_files:
            print(f"- {file}")
    except Exception as e:
        print(f"Error processing S3 folders: {str(e)}")

if __name__ == "__main__":
    main() 