"""
FastAPI application for EzDB REST API server
"""
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict
import logging
import os
import io
import csv

from ezdb import EzDB, SimilarityMetric
from ezdb.embeddings import EmbeddingFunction, default_embedding_function, CLIPEmbedding
from .models import (
    InsertRequest, InsertResponse,
    BatchInsertRequest, BatchInsertResponse,
    SearchRequest, SearchResponse, SearchResultItem,
    DocumentSearchRequest,
    GetResponse, UpdateRequest, UpdateResponse,
    UpsertRequest, UpsertResponse,
    DeleteResponse, StatsResponse,
    CreateCollectionRequest, CreateCollectionResponse,
    ListCollectionsResponse, ErrorResponse,
    SQLQueryRequest, SQLQueryResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollectionManager:
    """Manages multiple collections (databases) with optional embedding functions"""

    def __init__(self):
        self.collections: Dict[str, EzDB] = {}
        self.embedding_functions: Dict[str, EmbeddingFunction] = {}
        # Create default collection
        self.collections["default"] = EzDB(dimension=384, metric=SimilarityMetric.COSINE)
        logger.info("Initialized default collection with dimension 384")

    def get_collection(self, name: str) -> EzDB:
        """Get a collection by name"""
        if name not in self.collections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{name}' not found"
            )
        return self.collections[name]

    def get_embedding_function(self, name: str) -> EmbeddingFunction:
        """Get embedding function for a collection"""
        return self.embedding_functions.get(name)

    def create_collection(
        self,
        name: str,
        dimension: int = None,
        metric: str = "cosine",
        index_type: str = "hnsw",
        embedding_function: str = None
    ) -> EzDB:
        """Create a new collection"""
        if name in self.collections:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Collection '{name}' already exists"
            )

        # Handle embedding function
        embedding_fn = None
        if embedding_function:
            try:
                if embedding_function == "default":
                    embedding_fn = default_embedding_function()
                else:
                    # Parse format: provider/model or just provider
                    parts = embedding_function.split("/")
                    provider = parts[0]
                    model_name = parts[1] if len(parts) > 1 else None

                    from ezdb.embeddings import create_embedding_function
                    embedding_fn = create_embedding_function(provider, model_name)

                # Store embedding function
                self.embedding_functions[name] = embedding_fn

                # Use embedding dimension if dimension not provided
                if dimension is None:
                    dimension = embedding_fn.dimension()

                logger.info(f"Collection '{name}' will use embedding function: {embedding_fn.name()}")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to initialize embedding function: {str(e)}"
                )

        # Require dimension if no embedding function
        if dimension is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either dimension or embedding_function must be provided"
            )

        self.collections[name] = EzDB(
            dimension=dimension,
            metric=metric,
            index_type=index_type
        )
        logger.info(f"Created collection '{name}' with dimension {dimension}")
        return self.collections[name]

    def list_collections(self):
        """List all collection names"""
        return list(self.collections.keys())

    def delete_collection(self, name: str):
        """Delete a collection"""
        if name == "default":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete default collection"
            )
        if name not in self.collections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{name}' not found"
            )
        del self.collections[name]
        if name in self.embedding_functions:
            del self.embedding_functions[name]
        logger.info(f"Deleted collection '{name}'")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="EzDB API",
        description="REST API for EzDB Vector Database",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize collection manager
    manager = CollectionManager()

    # Mount static files
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Vector DB Dashboard endpoint (previously main dashboard at /)
    @app.get("/vectordb", response_class=HTMLResponse, tags=["Dashboard"])
    async def vectordb_dashboard():
        """Web-based dashboard for managing EzDB Vector Database"""
        dashboard_path = os.path.join(static_dir, "dashboard.html")
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r') as f:
                return f.read()
        return HTMLResponse("<h1>Vector DB Dashboard not found</h1>", status_code=404)

    # Health check endpoint
    @app.get("/", tags=["Health"])
    async def root():
        """Health check endpoint"""
        return {
            "service": "EzDB API",
            "version": "0.1.0",
            "status": "running",
            "dashboards": {
                "main": "/dashboard",
                "vectordb": "/vectordb",
                "rdbms": "/rdbms"
            }
        }

    @app.get("/health", tags=["Health"])
    async def health():
        """Detailed health check"""
        return {
            "status": "healthy",
            "collections": len(manager.collections),
            "total_vectors": sum(db.size() for db in manager.collections.values())
        }

    # Collection management endpoints
    @app.post(
        "/collections",
        response_model=CreateCollectionResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["Collections"]
    )
    async def create_collection(request: CreateCollectionRequest):
        """Create a new collection"""
        try:
            manager.create_collection(
                name=request.name,
                dimension=request.dimension,
                metric=request.metric,
                index_type=request.index_type,
                embedding_function=request.embedding_function
            )
            return CreateCollectionResponse(name=request.name, success=True)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get(
        "/collections",
        response_model=ListCollectionsResponse,
        tags=["Collections"]
    )
    async def list_collections():
        """List all collections"""
        collections = manager.list_collections()
        return ListCollectionsResponse(
            collections=collections,
            count=len(collections)
        )

    @app.delete(
        "/collections/{collection_name}",
        tags=["Collections"]
    )
    async def delete_collection(collection_name: str):
        """Delete a collection"""
        try:
            manager.delete_collection(collection_name)
            return {"success": True, "message": f"Collection '{collection_name}' deleted"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # Vector operations endpoints
    @app.post(
        "/collections/{collection_name}/insert",
        response_model=InsertResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["Vectors"]
    )
    async def insert_vector(collection_name: str, request: InsertRequest):
        """Insert a vector into the collection"""
        try:
            db = manager.get_collection(collection_name)

            # Handle text-to-vector or image-to-vector conversion
            vector = request.vector
            document = request.document  # Use document from request

            if vector is None and request.text is not None:
                # Use embedding function for text
                embedding_fn = manager.get_embedding_function(collection_name)
                if embedding_fn is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Collection '{collection_name}' does not have an embedding function configured. "
                               "Either provide a vector or create the collection with an embedding_function."
                    )
                vector = embedding_fn.embed(request.text)[0].tolist()
                document = request.text  # Store original text as document
                logger.info(f"Auto-embedded text to vector for '{collection_name}'")
            elif vector is None and request.image is not None:
                # Use embedding function for image (must be CLIP)
                embedding_fn = manager.get_embedding_function(collection_name)
                if embedding_fn is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Collection '{collection_name}' does not have an embedding function configured. "
                               "Create collection with embedding_function='clip' for image support."
                    )
                if not isinstance(embedding_fn, CLIPEmbedding):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Collection '{collection_name}' does not support images. "
                               "Create collection with embedding_function='clip' for multimodal support."
                    )
                vector = embedding_fn.embed_images(request.image)[0].tolist()
                document = f"[Image: {request.image[:50]}...]" if len(request.image) > 50 else f"[Image: {request.image}]"
                logger.info(f"Auto-embedded image to vector for '{collection_name}'")
            elif vector is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Either 'vector', 'text', or 'image' must be provided"
                )

            vector_id = db.insert(
                vector=vector,
                metadata=request.metadata,
                id=request.id,
                document=document
            )
            logger.info(f"Inserted vector {vector_id} into '{collection_name}'")
            return InsertResponse(id=vector_id, success=True)
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error inserting vector: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post(
        "/collections/{collection_name}/insert_batch",
        response_model=BatchInsertResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["Vectors"]
    )
    async def insert_batch(collection_name: str, request: BatchInsertRequest):
        """Insert multiple vectors into the collection"""
        try:
            db = manager.get_collection(collection_name)
            ids = db.insert_batch(
                vectors=request.vectors,
                metadata_list=request.metadata_list,
                ids=request.ids
            )
            logger.info(f"Batch inserted {len(ids)} vectors into '{collection_name}'")
            return BatchInsertResponse(
                ids=ids,
                count=len(ids),
                success=True
            )
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error batch inserting vectors: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post(
        "/collections/{collection_name}/search",
        response_model=SearchResponse,
        tags=["Vectors"]
    )
    async def search_vectors(collection_name: str, request: SearchRequest):
        """Search for similar vectors"""
        try:
            db = manager.get_collection(collection_name)

            # Handle text-to-vector or image-to-vector conversion
            query_vector = request.vector
            if query_vector is None and request.text is not None:
                # Use embedding function for text
                embedding_fn = manager.get_embedding_function(collection_name)
                if embedding_fn is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Collection '{collection_name}' does not have an embedding function configured. "
                               "Either provide a vector or create the collection with an embedding_function."
                    )
                query_vector = embedding_fn.embed(request.text)[0].tolist()
                logger.info(f"Auto-embedded query text to vector for '{collection_name}'")
            elif query_vector is None and request.image is not None:
                # Use embedding function for image (must be CLIP)
                embedding_fn = manager.get_embedding_function(collection_name)
                if embedding_fn is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Collection '{collection_name}' does not have an embedding function configured. "
                               "Create collection with embedding_function='clip' for image support."
                    )
                if not isinstance(embedding_fn, CLIPEmbedding):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Collection '{collection_name}' does not support images. "
                               "Create collection with embedding_function='clip' for multimodal support."
                    )
                query_vector = embedding_fn.embed_images(request.image)[0].tolist()
                logger.info(f"Auto-embedded query image to vector for '{collection_name}'")
            elif query_vector is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Either 'vector', 'text', or 'image' must be provided"
                )

            results = db.search(
                query_vector=query_vector,
                top_k=request.top_k,
                filters=request.filters,
                ef=request.ef
            )

            # Convert to response model
            result_items = [
                SearchResultItem(
                    id=r.id,
                    score=r.score,
                    metadata=r.metadata,
                    vector=r.vector.tolist(),
                    document=r.document
                )
                for r in results
            ]

            logger.info(f"Search in '{collection_name}' returned {len(results)} results")
            return SearchResponse(
                results=result_items,
                count=len(result_items),
                success=True
            )
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post(
        "/collections/{collection_name}/search_documents",
        response_model=SearchResponse,
        tags=["Vectors"]
    )
    async def search_documents(collection_name: str, request: DocumentSearchRequest):
        """Full-text search on stored documents"""
        try:
            db = manager.get_collection(collection_name)

            results = db.search_documents(
                query=request.query,
                top_k=request.top_k,
                case_sensitive=request.case_sensitive,
                filters=request.filters
            )

            # Convert to response model
            result_items = [
                SearchResultItem(
                    id=r.id,
                    score=r.score,
                    metadata=r.metadata,
                    vector=r.vector.tolist(),
                    document=r.document
                )
                for r in results
            ]

            logger.info(f"Document search in '{collection_name}' returned {len(results)} results")
            return SearchResponse(
                results=result_items,
                count=len(result_items),
                success=True
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get(
        "/collections/{collection_name}/vectors/{vector_id}",
        response_model=GetResponse,
        tags=["Vectors"]
    )
    async def get_vector(collection_name: str, vector_id: str):
        """Get a vector by ID"""
        try:
            db = manager.get_collection(collection_name)
            result = db.get(vector_id)

            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Vector '{vector_id}' not found"
                )

            return GetResponse(
                id=result['id'],
                vector=result['vector'].tolist(),
                metadata=result['metadata'],
                document=result.get('document'),
                success=True
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting vector: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.put(
        "/collections/{collection_name}/vectors/{vector_id}",
        response_model=UpdateResponse,
        tags=["Vectors"]
    )
    async def update_vector(collection_name: str, vector_id: str, request: UpdateRequest):
        """Update an existing vector's data, metadata, or document"""
        try:
            db = manager.get_collection(collection_name)

            # Handle text-to-vector or image-to-vector conversion
            vector = request.vector
            document = request.document
            if vector is None and request.text is not None:
                # Use embedding function for text
                embedding_fn = manager.get_embedding_function(collection_name)
                if embedding_fn is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Collection '{collection_name}' does not have an embedding function configured. "
                               "Either provide a vector or create the collection with an embedding_function."
                    )
                vector = embedding_fn.embed(request.text)[0].tolist()
                document = request.text  # Store original text as document
                logger.info(f"Auto-embedded text to vector for '{collection_name}'")
            elif vector is None and request.image is not None:
                # Use embedding function for image (must be CLIP)
                embedding_fn = manager.get_embedding_function(collection_name)
                if embedding_fn is None or not isinstance(embedding_fn, CLIPEmbedding):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Collection '{collection_name}' does not support images. "
                               "Create collection with embedding_function='clip' for multimodal support."
                    )
                vector = embedding_fn.embed_images(request.image)[0].tolist()
                document = f"[Image: {request.image[:50]}...]" if len(request.image) > 50 else f"[Image: {request.image}]"
                logger.info(f"Auto-embedded image to vector for '{collection_name}'")

            success = db.update(
                id=vector_id,
                vector=vector,
                metadata=request.metadata,
                document=document
            )

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Vector '{vector_id}' not found"
                )

            logger.info(f"Updated vector {vector_id} in '{collection_name}'")
            return UpdateResponse(id=vector_id, success=True)
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error updating vector: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post(
        "/collections/{collection_name}/upsert",
        response_model=UpsertResponse,
        tags=["Vectors"]
    )
    async def upsert_vector(collection_name: str, request: UpsertRequest):
        """Insert or update a vector (upsert)"""
        try:
            db = manager.get_collection(collection_name)

            # Handle text-to-vector or image-to-vector conversion
            vector = request.vector
            document = request.document
            if vector is None and request.text is not None:
                # Use embedding function for text
                embedding_fn = manager.get_embedding_function(collection_name)
                if embedding_fn is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Collection '{collection_name}' does not have an embedding function configured. "
                               "Either provide a vector or create the collection with an embedding_function."
                    )
                vector = embedding_fn.embed(request.text)[0].tolist()
                document = request.text  # Store original text as document
                logger.info(f"Auto-embedded text to vector for '{collection_name}'")
            elif vector is None and request.image is not None:
                # Use embedding function for image (must be CLIP)
                embedding_fn = manager.get_embedding_function(collection_name)
                if embedding_fn is None or not isinstance(embedding_fn, CLIPEmbedding):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Collection '{collection_name}' does not support images. "
                               "Create collection with embedding_function='clip' for multimodal support."
                    )
                vector = embedding_fn.embed_images(request.image)[0].tolist()
                document = f"[Image: {request.image[:50]}...]" if len(request.image) > 50 else f"[Image: {request.image}]"
                logger.info(f"Auto-embedded image to vector for '{collection_name}'")
            elif vector is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Either 'vector', 'text', or 'image' must be provided"
                )

            vector_id, was_update = db.upsert(
                vector=vector,
                id=request.id,
                metadata=request.metadata,
                document=document
            )

            action = "Updated" if was_update else "Inserted"
            logger.info(f"{action} vector {vector_id} in '{collection_name}'")
            return UpsertResponse(id=vector_id, updated=was_update, success=True)
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error upserting vector: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.delete(
        "/collections/{collection_name}/vectors/{vector_id}",
        response_model=DeleteResponse,
        tags=["Vectors"]
    )
    async def delete_vector(collection_name: str, vector_id: str):
        """Delete a vector by ID"""
        try:
            db = manager.get_collection(collection_name)
            success = db.delete(vector_id)

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Vector '{vector_id}' not found"
                )

            logger.info(f"Deleted vector {vector_id} from '{collection_name}'")
            return DeleteResponse(id=vector_id, success=True)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting vector: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get(
        "/collections/{collection_name}/stats",
        response_model=StatsResponse,
        tags=["Collections"]
    )
    async def get_stats(collection_name: str):
        """Get collection statistics"""
        try:
            db = manager.get_collection(collection_name)
            stats = db.stats()
            return StatsResponse(**stats)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get(
        "/collections/{collection_name}/vectors",
        tags=["Vectors"]
    )
    async def list_vectors(collection_name: str, limit: int = 100, offset: int = 0):
        """List all vectors in a collection with pagination"""
        try:
            db = manager.get_collection(collection_name)

            # Get all IDs, vectors, metadata, and documents
            all_ids = db.store.get_all_ids()
            all_metadata = db.store.get_all_metadata()
            all_vectors = db.store.get_all_vectors()
            all_documents = db.store.get_all_documents()

            total = len(all_ids)

            # Apply pagination
            start = offset
            end = min(offset + limit, total)

            vectors_list = []
            for i in range(start, end):
                vector_item = {
                    "id": all_ids[i],
                    "metadata": all_metadata[i],
                    "vector": all_vectors[i].tolist()[:5]  # Only show first 5 dimensions
                }
                if all_documents[i] is not None:
                    vector_item["document"] = all_documents[i]
                vectors_list.append(vector_item)

            return {
                "vectors": vectors_list,
                "total": total,
                "limit": limit,
                "offset": offset,
                "success": True
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error listing vectors: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post(
        "/sql/query",
        response_model=SQLQueryResponse,
        tags=["SQL"]
    )
    async def execute_sql_query(request: SQLQueryRequest):
        """
        Execute SQL-like queries on collection metadata.

        Supported syntax:
        - SELECT * FROM collection_name
        - SELECT column1, column2 FROM collection_name
        - WHERE conditions with operators: =, !=, <, >, <=, >=, LIKE, IN
        - ORDER BY column ASC/DESC
        - LIMIT and OFFSET

        Example queries:
        - SELECT * FROM movie_ratings
        - SELECT title, year, rating FROM movie_ratings WHERE rating >= 8.0
        - SELECT * FROM movie_ratings WHERE genre = 'Action' ORDER BY rating DESC LIMIT 10
        - SELECT * FROM movie_ratings WHERE year >= 2010 AND rating > 7.5
        """
        try:
            from ezdb.sql_parser import SQLExecutor

            executor = SQLExecutor(manager)
            result = executor.execute(request.query)

            logger.info(f"Executed SQL query: {request.query}")
            logger.info(f"Returned {result['returned']} of {result['total']} rows")

            return SQLQueryResponse(
                columns=result['columns'],
                rows=result['rows'],
                total=result['total'],
                returned=result['returned'],
                query=request.query,
                success=True
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error executing SQL query: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get(
        "/collections/{collection_name}/export/csv",
        tags=["SQL"]
    )
    async def download_collection_csv(collection_name: str, query: str = None):
        """
        Download collection data as CSV file.

        Args:
            collection_name: Name of collection to export
            query: Optional SQL query to filter data (e.g., "SELECT * FROM collection WHERE rating >= 8.0")

        Returns:
            CSV file with collection data
        """
        try:
            from ezdb.sql_parser import SQLExecutor

            # If no query provided, select all
            if not query:
                query = f"SELECT * FROM {collection_name}"

            executor = SQLExecutor(manager)
            result = executor.execute(query)

            # Create CSV in memory
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=result['columns'])
            writer.writeheader()
            writer.writerows(result['rows'])

            # Create response
            csv_content = output.getvalue()
            output.close()

            logger.info(f"Exported {result['returned']} rows from '{collection_name}' to CSV")

            return StreamingResponse(
                io.BytesIO(csv_content.encode('utf-8')),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={collection_name}.csv"
                }
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post(
        "/collections/{collection_name}/import/csv",
        tags=["SQL"]
    )
    async def upload_collection_csv(
        collection_name: str,
        file: UploadFile = File(...),
        text_column: str = Form(None)
    ):
        """
        Upload CSV file to populate collection.

        The CSV file should have:
        - One row per item
        - Columns become metadata fields
        - If text_column is specified, that column will be auto-embedded
        - If text_column is not specified, you must provide 'vector' column with JSON array

        Args:
            collection_name: Name of collection to import into
            file: CSV file to upload
            text_column: Name of column to use for auto-embedding (optional)

        Returns:
            Success response with count of imported rows
        """
        try:
            db = manager.get_collection(collection_name)
            embedding_fn = manager.get_embedding_function(collection_name)

            # Read CSV file
            contents = await file.read()
            csv_text = contents.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_text))

            rows = list(csv_reader)
            if not rows:
                raise ValueError("CSV file is empty")

            logger.info(f"Importing {len(rows)} rows from CSV to '{collection_name}'")

            # Process each row
            imported_count = 0
            for i, row in enumerate(rows):
                try:
                    # Extract ID if present
                    vector_id = row.pop('id', None)

                    # Handle vector/text
                    vector = None
                    document = None

                    if text_column and text_column in row:
                        # Auto-embed from text column
                        text = row[text_column]
                        if embedding_fn is None:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Collection '{collection_name}' has no embedding function. "
                                       "Either provide vectors or create collection with embedding_function."
                            )
                        vector = embedding_fn.embed(text)[0].tolist()
                        document = text
                    elif 'vector' in row:
                        # Use provided vector
                        import json
                        vector = json.loads(row.pop('vector'))
                    else:
                        raise ValueError(
                            f"Row {i+1}: Must either specify text_column or include 'vector' column"
                        )

                    # Remaining columns become metadata
                    metadata = {k: v for k, v in row.items() if k != text_column}

                    # Convert numeric strings to numbers
                    for key, value in metadata.items():
                        if value.isdigit():
                            metadata[key] = int(value)
                        else:
                            try:
                                metadata[key] = float(value)
                            except ValueError:
                                pass  # Keep as string

                    # Insert into database
                    db.insert(
                        vector=vector,
                        metadata=metadata,
                        id=vector_id,
                        document=document
                    )
                    imported_count += 1

                except Exception as e:
                    logger.warning(f"Error importing row {i+1}: {e}")
                    continue

            logger.info(f"Successfully imported {imported_count} rows into '{collection_name}'")

            return {
                "success": True,
                "imported": imported_count,
                "total": len(rows),
                "message": f"Imported {imported_count} of {len(rows)} rows"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error importing CSV: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # RDBMS endpoints
    from ezdb.rdbms.executor import RDBMSEngine

    # Initialize RDBMS engine (global for app lifespan)
    # Point to the EzDB database file in the current directory
    # Enable auto-vectorization for semantic search on TEXT columns
    # Using SQLite backend for production-ready performance
    rdbms_engine = RDBMSEngine(
        db_file='/Users/utpalraina/Documents/AI/EzDB/EzDB_database.db',
        auto_vectorization=True,
        backend='sqlite'  # Use SQLite for better performance and scalability
    )

    @app.get("/rdbms", response_class=HTMLResponse, tags=["RDBMS"])
    async def rdbms_dashboard():
        """Dark theme SQL Developer interface for RDBMS"""
        dashboard_path = os.path.join(static_dir, "rdbms.html")
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r') as f:
                return f.read()
        return HTMLResponse("<h1>RDBMS Dashboard not found</h1>", status_code=404)

    @app.get("/rdbms/pymagic", response_class=HTMLResponse, tags=["RDBMS"])
    async def rdbms_pymagic_dashboard():
        """PyMagic - Oracle-style SQL Worksheet + Python Functions interface"""
        dashboard_path = os.path.join(static_dir, "rdbms_oracle.html")
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r') as f:
                return f.read()
        return HTMLResponse("<h1>RDBMS Dashboard not found</h1>", status_code=404)

    @app.get("/rdbms/tables", tags=["RDBMS"])
    async def list_rdbms_tables():
        """List all RDBMS tables and views"""
        try:
            # Get tables
            tables = rdbms_engine.list_tables()
            table_info = []

            for table_name in tables:
                stats = rdbms_engine.table_stats(table_name)
                table_info.append(stats)

            # Get views
            views = []
            for view_name in rdbms_engine.views.keys():
                views.append({
                    'name': view_name,
                    'type': 'view',
                    'rows': 0  # Views don't have row counts
                })

            return {
                "success": True,
                "tables": table_info,
                "views": views,
                "count": len(tables) + len(views)
            }
        except Exception as e:
            logger.error(f"Error listing RDBMS tables: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get("/rdbms/tables/{table_name}/schema", tags=["RDBMS"])
    async def get_rdbms_table_schema(table_name: str):
        """Get schema for a specific table"""
        try:
            schema = rdbms_engine.get_table_schema(table_name)
            if not schema:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Table '{table_name}' not found"
                )

            return {
                "success": True,
                "schema": schema.to_dict()
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting table schema: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post("/rdbms/execute", tags=["RDBMS"])
    async def execute_rdbms_query(request: Dict[str, str]):
        """
        Execute an RDBMS SQL query.

        Supported SQL:
        - CREATE TABLE with VECTOR datatype
        - INSERT INTO with vector arrays
        - SELECT with WHERE, ORDER BY, LIMIT
        - UPDATE and DELETE
        - Vector similarity functions
        """
        try:
            sql = request.get("sql")
            if not sql:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="SQL query is required"
                )

            result = rdbms_engine.execute(sql)

            logger.info(f"Executed RDBMS query: {sql[:100]}...")
            return result

        except HTTPException:
            raise
        except ValueError as e:
            logger.error(f"RDBMS query ValueError: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error executing RDBMS query: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get("/rdbms/tables/{table_name}/data", tags=["RDBMS"])
    async def get_rdbms_table_data(table_name: str, limit: int = 100, offset: int = 0):
        """Get data from a specific table with pagination"""
        try:
            result = rdbms_engine.execute(
                f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"
            )

            # Also get total count
            table = rdbms_engine.get_table(table_name)
            total = table.size() if table else 0

            return {
                **result,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Error getting table data: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post("/rdbms/python/create_function", tags=["RDBMS"])
    async def create_python_function(request: Dict[str, str]):
        """
        Create a Python stored function in the database.

        Similar to Oracle PL/SQL packages, this allows you to store Python code
        in the database and reuse it across operations.

        Request body:
        {
            "function_name": "calculate_tax",
            "python_code": "def calculate_tax(salary): ...",
            "function_type": "FUNCTION",  # or "PROCEDURE"
            "parameters": "salary INTEGER",  # optional
            "return_type": "INTEGER",  # optional
            "description": "Calculate tax based on salary"  # optional
        }
        """
        try:
            function_name = request.get("function_name")
            python_code = request.get("python_code")
            function_type = request.get("function_type", "FUNCTION")
            parameters = request.get("parameters")
            return_type = request.get("return_type")
            description = request.get("description")

            if not function_name or not python_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="function_name and python_code are required"
                )

            # Create the function using the storage backend
            if rdbms_engine.backend_type == 'sqlite':
                rdbms_engine.storage.store.create_python_function(
                    function_name=function_name,
                    function_type=function_type,
                    python_code=python_code,
                    parameters=parameters,
                    return_type=return_type,
                    description=description,
                    or_replace=True  # Allow updating existing functions
                )

                logger.info(f"Created Python {function_type.lower()}: {function_name}()")
                return {
                    "success": True,
                    "function_name": function_name,
                    "function_type": function_type,
                    "message": f"Successfully created Python {function_type.lower()}: {function_name}()"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Python functions are only supported with SQLite backend"
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating Python function: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post("/rdbms/python/execute", tags=["RDBMS"])
    async def execute_python_code(request: Dict[str, str]):
        """
        Execute Python code with automatic database connection.

        The code runs with pre-configured database access:
        - db: RDBMSEngine instance
        - execute(sql): Execute SQL and return results
        - tables: List of all table names
        - get_table(name): Get a specific table

        Example:
        ```python
        # Query employees directly
        result = execute("SELECT * FROM employees WHERE salary > 50000")
        for row in result['rows']:
            print(row['name'], row['salary'])

        # Access table object
        employees = get_table('employees')
        print(f"Total employees: {employees.size()}")
        ```
        """
        try:
            python_code = request.get("python_code")
            if not python_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="python_code is required"
                )

            # Create execution environment with database access
            exec_globals = {
                '__builtins__': __builtins__,
                'db': rdbms_engine,
                'execute': lambda sql: rdbms_engine.execute(sql),
                'tables': rdbms_engine.list_tables(),
                'get_table': lambda name: rdbms_engine.get_table(name),
                'print': print,  # Allow print statements
            }

            # Capture output
            import io
            import sys
            output_buffer = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = output_buffer

            try:
                # Execute the Python code
                exec(python_code, exec_globals)

                # Restore stdout
                sys.stdout = old_stdout
                output = output_buffer.getvalue()

                logger.info(f"Executed Python code successfully")
                return {
                    "success": True,
                    "output": output if output else "Code executed successfully (no output)",
                    "message": "Python code executed successfully"
                }

            except Exception as exec_error:
                # Restore stdout
                sys.stdout = old_stdout
                raise Exception(f"Execution error: {str(exec_error)}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error executing Python code: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    @app.get("/rdbms/python/functions", tags=["RDBMS"])
    async def list_python_functions():
        """List all Python stored functions in the database"""
        try:
            if rdbms_engine.backend_type == 'sqlite':
                functions = rdbms_engine.storage.store.get_all_python_functions()

                return {
                    "success": True,
                    "functions": functions,
                    "count": len(functions)
                }
            else:
                return {
                    "success": True,
                    "functions": [],
                    "count": 0,
                    "message": "Python functions are only supported with SQLite backend"
                }

        except Exception as e:
            logger.error(f"Error listing Python functions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # Main Dashboard - Dual Architecture (RDBMS + Vector DB)
    @app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
    async def main_dashboard():
        """Main unified dashboard showing RDBMS + Vector DB dual architecture"""
        dashboard_path = os.path.join(static_dir, "dual_architecture.html")
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r') as f:
                return f.read()
        return HTMLResponse("<h1>Dashboard not found</h1>", status_code=404)

    # Legacy route redirect (for backwards compatibility)
    @app.get("/rdbms/dual-architecture", tags=["RDBMS"])
    async def dual_architecture_dashboard_redirect():
        """Legacy route - redirects to /dashboard"""
        return RedirectResponse(url="/dashboard", status_code=301)

    @app.get("/rdbms/auto-vectorization/status", tags=["RDBMS"])
    async def get_auto_vectorization_status():
        """Get auto-vectorization status for all tables"""
        try:
            if not rdbms_engine.auto_vectorizer:
                return {
                    "success": True,
                    "enabled": False,
                    "message": "Auto-vectorization is not enabled"
                }

            vectorizer = rdbms_engine.auto_vectorizer
            tables_info = []

            # Get all tables
            for table_name in rdbms_engine.list_tables():
                table = rdbms_engine.get_table(table_name)
                schema = table.schema

                # Check if table has TEXT columns
                text_columns = [col.name for col in schema.columns if col.data_type.value == 'TEXT']

                # Check if vector collection exists
                collection_name = f"{table_name}_vectors"
                has_vectors = collection_name in vectorizer.vector_collections

                if has_vectors:
                    vector_db = vectorizer.vector_collections[collection_name]
                    vector_count = vector_db.size()
                else:
                    vector_count = 0

                tables_info.append({
                    "table_name": table_name,
                    "rows": table.size(),
                    "text_columns": text_columns,
                    "has_vectors": has_vectors,
                    "vector_count": vector_count,
                    "vectorized_columns": text_columns if has_vectors else []
                })

            return {
                "success": True,
                "enabled": True,
                "dimension": vectorizer.dimension,
                "model": vectorizer.embedding_model_name,
                "tables": tables_info,
                "total_tables": len(tables_info),
                "vectorized_tables": sum(1 for t in tables_info if t['has_vectors'])
            }
        except Exception as e:
            logger.error(f"Error getting auto-vectorization status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get("/rdbms/json-indexes", tags=["RDBMS"])
    async def list_json_indexes():
        """List all JSON path indexes across all tables"""
        try:
            all_indexes = []

            for table_name in rdbms_engine.list_tables():
                table = rdbms_engine.get_table(table_name)

                # Get JSON indexes for this table
                indexes = table.json_indexes.list_indexes()

                for idx in indexes:
                    all_indexes.append({
                        "table_name": table_name,
                        "column": idx['column'],
                        "path": idx['path'],
                        "size": idx['size'],
                        "full_path": f"{table_name}.{idx['column']}.{idx['path']}"
                    })

            return {
                "success": True,
                "indexes": all_indexes,
                "count": len(all_indexes)
            }
        except Exception as e:
            logger.error(f"Error listing JSON indexes: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post("/rdbms/json-indexes/create", tags=["RDBMS"])
    async def create_json_index(request: Dict[str, str]):
        """
        Create a new JSON path index.

        Request body:
        {
            "table_name": "products",
            "column_name": "metadata",
            "path": "brand"
        }
        """
        try:
            table_name = request.get("table_name")
            column_name = request.get("column_name")
            path = request.get("path")

            if not all([table_name, column_name, path]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="table_name, column_name, and path are required"
                )

            table = rdbms_engine.get_table(table_name)
            if not table:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Table '{table_name}' not found"
                )

            # Create the index
            index = table.create_json_index(column_name, path)

            logger.info(f"Created JSON index on {table_name}.{column_name}.{path}")
            return {
                "success": True,
                "message": f"Created index on {table_name}.{column_name}.{path}",
                "size": index.size()
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating JSON index: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post("/rdbms/hybrid-search", tags=["RDBMS"])
    async def hybrid_search(request: Dict):
        """
        Execute a hybrid search combining semantic, SQL, and JSON filters.

        Request body:
        {
            "table_name": "products",
            "query_text": "gaming laptop",
            "top_k": 10,
            "sql_filters": {
                "price": {"$lt": 1500},
                "metadata.rating": {"$gte": 4.5}
            }
        }
        """
        try:
            if not rdbms_engine.auto_vectorizer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Auto-vectorization is not enabled. Cannot perform hybrid search."
                )

            table_name = request.get("table_name")
            query_text = request.get("query_text")
            top_k = request.get("top_k", 10)
            sql_filters = request.get("sql_filters", {})

            if not table_name or not query_text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="table_name and query_text are required"
                )

            # Perform hybrid search
            results = rdbms_engine.auto_vectorizer.hybrid_search(
                table_name=table_name,
                query_text=query_text,
                top_k=top_k,
                sql_filters=sql_filters,
                rdbms_executor=rdbms_engine
            )

            logger.info(f"Hybrid search on '{table_name}' returned {len(results)} results")
            return {
                "success": True,
                "results": results,
                "count": len(results),
                "table_name": table_name,
                "query_text": query_text
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error performing hybrid search: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get("/rdbms/vector-collections", tags=["RDBMS"])
    async def list_vector_collections():
        """List all vector collections created by auto-vectorization"""
        try:
            if not rdbms_engine.auto_vectorizer:
                return {
                    "success": True,
                    "enabled": False,
                    "collections": [],
                    "model": None
                }

            vectorizer = rdbms_engine.auto_vectorizer
            collections = []

            for collection_name, vector_db in vectorizer.vector_collections.items():
                # Extract table name from collection name
                table_name = collection_name.replace('_vectors', '')

                # Get the table to find text columns
                table = rdbms_engine.get_table(table_name)
                text_columns = []
                if table:
                    text_columns = [col.name for col in table.schema.columns if col.data_type.value == 'TEXT']

                collections.append({
                    "collection_name": collection_name,
                    "table_name": table_name,
                    "vector_count": vector_db.size(),
                    "dimension": vector_db.dimension,
                    "metric": vector_db.metric.value if hasattr(vector_db.metric, 'value') else str(vector_db.metric),
                    "text_columns": text_columns
                })

            return {
                "success": True,
                "enabled": True,
                "model": vectorizer.embedding_model_name,
                "dimension": vectorizer.dimension,
                "collections": collections,
                "count": len(collections)
            }
        except Exception as e:
            logger.error(f"Error listing vector collections: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get("/rdbms/vector-collections/{collection_name}/vectors", tags=["RDBMS"])
    async def get_rdbms_vectors(collection_name: str, limit: int = 50, offset: int = 0):
        """Get vectors from an RDBMS collection with pagination"""
        try:
            if not rdbms_engine.auto_vectorizer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Auto-vectorization is not enabled"
                )

            vectorizer = rdbms_engine.auto_vectorizer

            # Check if collection exists
            if collection_name not in vectorizer.vector_collections:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"RDBMS collection '{collection_name}' not found"
                )

            # Get the vector database
            vector_db = vectorizer.vector_collections[collection_name]

            # Extract table name
            table_name = collection_name.replace('_vectors', '')
            table = rdbms_engine.get_table(table_name)

            # Get all vectors, IDs, and metadata
            all_ids = vector_db.store.get_all_ids()
            all_vectors = vector_db.store.get_all_vectors()
            all_metadata = vector_db.store.get_all_metadata()

            total = len(all_ids)

            # Apply pagination
            start = offset
            end = min(offset + limit, total)

            vectors_list = []
            for i in range(start, end):
                # Get row data from table if available
                row_data = None
                if table and i < table.size():
                    row_data = table.get(i)

                vector_item = {
                    "id": str(i),  # Use row index as ID
                    "row_id": i,
                    "metadata": all_metadata[i] if all_metadata[i] else {},
                    "vector": all_vectors[i].tolist()[:5],  # Only show first 5 dimensions
                    "source_table": table_name
                }

                # Add row data from source table
                if row_data:
                    vector_item["row_data"] = row_data

                vectors_list.append(vector_item)

            return {
                "success": True,
                "vectors": vectors_list,
                "total": total,
                "limit": limit,
                "offset": offset,
                "collection_name": collection_name,
                "source_table": table_name
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting RDBMS vectors: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get("/rdbms/sequences", tags=["RDBMS"])
    async def list_sequences():
        """List all sequences in the RDBMS"""
        try:
            sequences_info = rdbms_engine.sequences.get_all_sequences_info()

            return {
                "success": True,
                "sequences": sequences_info,
                "count": len(sequences_info)
            }
        except Exception as e:
            logger.error(f"Error listing sequences: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get("/rdbms/sequences/{sequence_name}", tags=["RDBMS"])
    async def get_sequence_info(sequence_name: str):
        """Get detailed information about a specific sequence"""
        try:
            sequence = rdbms_engine.sequences.get_sequence(sequence_name)

            if not sequence:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Sequence '{sequence_name}' not found"
                )

            return {
                "success": True,
                "sequence": sequence.to_dict()
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting sequence info: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post("/rdbms/vectorize-table/{table_name}", tags=["RDBMS"]
)
    async def vectorize_table(table_name: str):
        """
        Trigger vectorization for an existing table.

        This will create a vector collection and embed all existing rows.
        Useful for tables that existed before auto-vectorization was enabled.
        """
        try:
            if not rdbms_engine.auto_vectorizer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Auto-vectorization is not enabled"
                )

            # Get the table
            table = rdbms_engine.get_table(table_name)
            if not table:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Table '{table_name}' not found"
                )

            # Create vector collection
            collection_name = rdbms_engine.auto_vectorizer.create_vector_collection(
                table_name=table_name,
                columns=table.schema.columns
            )

            if not collection_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Table '{table_name}' does not qualify for vectorization (no TEXT columns)"
                )

            # Get all existing rows
            row_ids = []
            row_data_list = []

            for row_id in range(table.size()):
                row_data = table.get(row_id)
                if row_data:
                    row_ids.append(row_id)
                    row_data_list.append(row_data)

            # Trigger batch vectorization
            if row_ids:
                rdbms_engine.auto_vectorizer.on_insert_batch(
                    table_name=table_name,
                    row_ids=row_ids,
                    row_data_list=row_data_list
                )

            # Get vector count
            vectorizer = rdbms_engine.auto_vectorizer
            vector_count = 0
            if collection_name in vectorizer.vector_collections:
                vector_db = vectorizer.vector_collections[collection_name]
                vector_count = vector_db.size()

            # Auto-save to persist the vectors
            rdbms_engine._auto_save()

            logger.info(f"Vectorized table '{table_name}': {vector_count} vectors created")

            return {
                "success": True,
                "table_name": table_name,
                "collection_name": collection_name,
                "rows_processed": len(row_ids),
                "vectors_created": vector_count,
                "message": f"Successfully vectorized {vector_count} rows from '{table_name}'"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error vectorizing table: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    return app


# For running with uvicorn directly
app = create_app()
