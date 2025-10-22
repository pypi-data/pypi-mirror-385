#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pathlib
import shutil
from operator import itemgetter

import pymongo
from bson.objectid import ObjectId
from girder import events
from girder.api import access
from girder.api.rest import setContentDisposition, setResponseHeader
from girder.constants import AccessType, TokenScope
from girder.exceptions import GirderException, ValidationException
from girder.models.folder import Folder
from girder.utility import ziputil

from . import VirtualObject, bail_if_exists, ensure_unique_path, validate_event


def file_stream(path, buf_size=65536):
    bytes_read = 0
    end_byte = path.stat().st_size
    with path.open(mode="rb") as f:
        while True:
            read_len = min(buf_size, end_byte - bytes_read)
            if read_len <= 0:
                break
            data = f.read(read_len)
            bytes_read += read_len
            # if not data:
            #    break
            yield data


class VirtualFolder(VirtualObject):
    def __init__(self):
        super(VirtualFolder, self).__init__()
        self.resourceName = "virtual_folder"
        name = "virtual_resources"
        events.bind("model.folder.validate", "jsonforms", self._validateFolder)
        events.bind("rest.get.folder.before", name, self.get_child_folders)
        events.bind("rest.post.folder.before", name, self.create_folder)
        events.bind("rest.get.folder/:id.before", name, self.get_folder_info)
        events.bind("rest.put.folder/:id.before", name, self.rename_folder)
        events.bind("rest.delete.folder/:id.before", name, self.remove_folder)
        events.bind("rest.post.folder.after", "jsonforms", self._folderUpdate)
        events.bind("rest.put.folder/:id.after", "jsonforms", self._folderUpdate)
        # GET /folder/:id/access -- not needed
        # PUT /folder/:id/access -- not needed
        # PUT /folder/:id/check -- not needed
        events.bind(
            "rest.delete.folder/:id/contents.before", name, self.remove_folder_contents
        )
        events.bind("rest.post.folder/:id/copy.before", name, self.copy_folder)
        events.bind("rest.get.folder/:id/details.before", name, self.get_folder_details)
        events.bind("rest.get.folder/:id/download.before", name, self.download_folder)
        # PUT/DELETE /folder/:id/metadata -- not needed
        events.bind("rest.get.folder/:id/rootpath.before", name, self.folder_root_path)
        events.bind(
            "rest.post.folder/recursive.before", name, self.create_folder_recursive
        )
        # For README plugin
        events.bind("rest.get.folder/:id/readme.before", name, self.get_folder_readme)

    def _folderUpdate(self, event):
        params = event.info["params"]
        if {"isSymlink", "symlinkTargetId"} & set(params):
            folder = Folder().load(event.info["returnVal"]["_id"], force=True)
            update = False

            if params.get("isSymlink") is not None:
                update = True
                folder["isSymlink"] = params["isSymlink"]
            if params.get("symlinkTargetId"):
                update = True
                try:
                    folder["symlinkTargetId"] = ObjectId(params["symlinkTargetId"])
                except Exception:
                    raise ValidationException(
                        "symlinkTargetId must be an ObjectId", field="symlinkTargetId"
                    )

            if update and not folder.get("isSymlink"):
                folder["symlinkTargetId"] = None

            if update:
                self.requireAdmin(
                    self.getCurrentUser(), "Must be admin to setup symlink folders."
                )
                folder = Folder().filter(Folder().save(folder), self.getCurrentUser())
                event.preventDefault().addResponse(folder)

    @staticmethod
    def _validateFolder(event):
        doc = event.info

        if isinstance(doc.get("_id"), str) and doc.get("_id").startswith("wtlocal:"):
            return

        if "isSymlink" in doc and not isinstance(doc["isSymlink"], bool):
            raise ValidationException("isSymlink must be a boolean.", field="isSymlink")

        if doc.get("isSymlink"):
            # Make sure it doesn't have children
            if list(Folder().childItems(doc, limit=1)):
                raise ValidationException(
                    "Symlink folders may not contain child items.", field="isSymlink"
                )
            if list(
                Folder().find(
                    {"parentId": doc["_id"], "parentCollection": "folder"}, limit=1
                )
            ):
                raise ValidationException(
                    "Symlink folders may not contain child folders.", field="isSymlink"
                )
        if doc["parentCollection"] == "folder":
            parent = Folder().load(event.info["parentId"], force=True, exc=True)
            if parent.get("isSymlink"):
                raise ValidationException(
                    "You may not place folders under a symlink folder.",
                    field="folderId",
                )

        if doc.get("symlinkTargetId") and not isinstance(
            doc["symlinkTargetId"], ObjectId
        ):
            raise ValidationException(
                "symlinkTargetId must be an ObjectId", field="symlinkTargetId"
            )

        if doc.get("symlinkTargetId"):
            if doc["_id"] == doc["symlinkTargetId"]:
                raise ValidationException(
                    "A folder may not symlink to itself.", field="symlinkTargetId"
                )
            try:
                Folder().load(doc["symlinkTargetId"], force=True, exc=True)
            except Exception:
                raise ValidationException(
                    "symlinkTargetId must reference a valid folder",
                    field="symlinkTargetId",
                )

    @access.public(scope=TokenScope.DATA_READ)
    def get_child_folders(self, event):
        params = event.info["params"]
        # Handle Symlink first
        parent_id = params.get("parentId")
        if parent_id and not parent_id.startswith("wtlocal:") and params.get("parentType") == "folder":
            parent = Folder().load(params["parentId"], force=True, exc=True)
            if parent.get("isSymlink") and parent.get("symlinkTargetId"):
                event.info["params"]["parentId"] = str(parent["symlinkTargetId"])
        self._get_child_folders(event)

    @access.public(scope=TokenScope.DATA_READ)
    @validate_event(level=AccessType.READ)
    def _get_child_folders(self, event, path, root, user=None):
        params = event.info["params"]
        name = params.get("name")
        offset = int(params.get("offset", 0))
        limit = int(params.get("limit", 50))
        sort_key = params.get("sort", "lowerName")
        reverse = int(params.get("sortdir", pymongo.ASCENDING)) == pymongo.DESCENDING

        # TODO: implement "text"
        if name:
            if (path / name).is_dir():
                folders = [self.vFolder(path / name, root)]
            else:
                folders = []
        else:
            folders = [
                self.vFolder(obj, root) for obj in path.iterdir() if obj.is_dir()
            ]

        folders = sorted(folders, key=itemgetter(sort_key), reverse=reverse)
        upper_bound = limit + offset if limit > 0 else None
        response = [
            Folder().filter(folder, user=user) for folder in folders[offset:upper_bound]
        ]
        event.preventDefault().addResponse(response)

    @access.user(scope=TokenScope.DATA_WRITE)
    @validate_event(level=AccessType.WRITE, validate_admin=True)
    def create_folder(self, event, path, root, user=None):
        params = event.info["params"]
        new_path = path / params["name"]
        try:
            new_path.mkdir()
        except FileExistsError:
            raise ValidationException(
                "A folder with that name already exists here.", "name"
            )
        event.preventDefault().addResponse(
            Folder().filter(self.vFolder(new_path, root), user=user)
        )

    @access.public(scope=TokenScope.DATA_READ)
    @validate_event(level=AccessType.READ)
    def get_folder_info(self, event, path, root, user=None):
        event.preventDefault().addResponse(
            Folder().filter(self.vFolder(path, root), user)
        )

    @access.user(scope=TokenScope.DATA_WRITE)
    @validate_event(level=AccessType.WRITE, validate_admin=True)
    def rename_folder(self, event, path, root, user=None):
        self.is_dir(path, root["_id"])
        source = self.vFolder(path, root)

        params = event.info.get("params", {})
        name = params.get("name", path.name)
        parentId = params.get("parentId", source["parentId"])

        if parentId == source["parentId"]:
            new_path = path.with_name(name)
            bail_if_exists(new_path)
            # Just rename in place
            path.rename(new_path)
        else:
            dst_path, dst_root_id = self.path_from_id(parentId)
            # Check whether the user can write to the destination
            Folder().load(dst_root_id, user=user, level=AccessType.WRITE, exc=True)
            new_path = dst_path / name
            bail_if_exists(new_path)
            shutil.move(
                path.as_posix(), new_path.as_posix(), copy_function=shutil.copytree
            )

        event.preventDefault().addResponse(
            Folder().filter(self.vFolder(new_path, root), user=user)
        )

    @access.user(scope=TokenScope.DATA_WRITE)
    @validate_event(level=AccessType.WRITE)
    def remove_folder(self, event, path, root, user=None):
        self.is_dir(path, root["_id"])
        shutil.rmtree(path.as_posix())
        event.preventDefault().addResponse(
            {"message": "Deleted folder %s." % path.name}
        )

    @access.user(scope=TokenScope.DATA_WRITE)
    @validate_event(level=AccessType.WRITE)
    def remove_folder_contents(self, event, path, root, user=None):
        self.is_dir(path, root["_id"])
        for sub_path in path.iterdir():
            if sub_path.is_file():
                sub_path.unlink()
            elif sub_path.is_dir():
                shutil.rmtree(sub_path.as_posix())
        event.preventDefault().addResponse(
            {"message": "Deleted contents of folder %s." % path.name}
        )

    @access.public(scope=TokenScope.DATA_READ)
    @validate_event(level=AccessType.READ)
    def copy_folder(self, event, path, root, user=None):
        self.is_dir(path, root["_id"])
        source = self.vFolder(path, root)

        if not str(source["_id"]).startswith("wtlocal:"):
            raise GirderException("Copying mappings is not allowed.")

        params = event.info.get("params", {})
        name = params.get("name", path.name)
        parentId = params.get("parentId", source["parentId"])

        dst_path, dst_root_id = self.path_from_id(parentId)
        dst_root = Folder().load(
            dst_root_id, user=user, level=AccessType.WRITE, exc=True
        )
        if "fsPath" not in dst_root:
            raise GirderException("Folder {} is not a mapping.".format(dst_root["_id"]))

        new_path = ensure_unique_path(dst_path, name)
        shutil.copytree(path.as_posix(), new_path.as_posix())
        event.preventDefault().addResponse(
            Folder().filter(self.vFolder(new_path, dst_root), user=user)
        )

    @access.public(scope=TokenScope.DATA_READ)
    @validate_event(level=AccessType.READ)
    def get_folder_details(self, event, path, root, user=None):
        self.is_dir(path, root["_id"])
        response = {"nFolders": 0, "nItems": 0}
        for obj in path.iterdir():
            if obj.is_dir():
                response["nFolders"] += 1
            elif obj.is_file():
                response["nItems"] += 1
        event.preventDefault().addResponse(response)

    @access.public(scope=TokenScope.DATA_READ)
    @validate_event(level=AccessType.READ)
    def download_folder(self, event, path, root, user=None):
        self.is_dir(path, root["_id"])
        setResponseHeader("Content-Type", "application/zip")
        setContentDisposition(path.name + ".zip")

        def stream():
            def recursive_file_list(p):
                for obj in p.iterdir():
                    if obj.is_file():
                        yield obj
                    elif obj.is_dir():
                        yield from recursive_file_list(obj)

            zip_stream = ziputil.ZipGenerator(rootPath="")
            for obj in recursive_file_list(path):
                zip_path = os.path.relpath(obj.as_posix(), path.as_posix())
                for data in zip_stream.addFile(lambda: file_stream(obj), zip_path):  # noqa
                    yield data
            yield zip_stream.footer()

        event.preventDefault().addResponse(stream)

    @access.public(scope=TokenScope.DATA_READ)
    @validate_event(level=AccessType.READ)
    def folder_root_path(self, event, path, root, user=None):
        root_path = pathlib.Path(root["fsPath"])
        response = []
        if root_path != path:
            response.append(
                {
                    "type": "folder",
                    "object": Folder().filter(self.vFolder(path, root), user=user),
                }
            )
            path = path.parent
            while path != root_path:
                response.append(
                    {
                        "type": "folder",
                        "object": Folder().filter(self.vFolder(path, root), user=user),
                    }
                )
                path = path.parent

        response.append({"type": "folder", "object": Folder().filter(root, user=user)})
        girder_rootpath = Folder().parentsToRoot(root, user=self.getCurrentUser())
        response += girder_rootpath[::-1]
        response.pop(0)
        event.preventDefault().addResponse(response[::-1])

    @access.user(scope=TokenScope.DATA_WRITE)
    @validate_event(level=AccessType.WRITE)
    def create_folder_recursive(self, event, path, root, user=None):
        self.is_dir(path, root["_id"])
        new_folder = path / event.info["params"]["path"]
        new_folder.mkdir(parents=True, exist_ok=True)
        event.preventDefault().addResponse(
            Folder().filter(self.vFolder(new_folder, root), user=user)
        )

    @access.public(scope=TokenScope.DATA_READ)
    @validate_event(level=AccessType.READ)
    def get_folder_readme(self, event, path, root, user=None):
        return ""
