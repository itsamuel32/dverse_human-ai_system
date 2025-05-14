from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
import requests


class VectorDB:
    def __init__(self, persist_dir: str = "./scene_object_db"):

        #self.embedder = SentenceTransformer("all-mpnet-base-v2")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name="scene_objects")

    # def update_from_unreal(self, endpoint: str = "http://localhost:8080/scene/objects") -> int:
    #     try:
    #         response = requests.get(endpoint)
    #         response.raise_for_status()
    #         data = response.json()
    #
    #         documents, metadatas, ids = [], [], []
    #
    #         for item in data.get("Items", []):
    #             transform = item.get("Transform", {})
    #
    #             doc_text = (
    #                 f"ID: {item['ID']}\n"
    #                 f"Name: {item['Name']}\n"
    #                 f"Type: {item['Type']}\n"
    #                 f"Description: {item['Description']}\n"
    #                 f"Position: X={transform.get('LocationX')}, Y={transform.get('LocationY')}, Z={transform.get('LocationZ')}\n"
    #                 f"Rotation: Pitch={transform.get('RotationPitch')}, Yaw={transform.get('RotationYaw')}, Roll={transform.get('RotationRoll')}\n"
    #                 f"Scale: X={transform.get('ScaleX')}, Y={transform.get('ScaleY')}, Z={transform.get('ScaleZ')}"
    #             )
    #             documents.append(doc_text)
    #
    #             metadatas.append({
    #                 "ID": item["ID"],
    #                 "Name": item["Name"],
    #                 "Type": item["Type"],
    #                 "Description": item["Description"],
    #                 **transform  # Unpack flat fields directly into metadata
    #             })
    #
    #             ids.append(str(item["ID"]))
    #
    #         # Delete existing entries by ID (safe delete for new Chroma)
    #         existing = self.collection.get()
    #         existing_ids = existing.get("ids", [])
    #         if existing_ids:
    #             self.collection.delete(ids=existing_ids)
    #
    #         # Add fresh data
    #         self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
    #
    #         return len(documents)
    #
    #     except Exception as e:
    #         print(f"[VectorDB] Failed to update: {e}")
    #         return 0

    def update_from_unreal(self, endpoint: str = "http://localhost:8080/scene/objects") -> int:

        try:
            data = requests.get(endpoint).json()["Items"]

            documents, metadatas, ids = [], [], []
            for item in data:
                transform = item["Transform"]
                doc_text = (
                    f"ID: {item['ID']}\n"
                    f"Name: {item['Name']}\n"
                    f"Type: {item['Type']}\n"
                    f"Description: {item['Description']}\n"
                    f"Position: X={transform.get('LocationX')}, Y={transform.get('LocationY')}, Z={transform.get('LocationZ')}\n"
                    f"Rotation: Pitch={transform.get('RotationPitch')}, Yaw={transform.get('RotationYaw')}, Roll={transform.get('RotationRoll')}\n"
                    f"Scale: X={transform.get('ScaleX')}, Y={transform.get('ScaleY')}, Z={transform.get('ScaleZ')}"
                )
                documents.append(doc_text)

                metadatas.append({
                    "ID": item["ID"],
                    "Name": item["Name"],
                    "Type": item["Type"],
                    "Description": item["Description"],
                    **transform
                })
                ids.append(str(item["ID"]))

            self.collection.upsert(documents=documents,
                                   metadatas=metadatas,
                                   ids=ids)
            return len(documents)

        except requests.HTTPError as exc:
            print("[VectorDB] HTTP error:", exc)

        except Exception as exc:
            print("[VectorDB] Unexpected error:", exc)

    def search(self, query: str, top_k: int = 5):
        try:
            query_embedding = self.embedder.encode([query])[0].tolist()
            results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)

            print(f"[SEARCH QUERY]: {query} == {results}")
            return [
                {
                    "ID": metadata["ID"],
                    "Name": metadata["Name"],
                    "Type": metadata["Type"],
                    "Description": metadata["Description"],
                    "Transform": {
                        "LocationX": metadata.get("LocationX"),
                        "LocationY": metadata.get("LocationY"),
                        "LocationZ": metadata.get("LocationZ"),
                        "RotationPitch": metadata.get("RotationPitch"),
                        "RotationYaw": metadata.get("RotationYaw"),
                        "RotationRoll": metadata.get("RotationRoll"),
                        "ScaleX": metadata.get("ScaleX"),
                        "ScaleY": metadata.get("ScaleY"),
                        "ScaleZ": metadata.get("ScaleZ")
                    }
                }
                for metadata in results.get("metadatas", [[]])[0]
            ]
        except Exception as e:
            print(f"[SceneObjectVectorDB] Search failed: {e}")
            return []
