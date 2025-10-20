"""This module provides utility functions and classes for interacting with a MongoDB database.
It includes functionality for connecting to the database, performing CRUD (Create, Read, Update, Delete)
operations on documents, and managing attachments within documents. The module is designed to work
with MongoDB collections and provides a high-level interface for common database operations.
Classes:
--------
- GWDatabaseException: Custom exception class for handling database-related errors.
Functions:
- get_mongodb: Establishes a connection to the MongoDB database and retrieves the specified database.
- get_documents: Retrieves all documents from a specified collection.
- get_document: Retrieves a single document by its ID from a specified collection.
- post_document: Adds a new document to a specified collection.
- put_document: Inserts or updates a document in a specified collection.
- delete_document: Deletes a document by its ID from a specified collection.
- find_document: Finds a single document in a collection based on a query selector.
- find_documents: Retrieves multiple documents from a collection based on a query selector.
- put_attachment: Adds or updates an attachment in a specified document within a collection.
- get_attachment: Retrieves an attachment from a specified document in the database.
Note:
-----
This module assumes that the MongoDB server is running and accessible at the specified URI.
The database name can be overridden using the `override_database_name` parameter in most functions.
"""



from bson import ObjectId
from gw_settings_management.setting_management import (
    database_name, database_url,
)
from pymongo import MongoClient


class GWDatabaseException(Exception):
    """Guidewire database Exception

    Parameters
    ----------
    Exception : _type_
        _description_
    """

    pass


def get_mongodb(*, uri: str=None, override_database_name=None):
    """Get the database, if the database has not yes been created it will be created

    Parameters
    ----------
    override_database_name : _type_, optional
        _description_, by default None

    Returns
    -------
    _type_
        _description_
    """
    if uri is None:
        uri = f"mongodb://{database_url(short=True)}/"
    client = MongoClient(uri)
    if override_database_name:
        db_name = override_database_name
    else:
        db_name = database_name()
    return client[db_name]


def get_documents(collection, *, override_database_name=None):
    """Extract the documents from the collection
    Parameters
    ----------
    collection : _type_
        _description_
    override_database_name : _type_, optional
        _description_, by default None

    Returns
    -------
    _type_
        _description_
    """
    documents = find_documents(
        collection, {}, override_database_name=override_database_name
    )
    return documents


def get_document(
    collection,
    doc_id: str,
    *,
    create_if_missing=False,
    override_database_name=None,
    db_connection=None,
):
    """Extract the document from the collection for the given id

    Parameters
    ----------
    collection : _type_
        _description_
    doc_id : str
        _description_
    create_if_missing : bool, optional
        _description_, by default False
    override_database_name : _type_, optional
        _description_, by default None
    db_connection : _type_, optional
        _description_, by default None

    Returns
    -------
    _type_
        _description_

    Raises
    ------
    GWDatabaseException
        _description_
    """
    if db_connection is None:
        db = get_mongodb(override_database_name=override_database_name)
    else:
        db = db_connection
    mongo_collection = db.get_collection(collection)
    mongo_document = mongo_collection.find_one(ObjectId(doc_id))
    if mongo_document is None:
        raise GWDatabaseException(f"Document not found ({doc_id})")
    return mongo_document


def post_document(collection, doc: dict, *, override_database_name=None):
    """Add a new document to the collection

    Parameters
    ----------
    collection : _type_
        _description_
    doc : dict
        _description_
    override_database_name : _type_, optional
        _description_, by default None

    Returns
    -------
    _type_
        _description_
    """
    db = get_mongodb(override_database_name=override_database_name)
    mongo_collection = db.get_collection(collection)
    mongo_collection.insert_one(doc)
    return doc


def put_document(
    collection_name, doc_id: str, doc: dict, *, override_database_name=None
):
    """Inserts or updates a document in a MongoDB collection.

    This function replaces an existing document with the specified `doc_id`
    in the given collection or inserts a new document if it does not exist.
    Optionally, a different database name can be specified

    Parameters
    ----------
    collection_name : _type_
        The name of the MongoDB collection where the document will be stored.
    doc_id : str
        The unique identifier (_id) for the document.
    doc : dict
        The document data to be inserted or updated in the collection.
    override_database_name : _type_, optional
        The name of an alternative database to use instead of the default,
        by default None.

    Returns
    -------
    The updated document
    """
    db = get_mongodb(override_database_name=override_database_name)
    mongo_collection = db.get_collection(collection_name)
    mongo_collection.replace_one({"_id": ObjectId(doc_id)}, doc)
    mongo_document = get_document(collection_name, doc_id, db_connection=db)
    return mongo_document


