"""
Serwis do komunikacji z Scaleway Object Storage
"""

import boto3
from botocore.exceptions import ClientError
import structlog
from typing import Optional, Dict, Any, List
import io
from datetime import datetime

from utils.config import get_settings

logger = structlog.get_logger(__name__)

class ScalewayObjectStorage:
    """Serwis do zarządzania plikami w Scaleway Object Storage"""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Konfiguracja S3-compatible klienta dla Scaleway
        self.client = boto3.client(
            's3',
            endpoint_url=f'https://s3.{self.settings.SCALEWAY_REGION}.scw.cloud',
            aws_access_key_id=self.settings.SCALEWAY_ACCESS_KEY,
            aws_secret_access_key=self.settings.SCALEWAY_SECRET_KEY,
            region_name=self.settings.SCALEWAY_REGION
        )
        
        self.bucket_name = self.settings.SCALEWAY_BUCKET_NAME
    
    async def check_connection(self) -> bool:
        """Sprawdzenie połączenia z Object Storage"""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            logger.error("Błąd połączenia z Scaleway Object Storage", error=str(e))
            return False
    
    async def upload_file(
        self, 
        file_content: bytes, 
        object_key: str, 
        content_type: str = 'application/octet-stream',
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload pliku do Object Storage
        
        Args:
            file_content: Zawartość pliku w bytes
            object_key: Klucz obiektu (ścieżka w bucket)
            content_type: Typ MIME pliku
            metadata: Dodatkowe metadane
            
        Returns:
            Dict z informacjami o uploadzie
        """
        try:
            upload_metadata = metadata or {}
            upload_metadata.update({
                'uploaded_at': datetime.now().isoformat(),
                'uploaded_by': 'hackathon-backend'
            })
            
            logger.info("Upload pliku do Object Storage",
                       object_key=object_key,
                       content_type=content_type,
                       size=len(file_content))
            
            response = self.client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_content,
                ContentType=content_type,
                Metadata=upload_metadata
            )
            
            # Generowanie URL do pliku
            file_url = f'https://{self.bucket_name}.s3.{self.settings.SCALEWAY_REGION}.scw.cloud/{object_key}'
            
            logger.info("Plik uploadowany pomyślnie",
                       object_key=object_key,
                       etag=response.get('ETag', ''),
                       url=file_url)
            
            return {
                'success': True,
                'object_key': object_key,
                'url': file_url,
                'etag': response.get('ETag', ''),
                'size': len(file_content),
                'content_type': content_type,
                'metadata': upload_metadata
            }
            
        except ClientError as e:
            logger.error("Błąd uploadu pliku", error=str(e), object_key=object_key)
            return {
                'success': False,
                'error': str(e),
                'object_key': object_key
            }
    
    async def download_file(self, object_key: str) -> Dict[str, Any]:
        """
        Download pliku z Object Storage
        
        Args:
            object_key: Klucz obiektu do pobrania
            
        Returns:
            Dict z zawartością pliku i metadanymi
        """
        try:
            logger.info("Download pliku z Object Storage", object_key=object_key)
            
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            content = response['Body'].read()
            
            return {
                'success': True,
                'content': content,
                'content_type': response.get('ContentType', ''),
                'content_length': response.get('ContentLength', 0),
                'last_modified': response.get('LastModified'),
                'metadata': response.get('Metadata', {}),
                'etag': response.get('ETag', '')
            }
            
        except ClientError as e:
            logger.error("Błąd downloadu pliku", error=str(e), object_key=object_key)
            return {
                'success': False,
                'error': str(e),
                'object_key': object_key
            }
    
    async def delete_file(self, object_key: str) -> Dict[str, Any]:
        """
        Usunięcie pliku z Object Storage
        
        Args:
            object_key: Klucz obiektu do usunięcia
            
        Returns:
            Dict z rezultatem operacji
        """
        try:
            logger.info("Usuwanie pliku z Object Storage", object_key=object_key)
            
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            return {
                'success': True,
                'object_key': object_key,
                'message': 'Plik usunięty pomyślnie'
            }
            
        except ClientError as e:
            logger.error("Błąd usuwania pliku", error=str(e), object_key=object_key)
            return {
                'success': False,
                'error': str(e),
                'object_key': object_key
            }
    
    async def list_files(self, prefix: str = '', max_keys: int = 1000) -> Dict[str, Any]:
        """
        Lista plików w bucket
        
        Args:
            prefix: Prefix do filtrowania plików
            max_keys: Maksymalna liczba plików do zwrócenia
            
        Returns:
            Dict z listą plików
        """
        try:
            logger.info("Lista plików w Object Storage",
                       prefix=prefix,
                       max_keys=max_keys)
            
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag'],
                    'storage_class': obj.get('StorageClass', 'STANDARD'),
                    'url': f'https://{self.bucket_name}.s3.{self.settings.SCALEWAY_REGION}.scw.cloud/{obj["Key"]}'
                })
            
            return {
                'success': True,
                'files': files,
                'count': len(files),
                'is_truncated': response.get('IsTruncated', False),
                'prefix': prefix
            }
            
        except ClientError as e:
            logger.error("Błąd listowania plików", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'files': []
            }
    
    async def generate_presigned_url(
        self, 
        object_key: str, 
        operation: str = 'get_object',
        expiration: int = 3600
    ) -> Dict[str, Any]:
        """
        Generowanie presigned URL dla pliku
        
        Args:
            object_key: Klucz obiektu
            operation: Typ operacji ('get_object', 'put_object')
            expiration: Czas wygaśnięcia URL w sekundach
            
        Returns:
            Dict z presigned URL
        """
        try:
            logger.info("Generowanie presigned URL",
                       object_key=object_key,
                       operation=operation,
                       expiration=expiration)
            
            url = self.client.generate_presigned_url(
                operation,
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            
            return {
                'success': True,
                'url': url,
                'object_key': object_key,
                'operation': operation,
                'expires_in': expiration,
                'expires_at': (datetime.now().timestamp() + expiration)
            }
            
        except ClientError as e:
            logger.error("Błąd generowania presigned URL", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'object_key': object_key
            }
    
    async def upload_document_for_rag(
        self, 
        document_content: str, 
        document_title: str,
        source_reference: str = None
    ) -> Dict[str, Any]:
        """
        Upload dokumentu specjalnie dla systemu RAG
        
        Args:
            document_content: Zawartość dokumentu
            document_title: Tytuł dokumentu
            source_reference: Referencja źródła
            
        Returns:
            Dict z informacjami o uploadzie
        """
        try:
            # Generowanie klucza obiektu
            timestamp = datetime.now().strftime('%Y/%m/%d')
            safe_title = "".join(c for c in document_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            object_key = f'documents/rag/{timestamp}/{safe_title}.txt'
            
            # Metadane specyficzne dla RAG
            metadata = {
                'document_title': document_title,
                'source_reference': source_reference or 'manual_upload',
                'content_type': 'rag_document',
                'processed': 'false'
            }
            
            # Upload jako text/plain
            content_bytes = document_content.encode('utf-8')
            
            result = await self.upload_file(
                file_content=content_bytes,
                object_key=object_key,
                content_type='text/plain; charset=utf-8',
                metadata=metadata
            )
            
            if result['success']:
                logger.info("Dokument RAG uploadowany pomyślnie",
                           title=document_title,
                           object_key=object_key)
            
            return result
            
        except Exception as e:
            logger.error("Błąd uploadu dokumentu RAG", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'document_title': document_title
            }