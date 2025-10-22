"""Controller module for crud operations."""

from typing import Any, Dict, List, Optional, Type

from fastapi import HTTPException
from odmantic import AIOEngine, EmbeddedModel, Model
from pydantic import BaseModel

from fastapi_sdk.utils.schema import datetime_now_sec


class OwnershipRule:
    """Rule for filtering records based on user claims."""

    def __init__(
        self,
        *,
        claim_field: str,
        model_field: str,
        allow_public: bool = False,
    ):
        """Initialize the ownership rule.

        Args:
            claim_field: The field in the user claims to use (e.g., "account_id")
            model_field: The field in the model to match against (e.g., "account_id")
            allow_public: Whether to allow access to records without ownership
        """
        self.claim_field = claim_field
        self.model_field = model_field
        self.allow_public = allow_public


class ModelController:
    """Base controller class."""

    model: Type[Model]
    schema_create: Type[BaseModel]
    schema_update: Type[BaseModel]
    n_per_page: int = 25
    relationships: dict = {}  # Define relationships between models
    cascade_delete: bool = False  # Whether to cascade delete related items
    ownership_rule: Optional[OwnershipRule] = None  # Rule for filtering records
    _controller_registry: dict = {}  # Registry for controller classes
    extra_pipeline: Optional[List[dict]] = (
        None  # Custom MongoDB aggregation pipeline stages
    )

    def __init__(self, db_engine: AIOEngine):
        """Initialize the controller."""
        self.db_engine = db_engine

    @classmethod
    def register_controller(
        cls, name: str, controller_class: Type["ModelController"]
    ) -> None:
        """Register a controller class."""
        cls._controller_registry[name] = controller_class

    @classmethod
    def get_controller(cls, name: str) -> Type["ModelController"]:
        """Get a controller class by name."""
        return cls._controller_registry[name]

    def _get_ownership_filter(self, claims: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get the ownership filter based on user claims.

        Args:
            claims: The user claims from the JWT token

        Returns:
            A filter dictionary or None if no ownership rule is set
        """
        if not self.ownership_rule:
            return None

        # Superuser has full access
        if "superuser" in claims.get("roles", []):
            return None

        claim_value = claims.get(self.ownership_rule.claim_field)
        if not claim_value and not self.ownership_rule.allow_public:
            raise HTTPException(
                status_code=403,
                detail=f"Missing required claim: {self.ownership_rule.claim_field}",
            )

        if not claim_value:
            return None

        # Handle both single values and arrays
        if isinstance(claim_value, list):
            # If it's an array, use $in operator for MongoDB
            return {self.ownership_rule.model_field: {"$in": claim_value}}
        else:
            # If it's a single value, use direct equality
            return {self.ownership_rule.model_field: claim_value}

    def _merge_ownership_with_query(
        self, ownership_filter: Dict[str, Any], user_query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge ownership filter with user query, handling conflicts intelligently.

        Args:
            ownership_filter: The ownership filter from claims
            user_query: The user-provided query filters

        Returns:
            Merged query dictionary
        """
        if not ownership_filter:
            return user_query

        merged_query = user_query.copy()
        ownership_field = self.ownership_rule.model_field
        ownership_value = ownership_filter[ownership_field]

        # If user query doesn't have the ownership field, just add it
        if ownership_field not in user_query:
            merged_query[ownership_field] = ownership_value
            return merged_query

        # Handle conflict: user query has the same field as ownership
        user_value = user_query[ownership_field]

        # If ownership is a single value
        if not isinstance(ownership_value, dict) or "$in" not in ownership_value:
            # If user query is also a single value, they must match
            if user_value == ownership_value:
                merged_query[ownership_field] = ownership_value
            else:
                # User is trying to access something they don't own
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied: {ownership_field} not in your allowed values",
                )
        else:
            # Ownership is an array ($in operator)
            ownership_list = ownership_value["$in"]

            # If user query is a single value, check if it's in the ownership list
            if not isinstance(user_value, dict) or "$in" not in user_value:
                if user_value in ownership_list:
                    merged_query[ownership_field] = user_value
                else:
                    # User is trying to access something they don't own
                    raise HTTPException(
                        status_code=403,
                        detail=f"Access denied: {ownership_field} not in your allowed values",
                    )
            else:
                # Both ownership and user query are arrays, find intersection
                user_list = user_value["$in"]
                intersection = [val for val in user_list if val in ownership_list]

                if not intersection:
                    # No intersection, user has no access
                    raise HTTPException(
                        status_code=403,
                        detail=f"Access denied: {ownership_field} not in your allowed values",
                    )
                elif len(intersection) == 1:
                    # Single value intersection, use direct equality
                    merged_query[ownership_field] = intersection[0]
                else:
                    # Multiple values intersection, use $in
                    merged_query[ownership_field] = {"$in": intersection}

        return merged_query

    def _convert_embedded_model_lists(self, data_dict: dict) -> dict:
        """Convert lists of embedded models in the data dictionary.

        Args:
            data_dict: The dictionary containing model data

        Returns:
            The dictionary with converted embedded model lists
        """
        for field, value in data_dict.items():
            if isinstance(value, list) and hasattr(self.model, field):
                # Get the field type from the model's __annotations__
                field_type = self.model.__annotations__.get(field)
                if (
                    field_type
                    and hasattr(field_type, "__origin__")
                    and field_type.__origin__ is list
                ):
                    # Get the embedded model type
                    embedded_model_type = field_type.__args__[0]
                    if hasattr(embedded_model_type, "__base__") and issubclass(
                        embedded_model_type.__base__, EmbeddedModel
                    ):
                        # Convert each item in the list to the embedded model type
                        data_dict[field] = [
                            embedded_model_type(**item) for item in value
                        ]
        return data_dict

    def _verify_ownership(
        self, data_dict: dict, claims: Optional[Dict[str, Any]] = None
    ) -> None:
        """Verify ownership of the data dictionary."""
        if self.ownership_rule:
            if (
                not self.ownership_rule.allow_public
                and not claims
                and self.ownership_rule.model_field != "uuid"
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Claims must be provided when ownership rule is set and allow_public is False",
                )
            if claims:
                ownership_filter = self._get_ownership_filter(claims)
                if ownership_filter and self.ownership_rule.model_field != "uuid":
                    # Check if the provided data matches the user's claim
                    model_field_value = data_dict.get(self.ownership_rule.model_field)
                    claim_value = claims.get(self.ownership_rule.claim_field)

                    # Handle both single values and arrays
                    if isinstance(claim_value, list):
                        # If claim is an array, check if model field value is in the array
                        if model_field_value not in claim_value:
                            raise HTTPException(
                                status_code=403,
                                detail=f"Invalid {self.ownership_rule.model_field}",
                            )
                    else:
                        # If claim is a single value, check direct equality
                        if model_field_value != claim_value:
                            raise HTTPException(
                                status_code=403,
                                detail=f"Invalid {self.ownership_rule.model_field}",
                            )

    async def create(
        self, data: dict, claims: Optional[Dict[str, Any]] = None
    ) -> BaseModel:
        """Create a new model."""
        data = self.schema_create(**data)
        data_dict = data.model_dump()

        # Verify ownership if rule exists
        self._verify_ownership(data_dict, claims)

        # Convert lists of embedded models
        data_dict = self._convert_embedded_model_lists(data_dict)

        # Call before_create hook if implemented
        if hasattr(self, "before_create"):
            data_dict = await self.before_create(data_dict, claims)

        model = self.model(**data_dict)
        model = await self.db_engine.save(model)

        # Call after_create hook if implemented
        if hasattr(self, "after_create"):
            model = await self.after_create(model, claims)

        return model

    async def update(
        self, uuid: str, data: dict, claims: Optional[Dict[str, Any]] = None
    ) -> Optional[BaseModel]:
        """Update a model."""
        model = await self.get(uuid, claims)
        if not model:
            return None

        data = self.schema_update(**data)
        data_dict = data.model_dump(exclude_unset=True)

        # Convert lists of embedded models
        data_dict = self._convert_embedded_model_lists(data_dict)

        # Call before_update hook if implemented
        if hasattr(self, "before_update"):
            data_dict = await self.before_update(data_dict, claims)

        # Update the fields submitted
        for field, value in data_dict.items():
            setattr(model, field, value)
        model.updated_at = datetime_now_sec()
        model = await self.db_engine.save(model)

        # Call after_update hook if implemented
        if hasattr(self, "after_update"):
            model = await self.after_update(model, claims)

        return model

    async def after_create(
        self, obj: BaseModel, claims: Optional[Dict[str, Any]] = None
    ) -> BaseModel:
        """Hook called after creating a model.

        Override this method in your controller to add custom behavior after creation.
        The method should return the modified object.

        Args:
            obj: The created model instance
            claims: Optional claims from the JWT token

        Returns:
            The modified model instance
        """
        return obj

    async def after_update(
        self, obj: BaseModel, claims: Optional[Dict[str, Any]] = None
    ) -> BaseModel:
        """Hook called after updating a model.

        Override this method in your controller to add custom behavior after update.
        The method should return the modified object.

        Args:
            obj: The updated model instance
            claims: Optional claims from the JWT token

        Returns:
            The modified model instance
        """
        return obj

    async def before_create(
        self, data_dict: dict, claims: Optional[Dict[str, Any]] = None
    ) -> dict:
        """Hook called before creating a model.

        Override this method in your controller to modify the data dictionary before creation.
        The method should return the modified data dictionary.

        Args:
            data_dict: The data dictionary to be used for model creation
            claims: Optional claims from the JWT token

        Returns:
            The modified data dictionary
        """
        return data_dict

    async def before_update(
        self, data_dict: dict, claims: Optional[Dict[str, Any]] = None
    ) -> dict:
        """Hook called before updating a model.

        Override this method in your controller to modify the data dictionary before update.
        The method should return the modified data dictionary.

        Args:
            data_dict: The data dictionary to be used for model update
            claims: Optional claims from the JWT token

        Returns:
            The modified data dictionary
        """
        return data_dict

    async def get(
        self,
        uuid: str,
        claims: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False,
        include: Optional[List[str]] = None,
    ) -> Optional[BaseModel]:
        """Get a model.

        Args:
            uuid: The UUID of the model to get
            claims: Optional claims for ownership verification
            include_deleted: Whether to include deleted items in the query
            include: Optional list of related objects to include
        """
        query = self.model.uuid == uuid
        if not include_deleted:
            query = query & (self.model.deleted == False)

        # Apply ownership filter if rule exists
        if self.ownership_rule:
            if not self.ownership_rule.allow_public and not claims:
                raise HTTPException(
                    status_code=403,
                    detail="Claims must be provided when ownership rule is set and allow_public is False",
                )
            if claims:
                ownership_filter = self._get_ownership_filter(claims)
                if ownership_filter:
                    # Handle both single values and arrays in ownership filter
                    filter_value = ownership_filter[self.ownership_rule.model_field]
                    if isinstance(filter_value, dict) and "$in" in filter_value:
                        # Array case: use $in operator
                        query = query & (
                            getattr(self.model, self.ownership_rule.model_field).in_(
                                filter_value["$in"]
                            )
                        )
                    else:
                        # Single value case: use direct equality
                        query = query & (
                            getattr(self.model, self.ownership_rule.model_field)
                            == filter_value
                        )

        model = await self.db_engine.find_one(self.model, query)

        # If model is found and include is specified, load relationships
        if model and include:
            for relation in include:
                if relation not in self.relationships:
                    continue

                rel_info = self.relationships[relation]
                rel_controller_name = rel_info["controller"]
                rel_type = rel_info["type"]
                foreign_key = rel_info.get("foreign_key")

                # Get the controller class from the registry
                rel_controller_class = self.get_controller(rel_controller_name)

                if rel_type == "one_to_many":
                    # Fetch related items where foreign_key matches this model's uuid
                    related_items = await rel_controller_class(
                        self.db_engine
                    ).list_related(
                        foreign_key=foreign_key, value=model.uuid, claims=claims
                    )
                    setattr(model, relation, related_items)
                elif rel_type == "many_to_one":
                    # Fetch single related item
                    related_item = await rel_controller_class(self.db_engine).get(
                        uuid=getattr(model, foreign_key), claims=claims
                    )
                    setattr(model, relation, related_item)

        return model

    async def delete(
        self, uuid: str, claims: Optional[Dict[str, Any]] = None
    ) -> Optional[BaseModel]:
        """Delete a model."""
        model = await self.get(uuid, claims)
        if model:
            model.deleted = True
            return await self.db_engine.save(model)
        return None

    async def undelete(
        self, uuid: str, claims: Optional[Dict[str, Any]] = None
    ) -> Optional[BaseModel]:
        """Undelete a model by setting deleted to False.

        Args:
            uuid: The UUID of the model to undelete
            claims: Optional claims for ownership verification

        Returns:
            The undeleted model or None if not found
        """
        model = await self.get(uuid, claims, include_deleted=True)
        if model:
            model.deleted = False
            return await self.db_engine.save(model)
        return None

    async def list(
        self,
        page: int = 1,
        query: Optional[List[dict]] = None,
        order_by: Optional[dict] = None,
        claims: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
        n_per_page: Optional[int] = None,
        deleted: bool = False,
    ) -> List[BaseModel]:
        """List models.

        Args:
            page: The page number (1-based, minimum 1)
            query: Optional query filters
            order_by: Optional sorting criteria
            claims: Optional claims for ownership verification
            include: Optional list of related objects to include
            n_per_page: Optional number of items per page (max 250)
            deleted: If True, only return deleted items. If False, only return non-deleted items.
        """
        # Validate page number
        if page < 1:
            raise ValueError("Page number must be 1 or greater")

        # Get the collection
        collection_name = (
            self.model.model_config.get("collection") or self.model.__collection__
        )
        _collection = self.db_engine.database[collection_name]

        # Create a pipeline for aggregation
        _pipeline = []

        # Filter by deleted status
        _query = {"deleted": deleted}
        if query:
            for q in query:
                _query.update(q)

        # Apply ownership filter if rule exists
        if self.ownership_rule:
            if not self.ownership_rule.allow_public and not claims:
                raise HTTPException(
                    status_code=403,
                    detail="Claims must be provided when ownership rule is set and allow_public is False",
                )
            if claims:
                ownership_filter = self._get_ownership_filter(claims)
                if ownership_filter:
                    _query = self._merge_ownership_with_query(ownership_filter, _query)

        # Append pipeline stages for related objects
        if include:
            for relation in include:
                if relation not in self.relationships:
                    continue

                rel_info = self.relationships[relation]
                rel_controller_name = rel_info["controller"]
                rel_type = rel_info["type"]
                foreign_key = rel_info.get("foreign_key")

                # Get the controller class from the registry
                rel_controller_class = self.get_controller(rel_controller_name)

                if rel_type == "one_to_many":
                    _pipeline.append(
                        {
                            "$lookup": {
                                "from": rel_controller_class.model.model_config.get(
                                    "collection"
                                )
                                or rel_controller_class.model.__collection__,
                                "localField": "uuid",
                                "foreignField": foreign_key,
                                "as": relation,
                            }
                        }
                    )
                elif rel_type == "many_to_one":
                    _pipeline.append(
                        {
                            "$lookup": {
                                "from": rel_controller_class.model.model_config.get(
                                    "collection"
                                )
                                or rel_controller_class.model.__collection__,
                                "localField": foreign_key,
                                "foreignField": "uuid",
                                "as": relation,
                            }
                        }
                    )
                    _pipeline.append({"$unwind": f"${relation}"})

        # Add custom pipeline stages if defined in the controller (first)
        if self.extra_pipeline:
            _pipeline.extend(self.extra_pipeline)

        # Sorting, default by created_at and _id for stable ordering
        _sort = order_by if order_by else {"created_at": -1, "_id": -1}

        # Add the pipeline stages
        _pipeline.append({"$match": _query})
        _pipeline.append({"$sort": _sort})

        # Determine items per page
        items_per_page = min(n_per_page or self.n_per_page, 250)

        # Add pagination data (1-based pagination)
        _pipeline.append({"$skip": (page - 1) * items_per_page})
        _pipeline.append({"$limit": items_per_page})

        # Execute the aggregation
        items = await _collection.aggregate(_pipeline).to_list(length=items_per_page)

        # Count the total number of items
        # If we have extra_pipeline or include relationships, we need to use aggregation for accurate count
        if self.extra_pipeline or include:
            # Create a count pipeline that applies the same transformations but without pagination
            count_pipeline = []

            # Add custom pipeline stages if defined in the controller (first)
            if self.extra_pipeline:
                count_pipeline.extend(self.extra_pipeline)

            # Add the match stage
            count_pipeline.append({"$match": _query})

            # Add count stage
            count_pipeline.append({"$count": "total"})

            # Execute the count aggregation
            count_result = await _collection.aggregate(count_pipeline).to_list(1)
            total = count_result[0]["total"] if count_result else 0
        else:
            # Use simple count for basic queries
            total = await _collection.count_documents(_query)

        pages = total // items_per_page
        if total % items_per_page > 0:
            pages += 1

        # Convert items to models
        models = [self.model.model_validate_doc(item) for item in items]

        return {
            "items": models,
            "total": total,
            "page": page,
            "pages": pages,
            "size": len(models),
        }

    async def list_related(
        self, foreign_key: str, value: str, claims: Optional[Dict[str, Any]] = None
    ) -> List[BaseModel]:
        """List related models by foreign key."""
        result = await self.list(query=[{foreign_key: value}], claims=claims)
        return result["items"]

    async def count(
        self,
        query: Optional[List[dict]] = None,
        claims: Optional[Dict[str, Any]] = None,
        deleted: bool = False,
    ) -> int:
        """Count models matching the query.

        Args:
            query: Optional query filters
            claims: Optional claims for ownership verification
            deleted: If True, only count deleted items. If False, only count non-deleted items.

        Returns:
            The total count of matching items
        """
        # Get the collection
        collection_name = (
            self.model.model_config.get("collection") or self.model.__collection__
        )
        _collection = self.db_engine.database[collection_name]

        # Build the query
        _query = {"deleted": deleted}
        if query:
            for q in query:
                _query.update(q)

        # Apply ownership filter if rule exists
        if self.ownership_rule:
            if not self.ownership_rule.allow_public and not claims:
                raise HTTPException(
                    status_code=403,
                    detail="Claims must be provided when ownership rule is set and allow_public is False",
                )
            if claims:
                ownership_filter = self._get_ownership_filter(claims)
                if ownership_filter:
                    _query = self._merge_ownership_with_query(ownership_filter, _query)

        # Count the documents
        return await _collection.count_documents(_query)

    async def get_with_relations(
        self,
        uuid: str,
        include: Optional[List[str]] = None,
        claims: Optional[Dict[str, Any]] = None,
    ) -> BaseModel:
        """Get a model with its relationships."""
        # Add deprecation warning
        print(
            "get_with_relations is deprecated. Use get with include parameter instead."
        )
        model = await self.get(uuid, claims, include=include)
        if not model or not include:
            return model

        for relation in include:
            if relation not in self.relationships:
                continue

            rel_info = self.relationships[relation]
            rel_controller_name = rel_info["controller"]
            rel_type = rel_info["type"]
            foreign_key = rel_info.get("foreign_key")

            # Get the controller class from the registry
            rel_controller_class = self.get_controller(rel_controller_name)

            if rel_type == "one_to_many":
                # Fetch related items where foreign_key matches this model's uuid
                related_items = await rel_controller_class(self.db_engine).list_related(
                    foreign_key=foreign_key, value=model.uuid, claims=claims
                )
                setattr(model, relation, related_items)
            elif rel_type == "many_to_one":
                # Fetch single related item
                related_item = await rel_controller_class(self.db_engine).get(
                    uuid=getattr(model, foreign_key), claims=claims
                )
                setattr(model, relation, related_item)

        return model

    async def delete_with_relations(
        self, uuid: str, claims: Optional[Dict[str, Any]] = None
    ) -> BaseModel:
        """Delete a model and its related items if cascade_delete is True."""
        model = await self.get(uuid, claims)
        if not model:
            return None

        if self.cascade_delete:
            for rel_info in self.relationships.values():
                if rel_info["type"] == "one_to_many":
                    rel_controller_name = rel_info["controller"]
                    foreign_key = rel_info.get("foreign_key")

                    # Get the controller class from the registry
                    rel_controller_class = self.get_controller(rel_controller_name)

                    # Find all related items
                    related_items = await rel_controller_class(
                        self.db_engine
                    ).list_related(foreign_key=foreign_key, value=uuid, claims=claims)
                    # Delete each related item
                    for item in related_items:
                        await rel_controller_class(
                            self.db_engine
                        ).delete_with_relations(item.uuid, claims=claims)

        return await self.delete(uuid, claims)