def patch_document(
    collection_name, query, setter, *, override_database_name=None
):
    """updates a document in a MongoDB collection.

    This function replaces an existing document with the specified `doc_id`
    in the given collection or inserts a new document if it does not exist.
    Optionally, a different database name can be specified

    Parameters
    ----------
    collection_name : _type_
        The name of the MongoDB collection where the document will be stored.
    doc_id : str
        The unique identifier (_id) for the document.
    doc : dict
        The document data to be inserted or updated in the collection.
    override_database_name : _type_, optional
        The name of an alternative database to use instead of the default,
        by default None.

    Returns
    -------
    The updated document
    """
    db = get_mongodb(override_database_name=override_database_name)
    mongo_collection = db.get_collection(collection_name)
    mongo_collection.update_one(query, setter)



def delete_document(collection_name, doc_id: str, *, override_database_name=None):
    """
    Delete a document from a MongoDB collection by its ID.
    Args:
        collection_name (str): The name of the MongoDB collection from which the document will be deleted.
        doc_id (str): The ID of the document to delete. Must be a valid MongoDB ObjectId string.
        override_database_name (str, optional): The name of the database to override the default database.
            If not provided, the default database will be used.
    Returns:
        pymongo.results.DeleteResult: The result of the delete operation, which includes information
        about the deletion status.
    Raises:
        bson.errors.InvalidId: If the provided `doc_id` is not a valid ObjectId.
        pymongo.errors.PyMongoError: If an error occurs during the deletion process.
    Example:
        >>> delete_document("users", "64f7c8e5b4d1e2a3c4f5g6h7")
    """

    db = get_mongodb(override_database_name=override_database_name)
    mongo_collection = db.get_collection(collection_name)
    status = mongo_collection.delete_one({"_id": ObjectId(doc_id)})
    return status


def find_document(collection_name, selector, *, override_database_name=None):
    """
    Finds a single document in a MongoDB collection based on the provided selector.
    Parameters:
        collection_name (str): The name of the MongoDB collection to query.
        selector (dict): A dictionary containing the query selector.
                         Must include a "selector" key with the query criteria.
                         Optionally, may include a "fields" key to specify fields to retrieve.
        override_database_name (str, optional): The name of the database to use instead of the default.
    Returns:
        dict or None: The document found in the collection, with the "_id" field converted to a string.
                      Returns None if no document matches the query.
    """

    db = get_mongodb(override_database_name=override_database_name)
    mongo_collection = db.get_collection(collection_name)
    selector_dict = selector["selector"]
    if "fields" in selector_dict:
        fields_dict = selector["fields"]
    else:
        fields_dict = {}
    result = mongo_collection.find_one(selector_dict)
    if result is not None:
        result["_id"] = str(result["_id"])
    return result


def find_documents(collection_name, selector, *, override_database_name=None):
    """
    Retrieves documents from a MongoDB collection based on the provided selector.
    Parameters:
    collection_name (str): The name of the MongoDB collection to query.
    selector (dict): A dictionary containing the query selector and optional fields to project.
                     Example format: {"selector": <query>, "fields": <projection_fields>}.
    override_database_name (str, optional): The name of the database to override the default database. Defaults to None.
    Returns:
    list: A list of documents matching the query, with the "_id" field converted to a string.
    """

    return_docs = list()
    db = get_mongodb(override_database_name=override_database_name)
    mongo_collection = db.get_collection(collection_name)
    selector_dict = selector["selector"]
    if "fields" in selector_dict:
        fields_dict = selector["fields"]
    else:
        fields_dict = {}
    result = mongo_collection.find(selector_dict)
    for doc in result:
        doc["_id"] = str(doc["_id"])
        return_docs.append(doc)
    return return_docs


def put_attachment(
    collection_name,
    *,
    doc_id: str,
    attachment_name: str,
    attachment,
    override_database_name=None,
):
    """
    Adds or updates an attachment in a specified document within a MongoDB collection.
    Parameters:
        collection_name (str): The name of the MongoDB collection.
        doc_id (str): The ID of the document to which the attachment will be added or updated.
        attachment_name (str): The key under which the attachment will be stored in the document.
        attachment: The attachment data to be added or updated in the document.
        override_database_name (str, optional): An optional database name to override the default database connection.
    """
    db = get_mongodb(override_database_name=override_database_name)
    document = get_document(collection_name, doc_id, db_connection=db)
    document[attachment_name] = attachment


def get_attachment(
    *, doc_id: str, attachment_name: str, rev: str = None, override_database_name=None
):
    """
    Retrieve an attachment from a document in the MongoDB database.
    Parameters:
        doc_id (str): The ID of the document containing the attachment.
        attachment_name (str): The name of the attachment to retrieve.
        rev (str, optional): The revision ID of the document. Defaults to None.
        override_database_name (str, optional): The name of an alternative database to use. Defaults to None.
    Returns:
        The requested attachment from the document.
    """
    db = get_mongodb(override_database_name=override_database_name)
    attachment = db.get_attachment(database_name, doc_id, attachment_name)
    return attachment
