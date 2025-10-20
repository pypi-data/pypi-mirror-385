"""
System Catalog for EzDB RDBMS
Provides Oracle-like system tables (ALL_OBJECTS, ALL_TABLES, etc.)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class SystemCatalog:
    """
    Manages system catalog tables like Oracle's data dictionary.
    Tracks metadata for all database objects.
    """

    def __init__(self):
        """Initialize system catalog"""
        self.objects = []  # Store ALL_OBJECTS data
        self.object_id_counter = 1000  # Start from 1000 for user objects

    def add_object(self, owner: str, object_name: str, object_type: str,
                   status: str = 'VALID', namespace: int = 1) -> int:
        """
        Add a new object to the catalog.

        Args:
            owner: Schema owner (default 'PUBLIC')
            object_name: Name of the object
            object_type: Type (TABLE, VIEW, PROCEDURE, FUNCTION, etc.)
            status: Status (VALID, INVALID)
            namespace: Namespace identifier

        Returns:
            Object ID assigned to the object
        """
        now = datetime.now()
        object_id = self.object_id_counter
        self.object_id_counter += 1

        obj_record = {
            'OWNER': owner,
            'OBJECT_NAME': object_name,
            'SUBOBJECT_NAME': None,
            'OBJECT_ID': object_id,
            'DATA_OBJECT_ID': object_id,
            'OBJECT_TYPE': object_type,
            'CREATED': now.strftime('%Y-%m-%d %H:%M:%S'),
            'LAST_DDL_TIME': now.strftime('%Y-%m-%d %H:%M:%S'),
            'TIMESTAMP': now.strftime('%Y-%m-%d %H:%M:%S'),
            'STATUS': status,
            'TEMPORARY': 'N',
            'GENERATED': 'N',
            'SECONDARY': 'N',
            'NAMESPACE': namespace,
            'EDITION_NAME': None,
            'SHARING': 'NONE',
            'EDITIONABLE': 'N',
            'ORACLE_MAINTAINED': 'N',
            'APPLICATION': 'N',
            'DEFAULT_COLLATION': 'USING_NLS_COMP',
            'DUPLICATED': 'N',
            'SHARDED': 'N',
            'IMPORTED_OBJECT': 'N',
            'SYNCHRONOUS_DUPLICATED': 'N',
            'CREATED_APPID': None,
            'CREATED_VSNID': None,
            'MODIFIED_APPID': None,
            'MODIFIED_VSNID': None
        }

        self.objects.append(obj_record)
        return object_id

    def update_object_ddl_time(self, object_name: str, object_type: str):
        """
        Update LAST_DDL_TIME when an object is modified.

        Args:
            object_name: Name of the object
            object_type: Type of the object
        """
        now = datetime.now()
        for obj in self.objects:
            if obj['OBJECT_NAME'] == object_name and obj['OBJECT_TYPE'] == object_type:
                obj['LAST_DDL_TIME'] = now.strftime('%Y-%m-%d %H:%M:%S')
                obj['TIMESTAMP'] = now.strftime('%Y-%m-%d %H:%M:%S')
                break

    def remove_object(self, object_name: str, object_type: str):
        """
        Remove an object from the catalog.

        Args:
            object_name: Name of the object
            object_type: Type of the object
        """
        self.objects = [obj for obj in self.objects
                       if not (obj['OBJECT_NAME'] == object_name and
                              obj['OBJECT_TYPE'] == object_type)]

    def get_object(self, object_name: str, object_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get object metadata.

        Args:
            object_name: Name of the object
            object_type: Optional type filter

        Returns:
            Object record or None
        """
        for obj in self.objects:
            if obj['OBJECT_NAME'] == object_name:
                if object_type is None or obj['OBJECT_TYPE'] == object_type:
                    return obj
        return None

    def list_objects(self, owner: Optional[str] = None,
                     object_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all objects, optionally filtered by owner and type.

        Args:
            owner: Filter by owner
            object_type: Filter by type

        Returns:
            List of object records
        """
        results = self.objects

        if owner:
            results = [obj for obj in results if obj['OWNER'] == owner]

        if object_type:
            results = [obj for obj in results if obj['OBJECT_TYPE'] == object_type]

        return results

    def get_all_objects_data(self) -> List[Dict[str, Any]]:
        """
        Get all objects for ALL_OBJECTS query.

        Returns:
            List of all object records
        """
        return self.objects.copy()

    def get_all_tables_data(self) -> List[Dict[str, Any]]:
        """
        Get table-specific metadata for ALL_TABLES query.

        Returns:
            List of table records with additional metadata
        """
        tables = [obj for obj in self.objects if obj['OBJECT_TYPE'] == 'TABLE']

        # Add table-specific fields
        result = []
        for table in tables:
            table_info = table.copy()
            table_info.update({
                'TABLESPACE_NAME': 'DEFAULT',
                'CLUSTER_NAME': None,
                'IOT_NAME': None,
                'STATUS': 'VALID',
                'PCT_FREE': None,
                'PCT_USED': None,
                'INI_TRANS': None,
                'MAX_TRANS': None,
                'INITIAL_EXTENT': None,
                'NEXT_EXTENT': None,
                'MIN_EXTENTS': None,
                'MAX_EXTENTS': None,
                'PCT_INCREASE': None,
                'FREELISTS': None,
                'FREELIST_GROUPS': None,
                'LOGGING': 'YES',
                'BACKED_UP': 'N',
                'NUM_ROWS': None,
                'BLOCKS': None,
                'EMPTY_BLOCKS': None,
                'AVG_SPACE': None,
                'CHAIN_CNT': None,
                'AVG_ROW_LEN': None,
                'AVG_SPACE_FREELIST_BLOCKS': None,
                'NUM_FREELIST_BLOCKS': None,
                'DEGREE': None,
                'INSTANCES': None,
                'CACHE': 'N',
                'TABLE_LOCK': 'ENABLED',
                'SAMPLE_SIZE': None,
                'LAST_ANALYZED': None,
                'PARTITIONED': 'NO',
                'IOT_TYPE': None,
                'TEMPORARY': 'N',
                'SECONDARY': 'N',
                'NESTED': 'NO',
                'BUFFER_POOL': 'DEFAULT',
                'FLASH_CACHE': 'DEFAULT',
                'CELL_FLASH_CACHE': 'DEFAULT',
                'ROW_MOVEMENT': 'DISABLED',
                'GLOBAL_STATS': 'NO',
                'USER_STATS': 'NO',
                'DURATION': None,
                'SKIP_CORRUPT': 'DISABLED',
                'MONITORING': 'NO',
                'CLUSTER_OWNER': None,
                'DEPENDENCIES': 'DISABLED',
                'COMPRESSION': 'DISABLED',
                'COMPRESS_FOR': None,
                'DROPPED': 'NO',
                'READ_ONLY': 'NO',
                'SEGMENT_CREATED': 'YES',
                'RESULT_CACHE': 'DEFAULT'
            })
            result.append(table_info)

        return result

    def get_object_count_by_type(self) -> Dict[str, int]:
        """
        Get count of objects by type.

        Returns:
            Dictionary mapping object type to count
        """
        counts = {}
        for obj in self.objects:
            obj_type = obj['OBJECT_TYPE']
            counts[obj_type] = counts.get(obj_type, 0) + 1
        return counts
