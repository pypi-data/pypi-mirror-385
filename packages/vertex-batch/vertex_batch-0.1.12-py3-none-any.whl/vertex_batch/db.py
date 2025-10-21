from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO
)


class Db:
    def __init__(self, url: str, db_name: str, batch_collection_name: str, file_collection_name: str = "file_infos"):
        self.url = url
        self.db_name = db_name
        self.batch_collection_name = batch_collection_name
        self.file_collection_name = file_collection_name

    def clone_db(self, batch_collection_name: str) -> "Db":
        return Db(
            url=self.url,
            db_name=self.db_name,
            batch_collection_name=batch_collection_name,
            file_collection_name=self.file_collection_name,
        )

    def _connect(self):
        try:
            client = MongoClient(self.url)
            return client
        except Exception as e:
            logging.exception(f"Error connecting to database: {e}")
            return None

    def _close(self, client: MongoClient):
        if client:
            client.close()
        
    def flag_payloads(self, file_path: Path, flag: str, clean: bool = False):
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.batch_collection_name]

                if clean:
                    filter_query = {"file_name": file_path.name, "status": "WRITTEN"}
                else:
                    filter_query = {"file_name": file_path.name}

                result = collection.update_many(
                    filter_query,
                    {"$set": {"status": flag, "updated_at": datetime.now()}}
                )
                if result.matched_count:
                    logging.info(f"All payloads for file {file_path.name} flagged as {flag}.")
                else:
                    logging.info(f"No payloads found for file {file_path.name}.")
            except Exception as e:
                logging.exception(f"Error flagging payloads: {e}")
            finally:
                self._close(client)
        else:
            logging.info("Failed to connect to the database.")
        
    def save_file(self, **kwargs):
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.file_collection_name]
                file_data = dict(kwargs)
                file_data["created_at"] = datetime.now()
                collection.insert_one(file_data)
                logging.info("File data saved to database.")
            except Exception as e:
                logging.exception(f"Error saving file data to database: {e}")
            finally:
                self._close(client)
        else:
            logging.info("Failed to connect to the database.")
        
    def save_payload(self, **kwargs)->bool:
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.batch_collection_name]
                payload = dict(kwargs)
                payload["status"] = "PENDING"
                exist = collection.find_one(filter={"custom_id": payload.get("custom_id")})
                
                if exist:
                    payload["updated_at"] = datetime.now()
                    collection.update_one(
                        filter={"custom_id": payload.get("custom_id")},
                        update={"$set": payload}
                    )
                else:
                    payload["created_at"] = datetime.now()
                    collection.insert_one(payload)

                logging.info("Payload saved to database.")
                return True
            except Exception as e:
                logging.exception(f"Error saving payload to database: {e}")
                return False
            finally:
                self._close(client)
        else:
            logging.info("Failed to connect to the database.")
            return False

    def get_file(self, file_path: Path):
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.file_collection_name]
                file_info = collection.find_one({"file_name": file_path.name})
                return file_info
            except Exception as e:
                logging.exception(f"Error retrieving file info: {e}")
                return None
            finally:
                self._close(client)
        else:
            logging.info("Failed to connect to the database.")
            return None

    def update_file(self, file_path: Path, **kwargs):
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.file_collection_name]
                update_fields = {k: v for k, v in kwargs.items()}
                update_fields["updated_at"] = datetime.now()
                result = collection.update_one(
                    {"file_path": file_path.name},
                    {"$set": update_fields}
                )
                if result.matched_count:
                    logging.info(f"File {file_path.name} updated with fields {list(kwargs.keys())}.")
                else:
                    logging.info(f"No file info found with file_name {file_path.name}.")
            except Exception as e:
                logging.exception(f"Error updating file info: {e}")
            finally:
                self._close(client)
        else:
            logging.info("Failed to connect to the database.")
        
    def get_payload(self, custom_id: str):
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.batch_collection_name]
                payload = collection.find_one({"custom_id": custom_id})
                return payload
            except Exception as e:
                logging.exception(f"Error retrieving payload by custom_id: {e}")
                return None
            finally:
                self._close(client)
        else:
            logging.info("Failed to connect to the database.")
            return None
        
    def get_payloads(self, status: str, file_name: str = None, created_before:datetime = None) -> list:
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.batch_collection_name]
                query = {"status": status}

                if file_name:
                    query["file_name"] = file_name

                if created_before:
                    query["created_at"] = {"$lt": created_before}

                payloads = list(collection.find(query))
                return payloads
            except Exception as e:
                logging.exception(f"Error retrieving payloads from database: {e}")
                return []
            finally:
                self._close(client)
        else:
            logging.info("Failed to connect to the database.")
            return []
        
    def update_payload(self, custom_id: str, **kwargs):
        client = self._connect()
        if client:
            try:
                db = client[self.db_name]
                collection = db[self.batch_collection_name]
                update_fields = {k: v for k, v in kwargs.items()}
                update_fields["updated_at"] = datetime.now()
                result = collection.update_one(
                    {"custom_id": custom_id},
                    {"$set": update_fields}
                )
                if result.matched_count:
                    logging.info(f"Payload {custom_id} updated with fields {list(kwargs.keys())}.")
                else:
                    logging.info(f"No payload found with custom_id {custom_id}.")
            except Exception as e:
                logging.exception(f"Error updating payload: {e}")
            finally:
                self._close(client)
        else:
            logging.info("Failed to connect to the database.")
